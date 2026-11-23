from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.base import Base
from app.core.dependencies import get_current_user_id
from app.core.enums.user_role import UserRole
from app.database.database import get_session_factory
from app.main import app
from app.models.classroom import Class, ClassEnrollment
from app.models.schedule import ClassSession, SessionAttendance, SessionsTransfer
from app.models.student import Student
from app.models.user import User
from app.core import clock


OPTIONS_URL = "/schedule/temporary-transfers/options"
ORIGINAL_START = datetime(2026, 11, 23, 14)
CURRENT_START = datetime(2026, 11, 27, 14)
CURRENT_END = CURRENT_START + timedelta(hours=3)
NEXT_START = datetime(2026, 11, 28, 14)


def add_session(db, session_id, class_id, week, starts_at, *, ends_at=None, status="scheduled"):
    db.add(
        ClassSession(
            id=session_id,
            class_id=class_id,
            teaching_week=week,
            topic=f"Nội dung tuần {week}",
            starts_at=starts_at,
            ends_at=ends_at or starts_at + timedelta(hours=3),
            status=status,
        )
    )


@pytest.fixture
def schedule_api():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all(
            [
                User(
                    id=1,
                    full_name="Học sinh kiểm thử",
                    phone_number="0000000000",
                    hashed_password="unused",
                    role=UserRole.STUDENT,
                    must_change_password=False,
                ),
                Student(user_id=1, grade=12),
                Class(id=1, name="12A", grade=12, starts_at=ORIGINAL_START),
                Class(id=2, name="12B", grade=12, starts_at=ORIGINAL_START),
                Class(id=3, name="11A", grade=11, starts_at=ORIGINAL_START),
                ClassEnrollment(student_id=1, class_id=1, starts_at=ORIGINAL_START),
            ]
        )
        db.add_all(
            Class(id=class_id, name=name, grade=12, starts_at=ORIGINAL_START)
            for class_id, name in enumerate(("12C", "12D", "12E", "12F"), start=4)
        )
        add_session(db, 1, 1, 17, ORIGINAL_START)
        add_session(db, 2, 2, 17, CURRENT_START)
        add_session(db, 3, 4, 17, datetime(2026, 11, 30, 14))
        add_session(db, 4, 1, 18, NEXT_START)
        add_session(db, 5, 2, 18, NEXT_START)
        add_session(db, 6, 3, 17, CURRENT_START)
        add_session(db, 7, 5, 17, CURRENT_START, status="cancelled")
        add_session(db, 8, 2, None, CURRENT_START)
        add_session(db, 9, 6, 17, ORIGINAL_START)
        add_session(db, 10, 7, 17, CURRENT_START)
        db.add(SessionsTransfer(student_id=1, original_session_id=1, replacement_sessions_id=2))
        db.commit()

    session_factory = sessionmaker(bind=engine)
    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_session_factory] = lambda: session_factory
    app.dependency_overrides[get_current_user_id] = lambda: 1
    try:
        with TestClient(app) as client:
            yield client, engine
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        engine.dispose()


def read_options(client, now):
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(clock, "center_local_now", lambda: now)
        response = client.get(OPTIONS_URL)
    assert response.status_code == 200, response.text
    return response.json()


def read_upcoming(client, now):
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(clock, "center_local_now", lambda: now)
        response = client.get("/schedule/upcoming")
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize("now", [CURRENT_START + timedelta(hours=1), CURRENT_END])
def test_keeps_transferred_session_while_it_is_ongoing_after_original_ended(schedule_api, now):
    client, engine = schedule_api

    response = read_options(client, now)

    assert response["source"] == {
        "enrollment_id": 1,
        "original_session_id": 1,
        "current_session_id": 2,
        "teaching_week": 17,
        "topic": "Nội dung tuần 17",
        "starts_at": CURRENT_START.isoformat(),
        "ends_at": CURRENT_END.isoformat(),
    }
    assert [option["session_id"] for option in response["options"]] == [10, 3]
    assert response["blocked_reason"] is None
    with Session(engine) as db:
        assert db.get(SessionsTransfer, (1, 1)).replacement_sessions_id == 2


def test_moves_to_next_assigned_lesson_after_current_session_ends(schedule_api):
    client, _ = schedule_api

    response = read_options(client, CURRENT_END + timedelta(seconds=1))

    assert response["source"]["original_session_id"] == 4
    assert response["source"]["current_session_id"] == 4
    assert response["source"]["teaching_week"] == 18
    assert [option["session_id"] for option in response["options"]] == [5]


def test_does_not_revive_original_when_earlier_replacement_has_finished(schedule_api):
    client, engine = schedule_api
    with Session(engine) as db:
        original = db.get(ClassSession, 1)
        original.starts_at = NEXT_START
        original.ends_at = NEXT_START + timedelta(hours=3)
        next_session = db.get(ClassSession, 4)
        next_session.starts_at = NEXT_START + timedelta(days=1)
        next_session.ends_at = next_session.starts_at + timedelta(hours=3)
        db.commit()

    response = read_options(client, CURRENT_END + timedelta(seconds=1))

    assert response["source"]["original_session_id"] == 4


def test_offers_original_if_it_is_still_eligible(schedule_api):
    client, engine = schedule_api
    with Session(engine) as db:
        original = db.get(ClassSession, 1)
        original.starts_at = datetime(2026, 11, 28, 7, 30)
        original.ends_at = original.starts_at + timedelta(hours=3)
        db.commit()

    response = read_options(client, CURRENT_START + timedelta(hours=1))

    assert response["source"]["current_session_id"] == 2
    assert [option["session_id"] for option in response["options"]] == [10, 1, 3]


def test_uses_original_when_transfer_destination_is_null(schedule_api):
    client, engine = schedule_api
    with Session(engine) as db:
        db.get(SessionsTransfer, (1, 1)).replacement_sessions_id = None
        db.commit()

    response = read_options(client, ORIGINAL_START + timedelta(hours=1))

    assert response["source"]["original_session_id"] == 1
    assert response["source"]["current_session_id"] == 1
    assert [option["session_id"] for option in response["options"]] == [9, 2, 10, 3]


def test_follows_replacement_when_teacher_moves_it_to_next_calendar_week(schedule_api):
    client, engine = schedule_api
    moved_start = datetime(2026, 11, 30, 14)
    with Session(engine) as db:
        current = db.get(ClassSession, 2)
        current.starts_at = moved_start
        current.ends_at = moved_start + timedelta(hours=3)
        db.commit()

    response = read_options(client, moved_start + timedelta(hours=1))

    assert response["source"]["original_session_id"] == 1
    assert response["source"]["current_session_id"] == 2
    assert response["source"]["starts_at"] == moved_start.isoformat()
    assert [option["session_id"] for option in response["options"]] == [3]


def test_returns_reason_if_upcoming_session_has_no_teaching_week(schedule_api):
    client, engine = schedule_api
    with Session(engine) as db:
        db.get(ClassSession, 1).teaching_week = None
        db.commit()

    response = read_options(client, CURRENT_START)

    assert response["source"]["teaching_week"] is None
    assert response["options"] == []
    assert response["blocked_reason"] == "MISSING_TEACHING_WEEK"


def test_returns_reason_if_student_has_no_assignment(schedule_api):
    client, engine = schedule_api
    with Session(engine) as db:
        db.query(ClassEnrollment).filter_by(student_id=1).delete()
        db.commit()

    response = read_options(client, CURRENT_START)

    assert response == {"source": None, "options": [], "blocked_reason": "NO_UPCOMING_SESSION"}
    assert read_upcoming(client, ORIGINAL_START) is None


def test_returns_reason_if_no_eligible_options_remain(schedule_api):
    client, engine = schedule_api
    with Session(engine) as db:
        db.get(ClassSession, 3).status = "cancelled"
        db.get(ClassSession, 10).status = "cancelled"
        db.commit()

    response = read_options(client, CURRENT_START)

    assert response["source"]["current_session_id"] == 2
    assert response["options"] == []
    assert response["blocked_reason"] == "NO_ELIGIBLE_SESSIONS"


def confirm_transfer(
    client, now, *, original_id=1, current_id=2, target_id, target_start, target_end=None
):
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(clock, "center_local_now", lambda: now)
        return client.put(
            f"/schedule/temporary-transfers/{original_id}",
            json={
                "expected_enrollment_id": 1,
                "expected_current_session_id": current_id,
                "target_session_id": target_id,
                "expected_target_starts_at": target_start.isoformat(),
                "expected_target_ends_at": (target_end or target_start + timedelta(hours=3)).isoformat(),
            },
        )


def test_presence_locks_old_confirmation_and_opens_options_for_next_teaching_week(schedule_api):
    client, engine = schedule_api
    with Session(engine) as db:
        db.add(SessionAttendance(student_id=1, session_id=2))
        db.commit()

    now = CURRENT_START + timedelta(hours=1)
    response = confirm_transfer(client, now, target_id=10, target_start=CURRENT_START)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "ALREADY_PRESENT"

    options = read_options(client, now)
    assert options["source"]["current_session_id"] == 4
    assert options["source"]["teaching_week"] == 18
    assert [option["session_id"] for option in options["options"]] == [5]
    assert read_upcoming(client, now)["topic"] == "Nội dung tuần 18"
    with Session(engine) as db:
        assert db.get(SessionsTransfer, (1, 1)).replacement_sessions_id == 2

    response = confirm_transfer(
        client, now, original_id=4, current_id=4, target_id=5, target_start=NEXT_START
    )
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        assert db.get(SessionsTransfer, (1, 4)).replacement_sessions_id == 5


def test_moved_target_requires_confirmation_with_new_times(schedule_api):
    client, engine = schedule_api
    moved_start = CURRENT_START + timedelta(hours=1)
    moved_end = moved_start + timedelta(hours=2)
    with Session(engine) as db:
        target = db.get(ClassSession, 10)
        target.starts_at = moved_start
        target.ends_at = moved_end
        db.commit()

    now = CURRENT_START + timedelta(hours=1, minutes=15)
    response = confirm_transfer(client, now, target_id=10, target_start=CURRENT_START)
    assert response.status_code == 409
    assert response.json()["detail"] == {
        "code": "SESSION_TIME_CHANGED",
        "option": {
            "session_id": 10,
            "starts_at": moved_start.isoformat(),
            "ends_at": moved_end.isoformat(),
        },
    }
    with Session(engine) as db:
        assert db.get(SessionsTransfer, (1, 1)).replacement_sessions_id == 2

    response = confirm_transfer(
        client, now, target_id=10, target_start=moved_start, target_end=moved_end
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"original_session_id": 1, "current_session_id": 10}
    assert read_upcoming(client, now) == {
        "grade": 12,
        "topic": "Nội dung tuần 17",
        "starts_at": moved_start.isoformat(),
        "ends_at": moved_end.isoformat(),
    }
    weekly = client.get("/schedule/weekly", params={"week_start": "2026-11-23"})
    assert weekly.status_code == 200, weekly.text
    assert weekly.json()["transferred_session_ids"] == [1]
    assert weekly.json()["my_session_ids"] == [10, 4]
    with Session(engine) as db:
        assert db.get(SessionsTransfer, (1, 1)).replacement_sessions_id == 10


def test_reselecting_original_clears_replacement_without_removing_record(schedule_api):
    client, engine = schedule_api
    original_start = datetime(2026, 11, 28, 7, 30)
    with Session(engine) as db:
        original = db.get(ClassSession, 1)
        original.starts_at = original_start
        original.ends_at = original_start + timedelta(hours=3)
        db.commit()

    now = CURRENT_START + timedelta(hours=1)
    response = confirm_transfer(client, now, target_id=1, target_start=original_start)

    assert response.status_code == 200, response.text
    assert response.json() == {"original_session_id": 1, "current_session_id": 1}
    with Session(engine) as db:
        assert db.get(SessionsTransfer, (1, 1)).replacement_sessions_id is None
    assert read_options(client, now)["source"]["current_session_id"] == 1


def test_second_tab_cannot_overwrite_a_newer_transfer(schedule_api):
    client, engine = schedule_api
    now = CURRENT_START + timedelta(hours=1)
    response = confirm_transfer(client, now, target_id=10, target_start=CURRENT_START)
    assert response.status_code == 200, response.text

    response = confirm_transfer(
        client, now, target_id=3, target_start=datetime(2026, 11, 30, 14)
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "SOURCE_CHANGED"
    with Session(engine) as db:
        assert db.get(SessionsTransfer, (1, 1)).replacement_sessions_id == 10


@pytest.mark.parametrize("target_id", [2, 5, 6, 7, 8, 9])
def test_unavailable_target_leaves_existing_transfer_intact(schedule_api, target_id):
    client, engine = schedule_api
    response = confirm_transfer(
        client, CURRENT_START + timedelta(hours=1), target_id=target_id, target_start=CURRENT_START
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "TARGET_UNAVAILABLE"
    with Session(engine) as db:
        assert db.get(SessionsTransfer, (1, 1)).replacement_sessions_id == 2


@pytest.mark.parametrize("seconds_after_end, expected_status", [(0, 200), (1, 409)])
def test_confirmation_at_and_after_end(schedule_api, seconds_after_end, expected_status):
    client, _ = schedule_api
    response = confirm_transfer(
        client,
        CURRENT_END + timedelta(seconds=seconds_after_end),
        target_id=10,
        target_start=CURRENT_START,
    )

    assert response.status_code == expected_status, response.text
