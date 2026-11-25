"""Test phần giáo viên theo dõi và điều khiển phòng thi, cùng ghi sự kiện, trên MySQL thật.

Dùng lại fixture `engine`, `world` của test_exam_attempts_mysql (kỳ thi 08:00–10:00, 90 phút, 40 học sinh).
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from test_exam_attempts_mysql import (  # noqa: F401  (fixture phải được import vào module này)
    CLOSES,
    FULL_MARKS,
    OPENS,
    Clock,
    count,
    engine,
    errs,
    fetch,
    oks,
    pytestmark,
    run_parallel,
    service_for,
    start_attempt,
    world,
)

from app.models.exam import ExamAttempt, ExamAttemptEvent, ExamGradeHistory
from app.modules.exams.attempts.repository import AttemptRepository
from app.modules.exams.attempts.service import AttemptService, Progress
from app.modules.exams.domain.errors import AttemptClosed, EpochMismatch, InvalidTeacherAction, NotAllowedToEnter
from app.modules.exams.monitor.repository import MonitorRepository
from app.modules.exams.monitor.service import MonitorService, TeacherControlService

TEACHER_REASON = "Mất điện giữa giờ"


def teacher_service(db: Session, clock: Clock) -> TeacherControlService:
    return TeacherControlService(AttemptService(AttemptRepository(db), now_fn=clock))


def events_of(engine, attempt_id: int) -> list[ExamAttemptEvent]:
    with Session(engine) as db:
        return list(db.scalars(select(ExamAttemptEvent).where(ExamAttemptEvent.attempt_id == attempt_id).order_by(ExamAttemptEvent.id)))


# ----- theo dõi -----
def test_overview_classifies_every_participant(engine, world):
    early = Clock(OPENS + timedelta(minutes=1))
    now = Clock(OPENS + timedelta(minutes=3))
    sids = world["students"]
    # 1: đang làm (vừa báo tín hiệu), 2: mất kết nối (báo lần cuối cách 2 phút), 3: đã nộp, 4: bị tự chốt
    v = {i: start_attempt(engine, world, early, index=i) for i in (1, 2, 3, 4)}
    with Session(engine) as db:
        service_for(db, now).sync(v[1].id, sids[1], epoch=1, base_version=0, answers={"q1": "A", "q2": {"a": True}, "q3": ""},
                                  progress=Progress(current_item="q2", away_count=2, away_ms=7000, fullscreen_exit_count=1, offline_count=3))
        service_for(db, early).sync(v[2].id, sids[2], epoch=1, base_version=0, answers={"q1": "B"})
        service_for(db, now).submit(v[3].id, sids[3], epoch=1, answers=FULL_MARKS, request_id="r3")
        teacher_service(db, now).force_submit(v[4].id, teacher_id=world["teacher"], reason="Kết thúc sớm")

    with Session(engine) as db:
        overview = MonitorService(MonitorRepository(db), now_fn=now).overview(world["exam"])
    by_id = {s.student_id: s for s in overview.students}
    assert by_id[sids[0]].state == "not_started" and by_id[sids[0]].attempt_id is None
    assert by_id[sids[1]].state == "in_progress"
    assert by_id[sids[2]].state == "disconnected"
    assert by_id[sids[3]].state == "submitted"
    assert by_id[sids[4]].state == "auto_submitted"
    assert overview.totals["total"] == 40
    assert overview.totals["not_started"] == 36
    one = by_id[sids[1]]
    assert (one.current_item, one.away_count, one.away_ms, one.fullscreen_exit_count, one.offline_count) == ("q2", 2, 7000, 1, 3)
    assert one.answered == 3  # JSON_LENGTH đếm số khóa đã lưu
    assert by_id[sids[3]].score == Decimal("1.75")


def test_overview_shows_only_the_current_attempt_of_each_student(engine, world):
    clock = Clock(OPENS + timedelta(minutes=5))
    sid = world["students"][5]
    first = start_attempt(engine, world, clock, index=5)
    with Session(engine) as db:
        service_for(db, clock).submit(first.id, sid, epoch=1, answers=FULL_MARKS, request_id="r1")
        new_id = teacher_service(db, clock).open_extra_attempt(world["exam"], sid, teacher_id=world["teacher"], reason=TEACHER_REASON)
        overview = MonitorService(MonitorRepository(db), now_fn=clock).overview(world["exam"])
    row = next(s for s in overview.students if s.student_id == sid)
    assert (row.attempt_id, row.attempt_no, row.extra_attempt_reason) == (new_id, 2, TEACHER_REASON)
    assert overview.totals["total"] == 40  # không nhân đôi dòng của em có hai lượt


# ----- gia hạn -----
def test_extend_one_attempt_moves_deadline_and_writes_audit_log(engine, world):
    clock = Clock(OPENS + timedelta(minutes=10))
    view = start_attempt(engine, world, clock, index=6)
    with Session(engine) as db:
        new_deadline = teacher_service(db, clock).extend_attempt(view.id, minutes=15, teacher_id=world["teacher"], reason=TEACHER_REASON)
    assert new_deadline == view.deadline_at + timedelta(minutes=15)
    assert fetch(engine, view.id).deadline_at == new_deadline
    log = [e for e in events_of(engine, view.id) if e.type == "teacher_extend"]
    assert len(log) == 1
    assert log[0].payload["teacher_id"] == world["teacher"] and log[0].payload["reason"] == TEACHER_REASON


def test_extension_lets_the_student_keep_saving_past_the_old_deadline(engine, world):
    view = start_attempt(engine, world, Clock(OPENS), index=7)  # hạn 09:30
    sid = world["students"][7]
    with Session(engine) as db:
        teacher_service(db, Clock(OPENS)).extend_attempt(view.id, minutes=20, teacher_id=world["teacher"], reason=TEACHER_REASON)
        past_old_deadline = Clock(view.deadline_at + timedelta(minutes=10))
        assert service_for(db, past_old_deadline).sync(view.id, sid, epoch=1, base_version=0, answers={"q1": "A"}) == 1


@pytest.mark.parametrize("minutes", [0, -5, 241, 1.5, True, None])
def test_extension_minutes_are_bounded(engine, world, minutes):
    view = start_attempt(engine, world, Clock(OPENS), index=8)
    with Session(engine) as db:
        with pytest.raises(InvalidTeacherAction):
            teacher_service(db, Clock(OPENS)).extend_attempt(view.id, minutes=minutes, teacher_id=world["teacher"], reason=TEACHER_REASON)
    assert fetch(engine, view.id).deadline_at == view.deadline_at


@pytest.mark.parametrize("reason", ["", "   ", None])
def test_every_teacher_action_requires_a_reason(engine, world, reason):
    view = start_attempt(engine, world, Clock(OPENS), index=9)
    with Session(engine) as db:
        svc = teacher_service(db, Clock(OPENS))
        with pytest.raises(InvalidTeacherAction):
            svc.extend_attempt(view.id, minutes=5, teacher_id=world["teacher"], reason=reason)
        with pytest.raises(InvalidTeacherAction):
            svc.force_submit(view.id, teacher_id=world["teacher"], reason=reason)
        with pytest.raises(InvalidTeacherAction):
            svc.extend_exam(world["exam"], minutes=5, teacher_id=world["teacher"], reason=reason)
    assert fetch(engine, view.id).status == "in_progress"
    assert events_of(engine, view.id) == []


def test_cannot_extend_a_submitted_attempt(engine, world):
    clock = Clock(OPENS + timedelta(minutes=5))
    view = start_attempt(engine, world, clock, index=10)
    with Session(engine) as db:
        service_for(db, clock).submit(view.id, world["students"][10], epoch=1, answers=FULL_MARKS, request_id="r1")
        with pytest.raises(InvalidTeacherAction):
            teacher_service(db, clock).extend_attempt(view.id, minutes=5, teacher_id=world["teacher"], reason=TEACHER_REASON)


def test_extend_whole_exam_moves_close_time_and_every_running_attempt(engine, world):
    clock = Clock(OPENS + timedelta(minutes=10))
    running = [start_attempt(engine, world, clock, index=i) for i in (11, 12, 13)]
    done = start_attempt(engine, world, clock, index=14)
    with Session(engine) as db:
        service_for(db, clock).submit(done.id, world["students"][14], epoch=1, answers=FULL_MARKS, request_id="r1")
        touched = teacher_service(db, clock).extend_exam(world["exam"], minutes=10, teacher_id=world["teacher"], reason=TEACHER_REASON)
    assert touched == 3
    for v in running:
        assert fetch(engine, v.id).deadline_at == v.deadline_at + timedelta(minutes=10)
        assert any(e.type == "teacher_extend_exam" for e in events_of(engine, v.id))
    assert fetch(engine, done.id).deadline_at == done.deadline_at  # em đã nộp không bị đổi
    # em vào muộn sau giờ đóng cũ vẫn vào được nhờ giờ đóng mới
    after_old_close = Clock(CLOSES + timedelta(minutes=5))
    late = start_attempt(engine, world, after_old_close, index=15)
    assert late.deadline_at == CLOSES + timedelta(minutes=10)


# ----- buộc nộp -----
def test_force_submit_grades_saved_answers_and_locks_the_attempt(engine, world):
    clock = Clock(OPENS + timedelta(minutes=20))
    view = start_attempt(engine, world, clock, index=16)
    sid = world["students"][16]
    with Session(engine) as db:
        service_for(db, clock).sync(view.id, sid, epoch=1, base_version=0, answers={"q1": "B"})
        result = teacher_service(db, clock).force_submit(view.id, teacher_id=world["teacher"], reason="Kết thúc sớm")
        with pytest.raises(AttemptClosed) as closed:
            service_for(db, clock).sync(view.id, sid, epoch=1, base_version=1, answers={"q1": "A"})
        with pytest.raises(AttemptClosed):
            teacher_service(db, clock).force_submit(view.id, teacher_id=world["teacher"], reason="lần hai")
    assert result.status == "auto_submitted" and result.score == Decimal("0.25")
    assert closed.value.receipt_code == result.receipt_code
    row = fetch(engine, view.id)
    assert row.answers == {"q1": "B"} and row.status == "auto_submitted"
    assert count(engine, ExamGradeHistory, ExamGradeHistory.attempt_id == view.id) == 1
    assert [e.payload["receipt"] for e in events_of(engine, view.id) if e.type == "teacher_force_submit"] == [result.receipt_code]


def test_force_submit_racing_with_the_students_own_submit_grades_once(engine, world):
    clock = Clock(OPENS + timedelta(minutes=20))
    view = start_attempt(engine, world, clock, index=17)
    sid = world["students"][17]

    def work(svc, i):
        if i == 0:
            return svc.submit(view.id, sid, epoch=1, answers=FULL_MARKS, request_id="r1")
        return TeacherControlService(svc).force_submit(view.id, teacher_id=world["teacher"], reason="cùng lúc")

    results = run_parallel(engine, clock, 4, work)
    assert all(isinstance(e, AttemptClosed) for e in errs(results))
    assert len(oks(results)) >= 1
    assert count(engine, ExamGradeHistory, ExamGradeHistory.attempt_id == view.id) == 1
    assert fetch(engine, view.id).status in ("submitted", "auto_submitted")


# ----- mở lại lượt đã bị tự chốt -----
def test_reopen_after_system_close_keeps_answers_and_cuts_off_old_device(engine, world):
    clock = Clock(OPENS + timedelta(minutes=20))
    view = start_attempt(engine, world, clock, index=18, device="may-a")
    sid = world["students"][18]
    with Session(engine) as db:
        service_for(db, clock).sync(view.id, sid, epoch=1, base_version=0, answers={"q1": "B"})
        closed = teacher_service(db, clock).force_submit(view.id, teacher_id=world["teacher"], reason="Em bị văng, hệ thống chốt")
        later = Clock(OPENS + timedelta(minutes=30))
        deadline = teacher_service(db, later).reopen_attempt(view.id, minutes=25, teacher_id=world["teacher"], reason="Cô cho làm tiếp")
        svc = service_for(db, later)
        with pytest.raises(EpochMismatch):
            svc.sync(view.id, sid, epoch=1, base_version=1, answers={"q1": "C"})  # máy cũ không ghi đè được
        row = fetch(engine, view.id)
        assert (row.status, row.write_epoch, row.answers, row.receipt_code, row.score) == ("in_progress", 2, {"q1": "B"}, None, None)
        assert deadline == later.now + timedelta(minutes=25)
        assert svc.sync(view.id, sid, epoch=2, base_version=row.answers_version, answers=FULL_MARKS) == row.answers_version + 1
        final = svc.submit(view.id, sid, epoch=2, answers=FULL_MARKS, request_id="r2")
    assert final.receipt_code != closed.receipt_code and final.score == Decimal("1.75")
    assert count(engine, ExamGradeHistory, ExamGradeHistory.attempt_id == view.id) == 2  # lịch sử chấm giữ cả hai lần
    reopen_log = [e for e in events_of(engine, view.id) if e.type == "teacher_reopen"]
    assert reopen_log[0].payload["previous_receipt"] == closed.receipt_code


def test_reopen_is_refused_for_self_submitted_and_for_running_attempts(engine, world):
    clock = Clock(OPENS + timedelta(minutes=20))
    done = start_attempt(engine, world, clock, index=19)
    running = start_attempt(engine, world, clock, index=20)
    with Session(engine) as db:
        service_for(db, clock).submit(done.id, world["students"][19], epoch=1, answers=FULL_MARKS, request_id="r1")
        with pytest.raises(InvalidTeacherAction):
            teacher_service(db, clock).reopen_attempt(done.id, minutes=10, teacher_id=world["teacher"], reason=TEACHER_REASON)
        with pytest.raises(InvalidTeacherAction):
            teacher_service(db, clock).reopen_attempt(running.id, minutes=10, teacher_id=world["teacher"], reason=TEACHER_REASON)
        with pytest.raises(NotAllowedToEnter):
            teacher_service(db, clock).reopen_attempt(10**9, minutes=10, teacher_id=world["teacher"], reason=TEACHER_REASON)
    assert fetch(engine, done.id).status == "submitted"


# ----- mở lượt mới -----
def test_extra_attempt_requires_the_current_one_to_be_finished(engine, world):
    clock = Clock(OPENS + timedelta(minutes=5))
    sid = world["students"][21]
    with Session(engine) as db:
        with pytest.raises(InvalidTeacherAction):  # chưa vào thi
            teacher_service(db, clock).open_extra_attempt(world["exam"], sid, teacher_id=world["teacher"], reason=TEACHER_REASON)
    view = start_attempt(engine, world, clock, index=21)
    with Session(engine) as db:
        with pytest.raises(InvalidTeacherAction):  # đang làm
            teacher_service(db, clock).open_extra_attempt(world["exam"], sid, teacher_id=world["teacher"], reason=TEACHER_REASON)
        service_for(db, clock).submit(view.id, sid, epoch=1, answers=FULL_MARKS, request_id="r1")
        new_id = teacher_service(db, clock).open_extra_attempt(world["exam"], sid, teacher_id=world["teacher"], reason=TEACHER_REASON, minutes=30)
    row = fetch(engine, new_id)
    assert (row.attempt_no, row.status, row.answers, row.granted_by, row.grant_reason) == (2, "in_progress", {}, world["teacher"], TEACHER_REASON)
    assert row.deadline_at == clock.now + timedelta(minutes=30)
    assert row.shuffle_seed is not None
    resumed = start_attempt(engine, world, clock, index=21)
    assert resumed.id == new_id and resumed.answers == {}  # em vào lại thấy lượt mới, đáp án trống
    assert fetch(engine, view.id).answers == FULL_MARKS  # lượt cũ còn nguyên
    assert any(e.type == "teacher_grant" and e.payload["previous_attempt_id"] == view.id for e in events_of(engine, new_id))


def test_double_clicking_open_extra_attempt_creates_exactly_one(engine, world):
    clock = Clock(OPENS + timedelta(minutes=5))
    sid = world["students"][22]
    view = start_attempt(engine, world, clock, index=22)
    with Session(engine) as db:
        service_for(db, clock).submit(view.id, sid, epoch=1, answers=FULL_MARKS, request_id="r1")
    results = run_parallel(
        engine, clock, 8,
        lambda svc, i: TeacherControlService(svc).open_extra_attempt(world["exam"], sid, teacher_id=world["teacher"], reason="bấm nhiều lần"),
    )
    assert len(oks(results)) == 1
    assert all(isinstance(e, InvalidTeacherAction) for e in errs(results))
    assert count(engine, ExamAttempt, ExamAttempt.exam_id == world["exam"], ExamAttempt.student_id == sid) == 2


def test_extra_attempt_refused_for_non_participant_and_unpublished_exam(engine, world):
    clock = Clock(OPENS + timedelta(minutes=5))
    with Session(engine) as db:
        with pytest.raises(InvalidTeacherAction):
            teacher_service(db, clock).open_extra_attempt(world["exam"], world["teacher"], teacher_id=world["teacher"], reason=TEACHER_REASON)
        with pytest.raises(InvalidTeacherAction):
            teacher_service(db, clock).open_extra_attempt(10**9, world["students"][0], teacher_id=world["teacher"], reason=TEACHER_REASON)


# ----- sự kiện từ trình duyệt -----
def test_events_are_recorded_deduplicated_and_filtered(engine, world):
    clock = Clock(OPENS + timedelta(minutes=5))
    view = start_attempt(engine, world, clock, index=23)
    sid = world["students"][23]
    batch = [
        {"type": "visibility_hidden", "seq": 1, "offset_ms": 1000},
        {"type": "visibility_visible", "seq": 2, "offset_ms": 4000, "payload": {"away_ms": 3000}},
        {"type": "khong-ton-tai", "seq": 3},  # loại sự kiện lạ bị bỏ
        {"type": "paste", "seq": 4, "payload": {"blob": "x" * 5000}},  # payload quá lớn bị bỏ
        {"type": "fullscreen_exit", "seq": 5},
    ]
    with Session(engine) as db:
        svc = service_for(db, clock)
        assert svc.record_events(view.id, sid, batch) == 3
        assert svc.record_events(view.id, sid, batch) == 0  # gửi lại cả lô (sendBeacon thử lại) vô hại
        assert svc.record_events(view.id, sid, [{"type": "online", "seq": 6}]) == 1
    types = [e.type for e in events_of(engine, view.id)]
    assert types == ["visibility_hidden", "visibility_visible", "fullscreen_exit", "online"]


def test_events_are_capped_per_request_and_per_attempt(engine, world):
    clock = Clock(OPENS + timedelta(minutes=5))
    view = start_attempt(engine, world, clock, index=24)
    sid = world["students"][24]
    with Session(engine) as db:
        svc = service_for(db, clock)
        flood = [{"type": "blur", "seq": i} for i in range(1, 121)]
        assert svc.record_events(view.id, sid, flood) == 50  # tối đa 50 mỗi lô
    assert count(engine, ExamAttemptEvent, ExamAttemptEvent.attempt_id == view.id) == 50


def test_events_of_another_student_are_refused(engine, world):
    clock = Clock(OPENS + timedelta(minutes=5))
    view = start_attempt(engine, world, clock, index=25)
    with Session(engine) as db:
        with pytest.raises(NotAllowedToEnter):
            service_for(db, clock).record_events(view.id, world["students"][26], [{"type": "blur", "seq": 1}])
    assert count(engine, ExamAttemptEvent, ExamAttemptEvent.attempt_id == view.id) == 0


def test_repository_never_shortens_a_deadline_or_touches_a_finished_attempt(engine, world):
    """Lớp bảo vệ thứ hai ở câu UPDATE: dù service có lỗi, hạn nộp không bị rút ngắn và bài đã nộp không bị đụng."""
    clock = Clock(OPENS + timedelta(minutes=5))
    view = start_attempt(engine, world, clock, index=27)
    done = start_attempt(engine, world, clock, index=28)
    with Session(engine) as db:
        service_for(db, clock).submit(done.id, world["students"][28], epoch=1, answers=FULL_MARKS, request_id="r1")
        repo = AttemptRepository(db)
        assert repo.extend_attempt_deadline(view.id, view.deadline_at - timedelta(minutes=10)) == 0
        assert repo.extend_attempt_deadline(view.id, view.deadline_at) == 0  # bằng hạn cũ cũng không đổi
        assert repo.extend_attempt_deadline(done.id, done.deadline_at + timedelta(hours=1)) == 0
        assert repo.reopen_attempt(done.id, done.deadline_at + timedelta(hours=1)) == 0  # chỉ mở lại lượt bị tự chốt
        db.rollback()
    assert fetch(engine, view.id).deadline_at == view.deadline_at
    assert fetch(engine, done.id).status == "submitted"
