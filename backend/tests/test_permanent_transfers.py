from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import os
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.base import Base
from app.core.enums.user_role import UserRole
from app.core.security import create_access_token
from app.database.database import engine as local_engine, get_session_factory
from app.main import app
from app.models.classroom import Class, ClassEnrollment
from app.models.schedule import ClassSession, SessionAttendance, SessionsTransfer
from app.models.student import Student
from app.models.user import User
from app.modules.schedule import service as schedule_service
from app.modules.schedule.permanent_transfers.repository import PermanentTransferRepository


URL = "/schedule/permanent-transfers"
TEMPORARY_URL = "/schedule/temporary-transfers"
NOW = datetime(2026, 11, 20, 15)
MYSQL_ENABLED = os.getenv("SCHEDULE_MYSQL_TESTS") == "1"


@pytest.fixture(params=["sqlite", "mysql"] if MYSQL_ENABLED else ["sqlite"])
def schedule_engine(request):
    if request.param == "mysql":
        assert local_engine.dialect.name == "mysql"
        yield local_engine
        return

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def open_api(monkeypatch):
    monkeypatch.setattr(schedule_service, "schedule_now", lambda: NOW)

    def api(engine):
        session_factory = sessionmaker(bind=engine)
        monkeypatch.setitem(app.dependency_overrides, get_session_factory, lambda: session_factory)
        return TestClient(app)

    return api


@pytest.fixture
def seed():
    created = []
    prefix = "Transfer test " + uuid4().hex

    def seed_data(engine, *, capacity=5, students=1):
        with Session(engine) as db:
            classrooms = [
                Class(name=f"{prefix} {label}", grade=12, starts_at=NOW - timedelta(days=30))
                for label in ("A", "B", "C")
            ]
            source, target, alternative = classrooms
            target.default_capacity = capacity
            db.add_all(classrooms)
            db.flush()
            ids = {label: classroom.id for label, classroom in zip(("source", "target", "alternative"), classrooms)}
            users = [
                User(
                    full_name=prefix,
                    phone_number=uuid4().hex,
                    hashed_password="unused",
                    role=UserRole.STUDENT,
                    must_change_password=False,
                )
                for _ in range(students)
            ]
            db.add_all(users)
            db.flush()
            ids["students"] = user_ids = [user.id for user in users]
            db.add_all(Student(user_id=user_id, grade=12) for user_id in user_ids)
            db.flush()
            db.add_all(
                ClassEnrollment(student_id=user_id, class_id=source.id, starts_at=source.starts_at)
                for user_id in user_ids
            )
            lessons = {
                "source_18": (source.id, 18, NOW - timedelta(days=1)),
                "source_19": (source.id, 19, NOW - timedelta(hours=1)),
                "target_18": (target.id, 18, NOW - timedelta(hours=1)),
                "target_19": (target.id, 19, NOW + timedelta(days=1)),
                "alternative_18": (alternative.id, 18, NOW - timedelta(days=2)),
                "alternative_19": (alternative.id, 19, NOW + timedelta(hours=1)),
            }
            for label, (class_id, week, starts_at) in lessons.items():
                session = ClassSession(
                    class_id=class_id,
                    teaching_week=week,
                    topic=label,
                    starts_at=starts_at,
                    ends_at=starts_at + timedelta(hours=3),
                )
                db.add(session)
                db.flush()
                ids[label] = session.id
            db.commit()
            created.append((engine, user_ids, [classroom.id for classroom in classrooms]))
            return ids

    yield seed_data

    for engine, users, classes in created:
        with engine.begin() as conn:
            for model in (SessionAttendance, SessionsTransfer, ClassEnrollment):
                conn.execute(delete(model).where(model.student_id.in_(users)))
            conn.execute(delete(ClassSession).where(ClassSession.class_id.in_(classes)))
            conn.execute(delete(Student).where(Student.user_id.in_(users)))
            conn.execute(delete(User).where(User.id.in_(users)))
            conn.execute(delete(Class).where(Class.id.in_(classes)))


def auth(student_id):
    token = create_access_token({"id": student_id}, timedelta(minutes=5))
    return {"Authorization": f"Bearer {token}"}


def get_choice(client, headers, class_id):
    response = client.get(URL + "/options", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    option = next(option for option in data["options"] if option["class_id"] == class_id)
    assert not option["is_full"]
    return data, {
        "target_class_id": class_id,
        "expected_current_enrollment_id": data["current_enrollment_id"],
        "expected_first_session": option["first_session"],
    }


def get_temporary_choice(client, headers, session_id):
    response = client.get(TEMPORARY_URL + "/options", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    source = data["source"]
    target = next(option for option in data["options"] if option["session_id"] == session_id)
    return source, {
        "expected_enrollment_id": source["enrollment_id"],
        "expected_current_session_id": source["current_session_id"],
        "target_session_id": target["session_id"],
        "expected_target_starts_at": target["starts_at"],
        "expected_target_ends_at": target["ends_at"],
    }


def test_join_ongoing_session_and_retire_old_planned_transfer(schedule_engine, seed, open_api):
    ids = seed(schedule_engine)
    student_id = ids["students"][0]
    headers = auth(student_id)
    with Session(schedule_engine) as db:
        db.add(SessionsTransfer(
            student_id=student_id, original_session_id=ids["source_19"],
            replacement_sessions_id=ids["alternative_19"],
        ))
        db.commit()
    with open_api(schedule_engine) as client:
        _, choice = get_choice(client, headers, ids["target"])
        assert choice["expected_first_session"]["session_id"] == ids["target_18"]
        response = client.post(URL, headers=headers, json=choice)
        assert response.status_code == 200, response.text
        assert response.json()["first_session"]["session_id"] == ids["target_18"]

        weekly = client.get("/schedule/weekly", headers=headers, params={"week_start": NOW.date().isoformat()})
        assert weekly.status_code == 200, weekly.text
        assert ids["target_18"] in weekly.json()["my_session_ids"]
        assert ids["source_19"] not in weekly.json()["my_session_ids"]
        assert ids["alternative_19"] not in weekly.json()["my_session_ids"]
        assert ids["source_19"] not in weekly.json()["transferred_session_ids"]
        upcoming = client.get("/schedule/upcoming", headers=headers)
        assert upcoming.json()["topic"] == "target_18"
        options = client.get("/schedule/temporary-transfers/options", headers=headers)
        assert options.json()["source"]["original_session_id"] == ids["target_18"]
        stale = client.post(URL, headers=headers, json=choice)
        assert stale.status_code == 409
        assert stale.json()["detail"]["code"] == "SOURCE_CHANGED"
    with Session(schedule_engine) as db:
        enrollment = db.get(ClassEnrollment, response.json()["enrollment_id"])
        assert enrollment.starts_at == NOW
        assert enrollment.entry_session_id == ids["target_18"]
        transfer = db.get(SessionsTransfer, (student_id, ids["source_19"]))
        assert transfer.superseded_at == NOW


@pytest.mark.skipif(not MYSQL_ENABLED, reason="requires migrated local MySQL")
def test_both_confirmations_complete_with_one_mysql_connection(seed, open_api):
    ids = seed(local_engine)
    headers = auth(ids["students"][0])
    engine = create_engine(local_engine.url, pool_size=1, max_overflow=0, pool_timeout=1)
    try:
        with open_api(engine) as client:
            source, temporary_choice = get_temporary_choice(client, headers, ids["alternative_19"])
            temporary_url = f"{TEMPORARY_URL}/{source['original_session_id']}"
            response = client.put(temporary_url, headers=headers, json=temporary_choice)
            assert response.status_code == 200, response.text

            _, permanent_choice = get_choice(client, headers, ids["target"])
            response = client.post(URL, headers=headers, json=permanent_choice)
            assert response.status_code == 200, response.text
        assert engine.pool.checkedout() == 0
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    ("account_flags", "expected_detail"),
    [
        ({"is_active": False}, {"code": "ACCOUNT_LOCKED", "message": "Tài khoản của bạn đã bị khóa"}),
        ({"must_change_password": True}, "Vui lòng đổi mật khẩu trước khi tiếp tục"),
    ],
)
def test_transfer_confirmations_enforce_account_access(schedule_engine, seed, open_api, account_flags, expected_detail):
    ids = seed(schedule_engine)
    student_id = ids["students"][0]
    headers = auth(student_id)
    with open_api(schedule_engine) as client:
        _, permanent_choice = get_choice(client, headers, ids["target"])
        source, temporary_choice = get_temporary_choice(client, headers, ids["alternative_19"])
        with Session(schedule_engine) as db:
            user = db.get(User, student_id)
            for name, value in account_flags.items():
                setattr(user, name, value)
            db.commit()

        temporary_url = f"{TEMPORARY_URL}/{source['original_session_id']}"
        for response in (
            client.put(temporary_url, headers=headers, json=temporary_choice),
            client.post(URL, headers=headers, json=permanent_choice),
        ):
            assert response.status_code == 403, response.text
            assert response.json()["detail"] == expected_detail


def test_skip_teaching_weeks_already_attended_in_another_class(schedule_engine, seed, open_api):
    ids = seed(schedule_engine)
    student_id = ids["students"][0]
    headers = auth(student_id)
    with Session(schedule_engine) as db:
        db.add(SessionAttendance(session_id=ids["alternative_18"], student_id=student_id))
        db.commit()
    with open_api(schedule_engine) as client:
        options, choice = get_choice(client, headers, ids["target"])
        assert options["completed_through_teaching_week"] == 18
        assert choice["expected_first_session"]["session_id"] == ids["target_19"]
        response = client.post(URL, headers=headers, json=choice)
        assert response.status_code == 200, response.text
        assert client.get("/schedule/upcoming", headers=headers).json()["topic"] == "target_19"
    with Session(schedule_engine) as db:
        assert db.get(SessionAttendance, (ids["alternative_18"], student_id)) is not None


def test_follow_first_session_moved_before_transfer_time(schedule_engine, seed, open_api):
    ids = seed(schedule_engine)
    student_id = ids["students"][0]
    headers = auth(student_id)
    session_id = ids["target_19"]
    moved_start = NOW - timedelta(hours=1)
    moved_end = NOW + timedelta(hours=2)

    with Session(schedule_engine) as db:
        db.add(SessionAttendance(session_id=ids["alternative_18"], student_id=student_id))
        db.commit()

    with open_api(schedule_engine) as client:
        _, choice = get_choice(client, headers, ids["target"])
        assert choice["expected_first_session"]["session_id"] == session_id
        response = client.post(URL, headers=headers, json=choice)
        assert response.status_code == 200, response.text

        with Session(schedule_engine) as db:
            session = db.get(ClassSession, session_id)
            assert session.starts_at > NOW
            session.starts_at = moved_start
            session.ends_at = moved_end
            db.commit()

        weekly = client.get("/schedule/weekly", headers=headers, params={"week_start": NOW.date().isoformat()})
        assert weekly.status_code == 200, weekly.text
        assert session_id in weekly.json()["my_session_ids"]
        moved_session = next(session for session in weekly.json()["sessions"] if session["id"] == session_id)
        assert moved_session["starts_at"] == moved_start.isoformat()
        assert moved_session["ends_at"] == moved_end.isoformat()

        upcoming = client.get("/schedule/upcoming", headers=headers)
        assert upcoming.status_code == 200, upcoming.text
        assert upcoming.json()["topic"] == "target_19"
        assert upcoming.json()["starts_at"] == moved_start.isoformat()
        assert upcoming.json()["ends_at"] == moved_end.isoformat()

    with Session(schedule_engine) as db:
        enrollment = db.get(ClassEnrollment, response.json()["enrollment_id"])
        assert enrollment.entry_session_id == session_id
        assert enrollment.starts_at == NOW


def test_old_temporary_tab_is_rejected_after_permanent_round_trip(schedule_engine, seed, open_api):
    ids = seed(schedule_engine)
    student_id = ids["students"][0]
    headers = auth(student_id)

    with open_api(schedule_engine) as client:
        original, stale = get_temporary_choice(client, headers, ids["alternative_19"])
        for destination in (ids["target"], ids["source"]):
            _, choice = get_choice(client, headers, destination)
            result = client.post(URL, headers=headers, json=choice)
            assert result.status_code == 200, result.text

        current, fresh = get_temporary_choice(client, headers, ids["alternative_19"])
        assert current["original_session_id"] == original["original_session_id"]
        assert current["current_session_id"] == original["current_session_id"]
        assert current["enrollment_id"] != original["enrollment_id"]

        endpoint = f'{TEMPORARY_URL}/{original["original_session_id"]}'
        stale_result = client.put(endpoint, headers=headers, json=stale)
        assert stale_result.status_code == 409, stale_result.text
        assert stale_result.json()["detail"]["code"] == "SOURCE_CHANGED"
        with Session(schedule_engine) as db:
            assert db.get(SessionsTransfer, (student_id, ids["source_19"])) is None
        assert client.get("/schedule/upcoming", headers=headers).json()["topic"] == "source_19"
        weekly = client.get("/schedule/weekly", headers=headers, params={"week_start": NOW.date().isoformat()})
        assert weekly.status_code == 200, weekly.text
        assert ids["source_19"] in weekly.json()["my_session_ids"]
        assert ids["alternative_19"] not in weekly.json()["my_session_ids"]

        fresh_result = client.put(endpoint, headers=headers, json=fresh)
        assert fresh_result.status_code == 200, fresh_result.text
        assert fresh_result.json()["current_session_id"] == ids["alternative_19"]


def test_late_attendance_in_old_class_updates_weekly_upcoming_and_transfer(schedule_engine, seed, open_api):
    ids = seed(schedule_engine)
    student_id = ids["students"][0]
    headers = auth(student_id)
    with Session(schedule_engine) as db:
        alternate = db.get(ClassSession, ids["alternative_18"])
        alternate.starts_at = NOW + timedelta(hours=5)
        alternate.ends_at = alternate.starts_at + timedelta(hours=3)
        db.commit()

    with open_api(schedule_engine) as client:
        _, choice = get_choice(client, headers, ids["target"])
        result = client.post(URL, headers=headers, json=choice)
        assert result.status_code == 200, result.text
        source, stale = get_temporary_choice(client, headers, ids["alternative_18"])
        assert source["current_session_id"] == ids["target_18"]
        assert client.get("/schedule/upcoming", headers=headers).json()["topic"] == "target_18"

        with Session(schedule_engine) as db:
            db.add(SessionAttendance(student_id=student_id, session_id=ids["source_18"]))
            db.commit()

        weekly = client.get("/schedule/weekly", headers=headers, params={"week_start": NOW.date().isoformat()})
        assert weekly.status_code == 200, weekly.text
        assert ids["source_18"] in weekly.json()["my_session_ids"]
        assert ids["target_18"] not in weekly.json()["my_session_ids"]
        assert ids["target_19"] in weekly.json()["my_session_ids"]
        upcoming = client.get("/schedule/upcoming", headers=headers)
        assert upcoming.status_code == 200, upcoming.text
        assert upcoming.json()["topic"] == "target_19"

        rejected = client.put(f'{TEMPORARY_URL}/{source["original_session_id"]}', headers=headers, json=stale)
        assert rejected.status_code == 409, rejected.text
        assert rejected.json()["detail"]["code"] == "SOURCE_CHANGED"
        options = client.get(TEMPORARY_URL + "/options", headers=headers)
        assert options.status_code == 200, options.text
        assert options.json()["source"]["teaching_week"] == 19
        assert ids["alternative_19"] in {option["session_id"] for option in options.json()["options"]}
        assert ids["alternative_18"] not in {option["session_id"] for option in options.json()["options"]}

    with Session(schedule_engine) as db:
        assert db.get(SessionsTransfer, (student_id, ids["target_18"])) is None
        assert db.get(SessionAttendance, (ids["source_18"], student_id)) is not None


@pytest.mark.parametrize("already_changed_temporarily", [False, True])
def test_late_higher_week_moves_new_class_to_next_unstudied_week(
    schedule_engine, seed, open_api, already_changed_temporarily,
):
    ids = seed(schedule_engine)
    student_id = ids["students"][0]
    headers = auth(student_id)
    with Session(schedule_engine) as db:
        starts = {
            "source_18": datetime(2026, 11, 19, 7, 30),
            "source_19": datetime(2026, 11, 20, 7, 30),
            "target_18": datetime(2026, 11, 20, 18),
            "target_19": datetime(2026, 11, 21, 14),
            "alternative_18": datetime(2026, 11, 21, 7, 30),
            "alternative_19": datetime(2026, 11, 21, 18),
        }
        for name, starts_at in starts.items():
            session = db.get(ClassSession, ids[name])
            session.starts_at = starts_at
            session.ends_at = starts_at + timedelta(hours=3)
        next_session = ClassSession(
            class_id=ids["target"], teaching_week=20, topic="target_20",
            starts_at=datetime(2026, 11, 22, 18), ends_at=datetime(2026, 11, 22, 21),
        )
        db.add(next_session)
        db.flush()
        next_id = next_session.id
        db.commit()

    with open_api(schedule_engine) as client:
        _, choice = get_choice(client, headers, ids["target"])
        assert choice["expected_first_session"]["teaching_week"] == 18
        switched = client.post(URL, headers=headers, json=choice)
        assert switched.status_code == 200, switched.text
        source, stale = get_temporary_choice(client, headers, ids["alternative_18"])
        endpoint = f'{TEMPORARY_URL}/{source["original_session_id"]}'
        if already_changed_temporarily:
            changed = client.put(endpoint, headers=headers, json=stale)
            assert changed.status_code == 200, changed.text
            _, stale = get_temporary_choice(client, headers, ids["target_18"])

        with Session(schedule_engine) as db:
            db.add(SessionAttendance(student_id=student_id, session_id=ids["source_19"]))
            db.commit()

        weekly = client.get("/schedule/weekly", headers=headers, params={"week_start": NOW.date().isoformat()})
        assert weekly.status_code == 200, weekly.text
        assert {ids["source_19"], next_id} <= set(weekly.json()["my_session_ids"])
        assert not {ids["target_18"], ids["target_19"], ids["alternative_18"]} & set(weekly.json()["my_session_ids"])
        assert ids["target_18"] not in weekly.json()["transferred_session_ids"]

        upcoming = client.get("/schedule/upcoming", headers=headers)
        assert upcoming.status_code == 200, upcoming.text
        assert upcoming.json()["topic"] == "target_20"
        temporary = client.get(TEMPORARY_URL + "/options", headers=headers)
        assert temporary.status_code == 200, temporary.text
        assert temporary.json()["source"]["current_session_id"] == next_id
        rejected = client.put(endpoint, headers=headers, json=stale)
        assert rejected.status_code == 409, rejected.text
        assert rejected.json()["detail"]["code"] == "SOURCE_CHANGED"


def test_allow_transfer_when_destination_has_no_schedule(schedule_engine, seed, open_api):
    ids = seed(schedule_engine)
    headers = auth(ids["students"][0])
    with Session(schedule_engine) as db:
        db.execute(delete(ClassSession).where(ClassSession.class_id == ids["target"]))
        db.commit()
    with open_api(schedule_engine) as client:
        _, choice = get_choice(client, headers, ids["target"])
        assert choice["expected_first_session"] is None
        response = client.post(URL, headers=headers, json=choice)
        assert response.status_code == 200, response.text
        assert response.json()["first_session"] is None
        assert client.get("/schedule/upcoming", headers=headers).json() is None
        assert client.get(URL + "/options", headers=headers).json()["current_class"]["class_id"] == ids["target"]


def test_require_reconfirmation_if_first_session_reaches_end(schedule_engine, seed, open_api, monkeypatch):
    ids = seed(schedule_engine)
    headers = auth(ids["students"][0])
    with open_api(schedule_engine) as client:
        _, choice = get_choice(client, headers, ids["target"])
        monkeypatch.setattr(schedule_service, "schedule_now", lambda: NOW + timedelta(hours=2))
        response = client.post(URL, headers=headers, json=choice)
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "FIRST_SESSION_CHANGED"
        assert response.json()["detail"]["first_session"]["session_id"] == ids["target_19"]
        assert client.get(URL + "/options", headers=headers).json()["current_class"]["class_id"] == ids["source"]


@pytest.mark.skipif(not MYSQL_ENABLED, reason="requires migrated local MySQL")
def test_two_students_compete_for_last_seat_on_mysql(seed, open_api, monkeypatch):
    assert local_engine.dialect.name == "mysql"
    ids = seed(local_engine, capacity=1, students=2)
    barrier = Barrier(2, timeout=10)
    lock_classes = PermanentTransferRepository.lock_classes

    def contend(repository, class_ids):
        barrier.wait()
        return lock_classes(repository, class_ids)

    monkeypatch.setattr(PermanentTransferRepository, "lock_classes", contend)
    with open_api(local_engine) as client:
        headers = [auth(student_id) for student_id in ids["students"]]
        choices = [get_choice(client, header, ids["target"])[1] for header in headers]

        def confirm(index):
            return client.post(URL, headers=headers[index], json=choices[index])

        with ThreadPoolExecutor(max_workers=2) as workers:
            responses = list(workers.map(confirm, range(2)))
        assert sorted(response.status_code for response in responses) == [200, 409]
        loser = next(index for index, response in enumerate(responses) if response.status_code == 409)
        assert responses[loser].json()["detail"]["code"] == "CLASS_FULL"
        assert client.get(URL + "/options", headers=headers[loser]).json()["current_class"]["class_id"] == ids["source"]

    with Session(local_engine) as db:
        active_target_count = db.scalar(
            select(func.count(ClassEnrollment.id)).where(
                ClassEnrollment.class_id == ids["target"], ClassEnrollment.ends_at.is_(None)
            )
        )
        assert active_target_count == 1
