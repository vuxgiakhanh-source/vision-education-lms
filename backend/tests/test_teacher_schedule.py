from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import os
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session, sessionmaker

from app.core.enums.user_role import UserRole
from app.core.security import create_access_token
from app.database.database import engine as local_engine, get_session_factory
from app.main import app
from app.models.classroom import Class, ClassEnrollment
from app.models.schedule import ClassSession, SessionAttendance, SessionsTransfer
from app.models.student import Student
from app.models.user import User
from app.core import clock


WEEKLY = "/teacher/schedule/weekly?week_start=2026-11-27"
UPCOMING = "/teacher/schedule/upcoming"
MONDAY = datetime(2026, 11, 23)


@pytest.fixture
def teacher_api(monkeypatch, sqlite_engine):
    engine = sqlite_engine

    with Session(engine) as db:
        for user_id, role, active, must_change in (
            (1, UserRole.TEACHER, True, False),
            (2, UserRole.STUDENT, True, False),
            (3, UserRole.TEACHER, False, False),
            (4, UserRole.TEACHER, True, True),
        ):
            db.add(User(
                id=user_id, role=role, full_name=f"User {user_id}", phone_number=str(user_id),
                hashed_password="unused", is_active=active, must_change_password=must_change,
            ))
        db.add_all([
            Class(id=1, name="12A", grade=12, starts_at=MONDAY),
            Class(id=2, name="11A", grade=11, starts_at=MONDAY),
        ])
        for session_id, class_id, starts_at, status in (
            (1, 1, MONDAY, "scheduled"),
            (2, 2, MONDAY, "scheduled"),
            (3, 1, MONDAY + timedelta(days=1), "cancelled"),
            (4, 2, MONDAY + timedelta(days=7), "scheduled"),
        ):
            db.add(ClassSession(
                id=session_id, class_id=class_id, topic="Nội dung buổi dạy", starts_at=starts_at,
                ends_at=starts_at + timedelta(hours=2), status=status,
            ))
        db.commit()

    session_factory = sessionmaker(bind=engine)
    monkeypatch.setitem(app.dependency_overrides, get_session_factory, lambda: session_factory)
    with TestClient(app) as client:
        yield client


def authorization(user_id=1):
    token = create_access_token({"id": user_id}, timedelta(minutes=1))
    return {"Authorization": f"Bearer {token}"}


def test_weekly_spans_grades_and_preserves_same_slot(teacher_api):
    response = teacher_api.get(WEEKLY, headers=authorization())
    assert response.status_code == 200
    assert response.json()["week_start"] == "2026-11-23"
    assert [(item["id"], item["class_name"]) for item in response.json()["sessions"]] == [(1, "12A"), (2, "11A")]


def test_upcoming_excludes_ongoing_and_cancelled_sessions(teacher_api, monkeypatch):
    monkeypatch.setattr(clock, "center_local_now", lambda: MONDAY + timedelta(minutes=1))
    assert teacher_api.get(UPCOMING, headers=authorization()).json()["id"] == 4
    monkeypatch.setattr(clock, "center_local_now", lambda: MONDAY + timedelta(days=8))
    assert teacher_api.get(UPCOMING, headers=authorization()).json() is None


def test_detail_reads_times_and_hides_cancelled_sessions(teacher_api):
    detail = teacher_api.get("/teacher/sessions/2", headers=authorization())
    assert detail.status_code == 200
    assert detail.json()["ends_at"] == "2026-11-23T02:00:00"
    assert teacher_api.get("/teacher/sessions/3", headers=authorization()).status_code == 404
    assert teacher_api.get("/teacher/sessions/999", headers=authorization()).status_code == 404


@pytest.mark.parametrize("user_id, expected_status", [(2, 403), (3, 403), (4, 403), (999, 401)])
def test_every_teacher_endpoint_checks_account(teacher_api, user_id, expected_status):
    for path in (WEEKLY, UPCOMING, "/teacher/sessions/1"):
        assert teacher_api.get(path, headers=authorization(user_id)).status_code == expected_status


ADJUSTMENT_URL = "/teacher/sessions"
SOURCE_START = MONDAY + timedelta(days=1, hours=14)
OTHER_START = MONDAY + timedelta(days=2, hours=18)


@pytest.fixture
def adjustment_api(teacher_api, monkeypatch):
    monkeypatch.setattr(clock, "center_local_now", lambda: MONDAY)
    session_factory = app.dependency_overrides[get_session_factory]()
    with session_factory.begin() as db:
        db.add(Student(user_id=2, grade=12))
        for session_id, class_id, start in ((5, 1, SOURCE_START), (6, 2, OTHER_START)):
            db.add(ClassSession(
                id=session_id, class_id=class_id, topic=f"Buổi {session_id}",
                teaching_week=17, starts_at=start, ends_at=start + timedelta(hours=3),
            ))
        db.add(SessionsTransfer(student_id=2, original_session_id=5, replacement_sessions_id=6))
    return teacher_api, session_factory


def session_time(start):
    return {"starts_at": start.isoformat(), "ends_at": (start + timedelta(hours=3)).isoformat()}


def move_body(target_date="2026-12-01", target_shift="morning"):
    return {
        "expected_time": session_time(SOURCE_START),
        "target_date": target_date,
        "target_shift": target_shift,
    }


def swap_body():
    return {
        "other_session_id": 6,
        "expected_time": session_time(SOURCE_START),
        "expected_other_time": session_time(OTHER_START),
    }


def test_move_across_weeks_keeps_session_and_transfer_ids(adjustment_api):
    client, session_factory = adjustment_api
    url = f"{ADJUSTMENT_URL}/5/move"
    for _ in range(2):
        assert client.put(url, headers=authorization(), json=move_body()).status_code == 204
    assert client.get("/teacher/sessions/5", headers=authorization()).json()["starts_at"] == "2026-12-01T07:30:00"
    with session_factory() as db:
        session = db.get(ClassSession, 5)
        assert (session.class_id, session.teaching_week, session.topic) == (1, 17, "Buổi 5")
        assert session.ends_at.isoformat() == "2026-12-01T10:30:00"
        assert db.get(SessionsTransfer, (2, 5)).replacement_sessions_id == 6


def test_move_rejects_overlap_stale_snapshot_and_past(adjustment_api):
    client, session_factory = adjustment_api
    url = f"{ADJUSTMENT_URL}/5/move"
    overlap = client.put(url, headers=authorization(), json=move_body("2026-11-25", "evening"))
    assert overlap.status_code == 409
    stale = client.put(url, headers=authorization(), json={
        **move_body(), "expected_time": session_time(OTHER_START),
    })
    assert stale.status_code == 409 and stale.json()["detail"]["code"] == "SESSION_TIME_CHANGED"
    assert client.put(url, headers=authorization(), json=move_body("2026-11-22")).status_code == 409
    with session_factory() as db:
        assert db.get(ClassSession, 5).starts_at == SOURCE_START


def test_swap_is_atomic_and_safe_to_retry(adjustment_api):
    client, session_factory = adjustment_api
    url = f"{ADJUSTMENT_URL}/5/swap"
    for _ in range(2):
        assert client.put(url, headers=authorization(), json=swap_body()).status_code == 204
    with session_factory() as db:
        source = db.get(ClassSession, 5)
        other = db.get(ClassSession, 6)
        assert (source.starts_at, source.ends_at, source.class_id) == (
            OTHER_START, OTHER_START + timedelta(hours=3), 1,
        )
        assert (other.starts_at, other.ends_at, other.class_id) == (
            SOURCE_START, SOURCE_START + timedelta(hours=3), 2,
        )
        assert db.get(SessionsTransfer, (2, 5)).replacement_sessions_id == 6


def test_swap_rejects_stale_or_attended_target_without_partial_update(adjustment_api):
    client, session_factory = adjustment_api
    url = f"{ADJUSTMENT_URL}/5/swap"
    same_session = client.put(url, headers=authorization(), json={**swap_body(), "other_session_id": 5})
    assert same_session.status_code == 422
    stale = client.put(url, headers=authorization(), json={
        **swap_body(), "expected_other_time": session_time(SOURCE_START),
    })
    assert stale.status_code == 409 and stale.json()["detail"]["code"] == "SESSION_TIME_CHANGED"
    with session_factory.begin() as db:
        db.add(SessionAttendance(student_id=2, session_id=6))
    assert client.put(url, headers=authorization(), json=swap_body()).status_code == 409
    with session_factory() as db:
        assert db.get(ClassSession, 5).starts_at == SOURCE_START
        assert db.get(ClassSession, 6).starts_at == OTHER_START


def test_swap_within_same_class_preserves_week_order(adjustment_api):
    client, session_factory = adjustment_api
    with session_factory.begin() as db:
        other = db.get(ClassSession, 6)
        other.class_id = 1
        other.teaching_week = 18

    response = client.put(f"{ADJUSTMENT_URL}/5/swap", headers=authorization(), json=swap_body())
    assert response.status_code == 204
    with session_factory() as db:
        assert db.get(ClassSession, 5).starts_at == SOURCE_START
        assert db.get(ClassSession, 6).starts_at == OTHER_START


def test_move_keeps_week_and_pending_transfer_follows_lesson(adjustment_api, monkeypatch):
    client, session_factory = adjustment_api
    later = MONDAY + timedelta(days=4, hours=14)
    with session_factory.begin() as db:
        db.get(Class, 2).grade = 12
        db.delete(db.get(SessionsTransfer, (2, 5)))
        db.add(SessionsTransfer(student_id=2, original_session_id=6, replacement_sessions_id=5))
        db.add(ClassEnrollment(student_id=2, class_id=2, starts_at=MONDAY - timedelta(days=1)))
        db.add(ClassSession(
            id=7, class_id=1, topic="Buổi 18", teaching_week=18,
            starts_at=later, ends_at=later + timedelta(hours=3),
        ))

    url = f"{ADJUSTMENT_URL}/5/move"
    assert client.put(url, headers=authorization(), json=move_body("2026-11-29")).status_code == 204
    assert client.put(url, headers=authorization(), json=move_body("2026-11-29")).status_code == 409
    with session_factory() as db:
        lesson_17 = db.get(ClassSession, 5)
        lesson_18 = db.get(ClassSession, 7)
        assert (lesson_17.teaching_week, lesson_17.topic, lesson_17.starts_at) == (17, "Buổi 5", later)
        assert lesson_18.starts_at == datetime(2026, 11, 29, 7, 30)
        transfer = db.get(SessionsTransfer, (2, 6))
        assert transfer.replacement_sessions_id == 5 and transfer.requires_confirmation

    monkeypatch.setattr(clock, "center_local_now", lambda: OTHER_START + timedelta(hours=3, minutes=1))
    pending_url = "/schedule/temporary-transfers/pending"
    pending = client.get(pending_url, headers=authorization(2))
    assert pending.status_code == 200 and len(pending.json()) == 1
    changed = pending.json()[0]
    assert (changed["teaching_week"], changed["session_id"], changed["starts_at"]) == (17, 5, later.isoformat())
    assert client.get("/schedule/upcoming", headers=authorization(2)).json()["starts_at"] == "2026-11-30T00:00:00"

    confirm_url = "/schedule/temporary-transfers/6/reconfirm"
    request = {
        "target_session_id": 5,
        "expected_target_starts_at": SOURCE_START.isoformat(),
        "expected_target_ends_at": (SOURCE_START + timedelta(hours=3)).isoformat(),
    }
    stale = client.put(confirm_url, headers=authorization(2), json=request)
    assert stale.status_code == 409 and stale.json()["detail"]["code"] == "SESSION_TIME_CHANGED"
    request.update(expected_target_starts_at=changed["starts_at"], expected_target_ends_at=changed["ends_at"])
    for _ in range(2):
        assert client.put(confirm_url, headers=authorization(2), json=request).status_code == 204
    assert client.get(pending_url, headers=authorization(2)).json() == []
    assert client.get("/schedule/upcoming", headers=authorization(2)).json()["topic"] == "Buổi 5"


def test_swap_keeps_chronology_in_both_affected_classes(adjustment_api):
    client, session_factory = adjustment_api
    class_1_middle = MONDAY + timedelta(days=2, hours=14)
    class_2_middle = MONDAY + timedelta(days=2, hours=7, minutes=30)
    with session_factory.begin() as db:
        for session_id, class_id, teaching_week, start in (
            (7, 1, 18, class_1_middle),
            (8, 2, 16, class_2_middle),
        ):
            db.add(ClassSession(
                id=session_id, class_id=class_id, teaching_week=teaching_week, topic=f"Buổi {teaching_week}",
                starts_at=start, ends_at=start + timedelta(hours=3),
            ))
    assert client.put(f"{ADJUSTMENT_URL}/5/swap", headers=authorization(), json=swap_body()).status_code == 204
    with session_factory() as db:
        assert db.get(ClassSession, 5).starts_at == class_1_middle
        assert db.get(ClassSession, 7).starts_at == OTHER_START
        assert db.get(ClassSession, 8).starts_at == SOURCE_START
        assert db.get(ClassSession, 6).starts_at == class_2_middle


def test_move_rolls_back_if_reordering_touches_attendance(adjustment_api):
    client, session_factory = adjustment_api
    later = MONDAY + timedelta(days=4, hours=14)
    with session_factory.begin() as db:
        db.add(ClassSession(
            id=7, class_id=1, topic="Đã điểm danh", teaching_week=18,
            starts_at=later, ends_at=later + timedelta(hours=3),
        ))
        db.add(SessionAttendance(student_id=2, session_id=7))
    assert client.put(f"{ADJUSTMENT_URL}/5/move", headers=authorization(), json=move_body("2026-11-29")).status_code == 409
    with session_factory() as db:
        assert db.get(ClassSession, 5).starts_at == SOURCE_START
        assert db.get(ClassSession, 7).starts_at == later


def test_adjustment_routes_enforce_teacher_role_and_start_time(adjustment_api, monkeypatch):
    client, _ = adjustment_api
    move_url = f"{ADJUSTMENT_URL}/5/move"
    swap_url = f"{ADJUSTMENT_URL}/5/swap"
    assert client.put(move_url, headers=authorization(2), json=move_body()).status_code == 403
    assert client.put(swap_url, headers=authorization(2), json=swap_body()).status_code == 403
    monkeypatch.setattr(clock, "center_local_now", lambda: SOURCE_START)
    assert client.put(move_url, headers=authorization(), json=move_body()).status_code == 409
    assert client.put(swap_url, headers=authorization(), json=swap_body()).status_code == 409


@pytest.mark.skipif(os.getenv("SCHEDULE_MYSQL_TESTS") != "1", reason="requires migrated local MySQL")
def test_two_mysql_moves_cannot_claim_same_empty_slot():
    unique = uuid4().hex
    future = datetime(2099, 7, 6, 14) + timedelta(days=int(unique[:4], 16) % 1_000)
    with Session(local_engine, expire_on_commit=False) as db, db.begin():
        teacher = User(
            full_name="Teacher concurrency fixture", phone_number=unique, hashed_password="unused",
            role=UserRole.TEACHER, must_change_password=False,
        )
        classroom = Class(name=f"Teacher concurrency {unique}", grade=12, starts_at=future)
        db.add_all([teacher, classroom])
        db.flush()
        sessions = [
            ClassSession(class_id=classroom.id, topic="Test move", starts_at=start, ends_at=start + timedelta(hours=3))
            for start in (future, future + timedelta(days=1))
        ]
        db.add_all(sessions)
        db.flush()
        teacher_id, class_id = teacher.id, classroom.id
        snapshots = [(session.id, session.starts_at) for session in sessions]

    try:
        assert local_engine.dialect.name == "mysql"
        ready = Barrier(2)
        target = (future + timedelta(days=2)).date().isoformat()
        with TestClient(app) as client, ThreadPoolExecutor(max_workers=2) as executor:
            def move(snapshot):
                session_id, starts_at = snapshot
                ready.wait(timeout=5)
                return client.put(f"{ADJUSTMENT_URL}/{session_id}/move", headers=authorization(teacher_id), json={
                    "expected_time": session_time(starts_at), "target_date": target, "target_shift": "morning",
                }).status_code

            assert sorted(executor.map(move, snapshots)) == [204, 409]
    finally:
        with Session(local_engine) as db, db.begin():
            db.execute(delete(ClassSession).where(ClassSession.class_id == class_id))
            db.execute(delete(Class).where(Class.id == class_id))
            db.execute(delete(User).where(User.id == teacher_id))
