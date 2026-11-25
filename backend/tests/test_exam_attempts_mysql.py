"""Test tranh chấp của lượt thi trên MySQL THẬT.

SQLite bỏ qua SELECT ... FOR UPDATE và khóa dòng, nên không chứng minh được gì về đồng thời. Các test này chạy
nhiều luồng, mỗi luồng một kết nối riêng, cùng bấm một lúc. Chạy bằng:
    SCHEDULE_MYSQL_TESTS=1 LMS_TEST_MYSQL_DATABASE=<tên DB có chữ test> pytest tests/test_exam_attempts_mysql.py
DB phải được `alembic upgrade head`.
"""

from __future__ import annotations

import os
import threading
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, delete, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums.user_role import UserRole
from app.models.exam import (
    Exam,
    ExamAnswerKey,
    ExamAttempt,
    ExamAttemptEvent,
    ExamGradeHistory,
    ExamLateSubmission,
    ExamPaper,
    ExamParticipant,
)
from app.models.user import User
from app.modules.exams.attempts import service as service_module
from app.modules.exams.attempts.repository import AttemptRepository
from app.modules.exams.attempts.service import AttemptService, Progress
from app.modules.exams.domain.errors import (
    AttemptClosed,
    EpochMismatch,
    NotAllowedToEnter,
    RequestIdReused,
    VersionConflict,
)

pytestmark = pytest.mark.skipif(
    os.getenv("SCHEDULE_MYSQL_TESTS") != "1", reason="cần MySQL đã chạy alembic upgrade head"
)

OPENS = datetime(2030, 1, 1, 8, 0)
CLOSES = datetime(2030, 1, 1, 10, 0)
KEY = {
    "q1": {"type": "multiple_choice", "correct": "B"},
    "q2": {"type": "true_false", "correct": {"a": True, "b": False, "c": True, "d": False}},
    "q3": {"type": "short_answer", "correct": "3,5"},
}
FULL_MARKS = {"q1": "B", "q2": {"a": True, "b": False, "c": True, "d": False}, "q3": "3,5"}  # 1.75 điểm


class Clock:
    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture(scope="module")
def engine():
    eng = create_engine(settings.database_url, pool_size=40, max_overflow=0)
    yield eng
    eng.dispose()


@pytest.fixture
def world(engine):
    """Giáo viên, 40 học sinh, một đề có khóa, một kỳ thi đã phát hành 08:00–10:00 (90 phút)."""
    tag = uuid.uuid4().hex[:8]
    ids: dict = {"students": []}
    with Session(engine) as db:
        def user(name: str, role: UserRole) -> int:
            u = User(full_name=name, phone_number=f"t{tag}{name}"[:30], hashed_password="x", role=role)
            db.add(u)
            db.flush()
            return u.id

        ids["teacher"] = user("gv", UserRole.TEACHER)
        ids["students"] = [user(f"hs{i}", UserRole.STUDENT) for i in range(40)]
        paper = ExamPaper(
            created_by=ids["teacher"], title="Đề thử", kind="structured", structure={}, structure_hash="0" * 64,
            status="locked", version=1, created_at=OPENS,
        )
        db.add(paper)
        db.flush()
        db.add(ExamAnswerKey(paper_id=paper.id, key=KEY, scoring={"multiple_choice": "0.25", "true_false": ["0", "0.1", "0.25", "0.5", "1"], "short_answer": "0.5"}, version=3))
        exam = Exam(
            paper_id=paper.id, created_by=ids["teacher"], title="Thi thử", opens_at=OPENS, closes_at=CLOSES,
            duration_minutes=90, status="published", version=1, created_at=OPENS,
        )
        db.add(exam)
        db.flush()
        for sid in ids["students"]:
            db.add(ExamParticipant(exam_id=exam.id, student_id=sid, added_via="student"))
        db.commit()
        ids["paper"], ids["exam"] = paper.id, exam.id

    yield ids

    with Session(engine) as db:
        exam_ids = [i for i in (ids["exam"], *ids.get("extra_exams", [])) if i]
        attempt_ids = db.scalars(select(ExamAttempt.id).where(ExamAttempt.exam_id.in_(exam_ids))).all()
        if attempt_ids:
            db.execute(delete(ExamGradeHistory).where(ExamGradeHistory.attempt_id.in_(attempt_ids)))
            db.execute(delete(ExamAttemptEvent).where(ExamAttemptEvent.attempt_id.in_(attempt_ids)))
            db.execute(delete(ExamLateSubmission).where(ExamLateSubmission.attempt_id.in_(attempt_ids)))
            db.execute(delete(ExamAttempt).where(ExamAttempt.id.in_(attempt_ids)))
        db.execute(delete(ExamParticipant).where(ExamParticipant.exam_id.in_(exam_ids)))
        db.execute(delete(Exam).where(Exam.id.in_(exam_ids)))
        paper_ids = [ids["paper"], *ids.get("extra_papers", [])]
        db.execute(delete(ExamAnswerKey).where(ExamAnswerKey.paper_id.in_(paper_ids)))
        db.execute(delete(ExamPaper).where(ExamPaper.id.in_(paper_ids)))
        db.execute(delete(User).where(User.id.in_([ids["teacher"], *ids["students"]])))
        db.commit()


# ----- trợ giúp -----
def service_for(db: Session, clock: Clock) -> AttemptService:
    return AttemptService(AttemptRepository(db), now_fn=clock)


def run_parallel(engine, clock: Clock, count: int, fn):
    """Chạy `fn(service, i)` ở `count` luồng, mỗi luồng một kết nối, cùng xuất phát nhờ Barrier."""
    barrier = threading.Barrier(count)
    results: list = [None] * count

    def worker(i: int) -> None:
        with Session(engine) as db:
            svc = service_for(db, clock)
            barrier.wait(timeout=30)
            try:
                results[i] = ("ok", fn(svc, i))
            except Exception as exc:  # noqa: BLE001 - test cần xem mọi loại lỗi
                results[i] = ("err", exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert all(r is not None for r in results), "có luồng không kết thúc"
    return results


def oks(results):
    return [r[1] for r in results if r[0] == "ok"]


def errs(results):
    return [r[1] for r in results if r[0] == "err"]


def start_attempt(engine, world, clock, index=0, device="dev-1"):
    with Session(engine) as db:
        return service_for(db, clock).start(world["exam"], world["students"][index], device)


def count(engine, model, *conds):
    with Session(engine) as db:
        return db.scalar(select(func.count()).select_from(model).where(*conds))


def fetch(engine, attempt_id):
    with Session(engine) as db:
        return db.get(ExamAttempt, attempt_id)


# ----- rowcount -----
def test_update_with_unchanged_values_still_reports_matched_row(engine, world):
    """Thiết kế dựa vào rowcount = số dòng KHỚP điều kiện (CLIENT_FOUND_ROWS). Nếu tắt cờ này, ghi trùng nội
    dung sẽ báo 0 dòng và bị nhầm là xung đột phiên bản."""
    view = start_attempt(engine, world, Clock(OPENS))
    with Session(engine) as db:
        result = db.execute(text("UPDATE exam_attempts SET device_id = device_id WHERE id = :id"), {"id": view.id})
        assert result.rowcount == 1


# ----- bắt đầu -----
def test_many_simultaneous_starts_create_one_attempt(engine, world):
    clock = Clock(OPENS + timedelta(minutes=5))
    results = run_parallel(engine, clock, 20, lambda svc, i: svc.start(world["exam"], world["students"][0], f"dev-{i}"))
    assert not errs(results)
    views = oks(results)
    assert len({v.id for v in views}) == 1
    assert len({v.shuffle_seed for v in views}) == 1  # hạt giống chốt một lần
    assert len({v.deadline_at for v in views}) == 1
    assert count(engine, ExamAttempt, ExamAttempt.student_id == world["students"][0]) == 1


def test_deadline_rules_at_entry(engine, world):
    on_time = start_attempt(engine, world, Clock(OPENS), index=1)
    late = start_attempt(engine, world, Clock(datetime(2030, 1, 1, 8, 45)), index=2)
    assert on_time.deadline_at == datetime(2030, 1, 1, 9, 30)
    assert late.deadline_at == CLOSES  # vào muộn không được thêm giờ


def test_entry_is_refused_outside_window_or_without_name_or_unpublished(engine, world):
    with Session(engine) as db:
        with pytest.raises(NotAllowedToEnter):
            service_for(db, Clock(OPENS - timedelta(seconds=1))).start(world["exam"], world["students"][3], "d")
        with pytest.raises(NotAllowedToEnter):
            service_for(db, Clock(CLOSES)).start(world["exam"], world["students"][3], "d")
        with pytest.raises(NotAllowedToEnter):
            service_for(db, Clock(OPENS)).start(world["exam"], world["teacher"], "d")  # không có tên
    with Session(engine) as db:
        db.execute(text("UPDATE exams SET status = 'draft' WHERE id = :i"), {"i": world["exam"]})
        db.commit()
        with pytest.raises(NotAllowedToEnter):
            service_for(db, Clock(OPENS)).start(world["exam"], world["students"][3], "d")


def test_existing_attempt_can_resume_after_window_closes(engine, world):
    view = start_attempt(engine, world, Clock(OPENS), index=4)
    resumed = start_attempt(engine, world, Clock(CLOSES + timedelta(minutes=1)), index=4)
    assert resumed.id == view.id


def test_second_device_must_confirm_takeover_while_first_is_alive(engine, world):
    view = start_attempt(engine, world, Clock(OPENS), index=5, device="may-a")
    near = start_attempt(engine, world, Clock(OPENS + timedelta(seconds=30)), index=5, device="may-b")
    far = start_attempt(engine, world, Clock(OPENS + timedelta(seconds=300)), index=5, device="may-b")
    assert near.takeover_required is True
    assert far.takeover_required is False
    assert near.id == far.id == view.id


# ----- lưu bài -----
def test_save_increments_version_and_progress_counters_never_go_back(engine, world):
    clock = Clock(OPENS + timedelta(minutes=1))
    view = start_attempt(engine, world, clock, index=6)
    sid = world["students"][6]
    with Session(engine) as db:
        svc = service_for(db, clock)
        v1 = svc.sync(view.id, sid, epoch=1, base_version=0, answers={"q1": "A"},
                      progress=Progress(current_item="q2", item_ms={"q1": 5000}, away_count=3, away_ms=9000, offline_count=1))
        v2 = svc.sync(view.id, sid, epoch=1, base_version=v1, answers={"q1": "B"},
                      progress=Progress(current_item="q3", away_count=1, away_ms=100, offline_count=0))  # số nhỏ hơn
    assert (v1, v2) == (1, 2)
    row = fetch(engine, view.id)
    assert row.answers == {"q1": "B"}
    assert row.current_item == "q3"
    assert (row.away_count, row.away_ms, row.offline_count) == (3, 9000, 1)  # GREATEST: không lùi


def test_racing_saves_with_same_base_version_exactly_one_wins(engine, world):
    clock = Clock(OPENS + timedelta(minutes=1))
    view = start_attempt(engine, world, clock, index=7)
    sid = world["students"][7]
    results = run_parallel(
        engine, clock, 8, lambda svc, i: svc.sync(view.id, sid, epoch=1, base_version=0, answers={"q1": f"x{i}"})
    )
    assert len(oks(results)) == 1
    assert all(isinstance(e, VersionConflict) for e in errs(results))
    row = fetch(engine, view.id)
    assert row.answers_version == 1
    assert row.answers == {"q1": f"x{[r[0] for r in results].index('ok')}"}


def test_retry_after_lost_response_is_success_but_different_content_conflicts(engine, world):
    clock = Clock(OPENS + timedelta(minutes=1))
    view = start_attempt(engine, world, clock, index=8)
    sid = world["students"][8]
    with Session(engine) as db:
        svc = service_for(db, clock)
        assert svc.sync(view.id, sid, epoch=1, base_version=0, answers={"q1": "A"}) == 1
        assert svc.sync(view.id, sid, epoch=1, base_version=0, answers={"q1": "A"}) == 1  # phản hồi trước bị mất
        with pytest.raises(VersionConflict) as exc:
            svc.sync(view.id, sid, epoch=1, base_version=0, answers={"q1": "C"})
        assert exc.value.server_answers == {"q1": "A"}
        assert exc.value.server_version == 1


def test_old_device_is_rejected_after_takeover(engine, world):
    clock = Clock(OPENS + timedelta(minutes=1))
    view = start_attempt(engine, world, clock, index=9, device="may-a")
    sid = world["students"][9]
    with Session(engine) as db:
        svc = service_for(db, clock)
        taken = svc.take_over(view.id, sid, "may-b")
        assert taken.write_epoch == 2
        with pytest.raises(EpochMismatch):
            svc.sync(view.id, sid, epoch=1, base_version=0, answers={"q1": "A"})
        with pytest.raises(EpochMismatch):
            svc.submit(view.id, sid, epoch=1, answers={"q1": "A"}, request_id="r1")
        assert svc.sync(view.id, sid, epoch=2, base_version=0, answers={"q1": "B"}) == 1


def test_saving_at_grace_boundary(engine, world):
    view = start_attempt(engine, world, Clock(OPENS), index=10)  # hạn 09:30
    sid = world["students"][10]
    deadline = view.deadline_at
    with Session(engine) as db:
        assert service_for(db, Clock(deadline + timedelta(seconds=30))).sync(
            view.id, sid, epoch=1, base_version=0, answers={"q1": "A"}) == 1
        with pytest.raises(AttemptClosed):
            service_for(db, Clock(deadline + timedelta(seconds=31))).sync(
                view.id, sid, epoch=1, base_version=1, answers={"q1": "B"})


def test_deactivated_account_cannot_save(engine, world):
    clock = Clock(OPENS + timedelta(minutes=1))
    view = start_attempt(engine, world, clock, index=11)
    sid = world["students"][11]
    with Session(engine) as db:
        db.execute(text("UPDATE users SET is_active = 0 WHERE id = :i"), {"i": sid})
        db.commit()
        with pytest.raises(NotAllowedToEnter):
            service_for(db, clock).sync(view.id, sid, epoch=1, base_version=0, answers={"q1": "A"})
    assert fetch(engine, view.id).answers == {}


def test_student_cannot_write_someone_elses_attempt(engine, world):
    clock = Clock(OPENS + timedelta(minutes=1))
    view = start_attempt(engine, world, clock, index=12)
    with Session(engine) as db:
        with pytest.raises(NotAllowedToEnter):
            service_for(db, clock).sync(view.id, world["students"][13], epoch=1, base_version=0, answers={"q1": "A"})
        with pytest.raises(NotAllowedToEnter):
            service_for(db, clock).submit(view.id, world["students"][13], epoch=1, answers={}, request_id="x")
    assert fetch(engine, view.id).answers == {}


# ----- nộp bài -----
def test_submit_grades_and_returns_receipt(engine, world):
    clock = Clock(OPENS + timedelta(minutes=30))
    view = start_attempt(engine, world, clock, index=14)
    sid = world["students"][14]
    with Session(engine) as db:
        result = service_for(db, clock).submit(view.id, sid, epoch=1, answers=FULL_MARKS, request_id="r1")
    assert result.status == "submitted" and not result.late and not result.replayed
    assert result.score == result.max_score == Decimal("1.75")
    row = fetch(engine, view.id)
    assert row.status == "submitted" and row.receipt_code == result.receipt_code and len(row.receipt_code) == 10
    assert row.content_digest == result.content_digest
    assert row.answers == FULL_MARKS
    with Session(engine) as db:
        history = db.scalars(select(ExamGradeHistory).where(ExamGradeHistory.attempt_id == view.id)).all()
        assert [(h.answer_key_version, h.score, h.reason) for h in history] == [(3, Decimal("1.75"), "submit")]


def test_double_clicking_submit_is_safe_under_concurrency(engine, world):
    clock = Clock(OPENS + timedelta(minutes=30))
    view = start_attempt(engine, world, clock, index=15)
    sid = world["students"][15]
    results = run_parallel(
        engine, clock, 12, lambda svc, i: svc.submit(view.id, sid, epoch=1, answers=FULL_MARKS, request_id="same-id")
    )
    assert not errs(results)
    receipts = {r.receipt_code for r in oks(results)}
    assert len(receipts) == 1  # mọi bản gửi nhận đúng một biên nhận
    assert sum(1 for r in oks(results) if not r.replayed) == 1  # chỉ một bản thật sự chấm
    assert count(engine, ExamGradeHistory, ExamGradeHistory.attempt_id == view.id) == 1


def test_competing_submits_with_different_request_ids_keep_the_first(engine, world):
    clock = Clock(OPENS + timedelta(minutes=30))
    view = start_attempt(engine, world, clock, index=16)
    sid = world["students"][16]
    results = run_parallel(
        engine, clock, 6, lambda svc, i: svc.submit(view.id, sid, epoch=1, answers={"q1": "B", "q3": f"v{i}"}, request_id=f"rid-{i}")
    )
    winners = oks(results)
    assert len(winners) == 1
    assert all(isinstance(e, AttemptClosed) and e.receipt_code == winners[0].receipt_code for e in errs(results))
    assert count(engine, ExamGradeHistory, ExamGradeHistory.attempt_id == view.id) == 1


def test_same_request_id_with_different_answers_is_rejected(engine, world):
    clock = Clock(OPENS + timedelta(minutes=30))
    view = start_attempt(engine, world, clock, index=17)
    sid = world["students"][17]
    with Session(engine) as db:
        svc = service_for(db, clock)
        svc.submit(view.id, sid, epoch=1, answers=FULL_MARKS, request_id="r1")
        with pytest.raises(RequestIdReused):
            svc.submit(view.id, sid, epoch=1, answers={"q1": "A"}, request_id="r1")


def test_nothing_can_be_written_after_submit(engine, world):
    clock = Clock(OPENS + timedelta(minutes=30))
    view = start_attempt(engine, world, clock, index=18)
    sid = world["students"][18]
    with Session(engine) as db:
        svc = service_for(db, clock)
        receipt = svc.submit(view.id, sid, epoch=1, answers=FULL_MARKS, request_id="r1").receipt_code
        with pytest.raises(AttemptClosed) as exc:
            svc.sync(view.id, sid, epoch=1, base_version=1, answers={"q1": "A"})
        assert exc.value.receipt_code == receipt
    assert fetch(engine, view.id).answers == FULL_MARKS


def test_sync_racing_with_submit_never_corrupts_the_submitted_answers(engine, world):
    clock = Clock(OPENS + timedelta(minutes=30))
    view = start_attempt(engine, world, clock, index=19)
    sid = world["students"][19]

    def work(svc, i):
        if i == 0:
            return svc.submit(view.id, sid, epoch=1, answers=FULL_MARKS, request_id="r1")
        return svc.sync(view.id, sid, epoch=1, base_version=0, answers={"q1": f"nhieu{i}"})

    results = run_parallel(engine, clock, 8, work)
    row = fetch(engine, view.id)
    assert row.status == "submitted"
    unexpected = [e for e in errs(results) if not isinstance(e, (AttemptClosed, VersionConflict))]
    assert not unexpected, unexpected
    # Bài đã nộp phải khớp biên nhận: không lần lưu nào đến sau được chen vào.
    assert row.content_digest == service_module.content_digest(row.answers)
    assert count(engine, ExamGradeHistory, ExamGradeHistory.attempt_id == view.id) == 1


def test_submit_after_grace_keeps_last_synced_answers_and_records_late_part(engine, world):
    early = Clock(OPENS + timedelta(minutes=10))
    view = start_attempt(engine, world, early, index=20)
    sid = world["students"][20]
    with Session(engine) as db:
        service_for(db, early).sync(view.id, sid, epoch=1, base_version=0, answers={"q1": "B"})
        too_late = Clock(view.deadline_at + timedelta(minutes=5))
        result = service_for(db, too_late).submit(view.id, sid, epoch=1, answers=FULL_MARKS, request_id="r1")
    assert result.late and result.status == "auto_submitted"
    assert result.score == Decimal("0.25")  # chỉ phần đã đồng bộ (q1 đúng)
    assert fetch(engine, view.id).answers == {"q1": "B"}
    with Session(engine) as db:
        late = db.scalars(select(ExamLateSubmission).where(ExamLateSubmission.attempt_id == view.id)).all()
        assert [(x.answers, x.decision) for x in late] == [(FULL_MARKS, "pending")]


def test_grading_failure_never_loses_the_saved_answers(engine, world):
    """Kỳ thi thiếu khóa đáp án: nộp báo lỗi, nhưng lượt vẫn đang làm và đáp án vẫn còn để chấm lại sau."""
    with Session(engine) as db:
        paper = ExamPaper(created_by=world["teacher"], title="Không khóa", kind="structured", structure={},
                          structure_hash="0" * 64, status="locked", version=1, created_at=OPENS)
        db.add(paper)
        db.flush()
        exam = Exam(paper_id=paper.id, created_by=world["teacher"], title="Thiếu khóa", opens_at=OPENS, closes_at=CLOSES,
                    duration_minutes=90, status="published", version=1, created_at=OPENS)
        db.add(exam)
        db.flush()
        db.add(ExamParticipant(exam_id=exam.id, student_id=world["students"][21], added_via="student"))
        db.commit()
        world.setdefault("extra_papers", []).append(paper.id)
        world.setdefault("extra_exams", []).append(exam.id)
        clock = Clock(OPENS + timedelta(minutes=5))
        svc = service_for(db, clock)
        view = svc.start(exam.id, world["students"][21], "d")
        svc.sync(view.id, world["students"][21], epoch=1, base_version=0, answers={"q1": "B"})
        with pytest.raises(RuntimeError):
            svc.submit(view.id, world["students"][21], epoch=1, answers=FULL_MARKS, request_id="r1")
    row = fetch(engine, view.id)
    assert row.status == "in_progress"
    assert row.answers == {"q1": "B"}
    assert count(engine, ExamGradeHistory, ExamGradeHistory.attempt_id == view.id) == 0


def test_receipt_code_collision_is_retried_with_a_new_code(engine, world, monkeypatch):
    clock = Clock(OPENS + timedelta(minutes=30))
    first = start_attempt(engine, world, clock, index=22)
    second = start_attempt(engine, world, clock, index=23)
    with Session(engine) as db:
        taken = service_for(db, clock).submit(first.id, world["students"][22], epoch=1, answers=FULL_MARKS, request_id="a").receipt_code
    codes = iter([taken, taken, "ZZZZZZZZZZ"])
    monkeypatch.setattr(service_module, "new_receipt_code", lambda: next(codes))
    with Session(engine) as db:
        result = service_for(db, clock).submit(second.id, world["students"][23], epoch=1, answers=FULL_MARKS, request_id="b")
    assert result.receipt_code == "ZZZZZZZZZZ"
    assert count(engine, ExamGradeHistory, ExamGradeHistory.attempt_id == second.id) == 1


# ----- quét chốt -----
def make_expired(engine, world, indexes, answers_by_index=None):
    """Tạo lượt đã quá hạn (đã qua cả ân hạn) cho các học sinh."""
    views = []
    for i in indexes:
        views.append(start_attempt(engine, world, Clock(OPENS), index=i))
        if answers_by_index and i in answers_by_index:
            with Session(engine) as db:
                service_for(db, Clock(OPENS + timedelta(minutes=1))).sync(
                    views[-1].id, world["students"][i], epoch=1, base_version=0, answers=answers_by_index[i])
    return views


def test_sweep_finalizes_only_expired_attempts_and_is_idempotent(engine, world):
    expired = make_expired(engine, world, [24, 25], {24: FULL_MARKS})
    alive = start_attempt(engine, world, Clock(datetime(2030, 1, 1, 9, 29)), index=26)  # hạn 10:00
    after = Clock(datetime(2030, 1, 1, 9, 31))  # đã quá hạn của hai lượt vào lúc 08:00 (hạn 09:30) cộng ân hạn
    with Session(engine) as db:
        assert service_for(db, after).sweep() == 2
        assert service_for(db, after).sweep() == 0  # chạy lại vô hại
    a, b = (fetch(engine, v.id) for v in expired)
    assert (a.status, b.status) == ("auto_submitted", "auto_submitted")
    assert a.score == Decimal("1.75") and b.score == Decimal("0.00")  # bài trống vẫn được chốt, 0 điểm
    assert a.submit_request_id is None and a.receipt_code
    assert fetch(engine, alive.id).status == "in_progress"
    assert count(engine, ExamGradeHistory, ExamGradeHistory.attempt_id.in_([v.id for v in expired])) == 2


def test_two_sweepers_in_parallel_never_double_grade(engine, world):
    views = make_expired(engine, world, list(range(0, 40)), {i: FULL_MARKS for i in range(0, 40, 2)})
    after = Clock(datetime(2030, 1, 1, 9, 45))
    results = run_parallel(engine, after, 4, lambda svc, i: svc.sweep(batch_size=7))
    assert not errs(results), errs(results)
    ids = [v.id for v in views]
    assert sum(oks(results)) == 40  # mỗi lượt được đúng một người quét chốt
    assert count(engine, ExamGradeHistory, ExamGradeHistory.attempt_id.in_(ids)) == 40
    assert count(engine, ExamAttempt, ExamAttempt.id.in_(ids), ExamAttempt.status == "auto_submitted") == 40


def test_sweeper_racing_with_a_late_submit_grades_each_attempt_once(engine, world):
    views = make_expired(engine, world, [27, 28, 29, 30], {27: FULL_MARKS})
    after = Clock(datetime(2030, 1, 1, 9, 45))
    sids = {v.id: world["students"][i] for v, i in zip(views, [27, 28, 29, 30])}

    def work(svc, i):
        if i < 4:
            v = views[i]
            return svc.submit(v.id, sids[v.id], epoch=1, answers=FULL_MARKS, request_id=f"r{i}")
        return svc.sweep(batch_size=2)

    results = run_parallel(engine, after, 7, work)
    unexpected = [e for e in errs(results) if not isinstance(e, AttemptClosed)]
    assert not unexpected, unexpected
    for v in views:
        assert count(engine, ExamGradeHistory, ExamGradeHistory.attempt_id == v.id) == 1
        assert fetch(engine, v.id).status == "auto_submitted"


# ----- lượt thi thêm -----
def test_extra_attempt_granted_by_teacher_becomes_the_current_one(engine, world):
    first = start_attempt(engine, world, Clock(OPENS), index=31)
    sid = world["students"][31]
    with Session(engine) as db:
        db.add(ExamAttempt(exam_id=world["exam"], student_id=sid, attempt_no=2, started_at=OPENS, deadline_at=CLOSES,
                           status="in_progress", answers={}, answers_version=0, write_epoch=1,
                           granted_by=world["teacher"], grant_reason="Mất điện giữa giờ"))
        db.commit()
    resumed = start_attempt(engine, world, Clock(OPENS + timedelta(minutes=1)), index=31)
    assert resumed.id != first.id  # lượt có attempt_no lớn nhất là lượt hiện hành
    with Session(engine) as db:
        db.add(ExamAttempt(exam_id=world["exam"], student_id=sid, attempt_no=2, started_at=OPENS, deadline_at=CLOSES,
                           status="in_progress", answers={}, answers_version=0, write_epoch=1))
        with pytest.raises(IntegrityError):
            db.commit()  # trùng (kỳ thi, học sinh, số lượt): cô bấm "mở lượt mới" hai lần cũng chỉ ra một lượt


# ----- bổ sung sau khi phá cố ý cơ chế bảo vệ -----
def test_insert_of_first_attempt_is_idempotent_even_when_every_thread_inserts(engine, world):
    """Gọi thẳng câu INSERT từ nhiều luồng (bỏ qua bước tra cứu trước của start) để ép tranh chấp thật sự xảy ra:
    ON DUPLICATE KEY UPDATE id = id phải khiến các lần chèn thừa không lỗi và không tạo thêm dòng."""
    sid = world["students"][32]

    def insert(svc, i):
        svc.repo.create_first_attempt_if_absent(
            exam_id=world["exam"], student_id=sid, now=OPENS, deadline_at=CLOSES,
            device_id=f"d{i}", shuffle_seed=1000 + i,
        )
        svc.db.commit()
        return i

    results = run_parallel(engine, Clock(OPENS), 30, insert)
    assert not errs(results), errs(results)
    assert count(engine, ExamAttempt, ExamAttempt.student_id == sid) == 1
    row = fetch(engine, _only_attempt_id(engine, world["exam"], sid))
    assert row.write_epoch == 1 and row.answers_version == 0  # lần chèn thừa không làm đổi gì


def _only_attempt_id(engine, exam_id, student_id):
    with Session(engine) as db:
        return db.scalar(select(ExamAttempt.id).where(ExamAttempt.exam_id == exam_id, ExamAttempt.student_id == student_id))


def test_finalize_refuses_an_attempt_that_is_no_longer_in_progress(engine, world):
    """Lớp bảo vệ thứ hai ngoài khóa dòng: UPDATE chốt chỉ chạy được khi lượt còn đang làm."""
    clock = Clock(OPENS + timedelta(minutes=30))
    view = start_attempt(engine, world, clock, index=33)
    with Session(engine) as db:
        service_for(db, clock).submit(view.id, world["students"][33], epoch=1, answers=FULL_MARKS, request_id="r1")
    with Session(engine) as db:
        repo = AttemptRepository(db)
        with pytest.raises(RuntimeError):
            repo.finalize(
                attempt_id=view.id, status="submitted", answers={"q1": "A"}, now=clock.now, request_id="r2",
                receipt_code="ABCDEFGHJK", digest="0" * 64, score=Decimal("0"), max_score=Decimal("1"),
            )
        db.rollback()
    assert fetch(engine, view.id).answers == FULL_MARKS
