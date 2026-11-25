from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.core.enums.user_role import UserRole
from app.core.security import create_access_token
from app.database.database import get_session_factory
from app.main import app
from app.models.exam import Exam, ExamPaper
from app.models.user import User


def authorization(user_id: int = 1) -> dict[str, str]:
    token = create_access_token({"id": user_id}, timedelta(minutes=5))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def draft_api(monkeypatch, sqlite_engine):
    with sqlite_engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA foreign_keys = ON")

    session_factory = sessionmaker(bind=sqlite_engine)
    with session_factory.begin() as db:
        for user_id, role in ((1, UserRole.TEACHER), (2, UserRole.TEACHER), (3, UserRole.STUDENT)):
            db.add(User(
                id=user_id,
                full_name=f"User {user_id}",
                phone_number=str(user_id),
                hashed_password="unused",
                role=role,
                is_active=True,
                must_change_password=False,
            ))
        db.flush()
        for paper_id, owner_id in ((11, 1), (22, 2)):
            db.add(ExamPaper(
                id=paper_id,
                created_by=owner_id,
                title=f"Đề {paper_id}",
                kind="structured",
                structure={},
                structure_hash="0" * 64,
                created_at=datetime(2026, 11, 25),
            ))

    monkeypatch.setitem(app.dependency_overrides, get_session_factory, lambda: session_factory)
    with TestClient(app) as client:
        yield client, session_factory


@pytest.fixture
def draft_request():
    return {
        "paper_id": 11,
        "title": "  Kiểm tra Toán 12  ",
        "description": "Chương đạo hàm",
        "opens_at": "2026-12-01T12:00:00Z",
        "closes_at": "2026-12-01T21:00:00",
        "duration_minutes": 90,
    }


def test_create_draft_links_existing_paper_and_commits_before_returning(draft_api, draft_request):
    client, session_factory = draft_api
    response = client.post("/teacher/exams", json=draft_request, headers=authorization())

    assert response.status_code == 201
    with session_factory() as db:
        exam = db.scalars(select(Exam)).one()
        assert response.json() == {"exam_id": exam.id}
        assert exam.paper_id == 11
        assert exam.created_by == 1
        assert exam.status == "draft"
        assert exam.title == "Kiểm tra Toán 12"
        assert exam.description == "Chương đạo hàm"
        assert exam.opens_at == datetime(2026, 12, 1, 19)
        assert exam.closes_at == datetime(2026, 12, 1, 21)
        assert exam.duration_minutes == 90
        assert db.scalar(select(func.count()).select_from(ExamPaper)) == 2


@pytest.mark.parametrize("user_id, overrides, expected_status", [
    (1, {"paper_id": 22}, 404),
    (1, {"paper_id": 999}, 404),
    (3, {}, 403),
    (1, {"paper_id": 0}, 422),
    (1, {"title": "  "}, 422),
    (1, {"duration_minutes": 0}, 422),
    (1, {"closes_at": "2026-12-01T18:00:00+07:00"}, 422),
    (1, {"closes_at": "2026-12-01T19:00:00.500+07:00"}, 422),
    (1, {"schedule_inputs": {"opens_at": "2026-12-01T"}}, 422),
    (1, {"opens_at": None, "schedule_inputs": {"opens_at": "2026-02-30T"}}, 422),
])
def test_rejected_request_leaves_no_exam(draft_api, draft_request, user_id, overrides, expected_status):
    client, session_factory = draft_api
    response = client.post("/teacher/exams", json={**draft_request, **overrides}, headers=authorization(user_id))

    assert response.status_code == expected_status
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(Exam)) == 0


def test_new_blank_draft_can_be_reopened_updated_and_listed_with_same_id(draft_api):
    client, session_factory = draft_api
    key = "b93e427f-1447-4000-8000-62a100000001"
    headers = authorization()
    created = client.post("/teacher/exams", json={"autosave_key": key}, headers=headers)
    assert created.status_code == 201
    path = f"/teacher/exams/{created.json()['exam_id']}"
    draft = client.get(path, headers=headers).json()
    assert draft["paper_id"] is None and draft["opens_at"] is None
    assert client.get(f"/teacher/exams/drafts/by-key/{key}", headers=headers).json() == draft

    payload = {"title": "Đang chuẩn bị", "opens_at": "2026-12-01T19:00:00", "version": draft["version"]}
    updated = client.put(path, headers=headers, json=payload)
    assert updated.status_code == 200
    assert updated.json()["opens_at"] == "2026-12-01T19:00:00+07:00"
    assert updated.json()["closes_at"] is None
    assert client.put(path, headers=headers, json=payload).status_code == 409
    assert client.post("/teacher/exams", json={"autosave_key": key}, headers=headers).json() == created.json()
    assert client.get("/teacher/exams/drafts", headers=headers).json() == [updated.json()]
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(Exam)) == 1


def test_delete_clears_the_draft_and_late_writes_do_not_restore_it(draft_api):
    client, session_factory = draft_api
    key = "b93e427f-1447-4000-8000-62a100000002"
    payload = {"autosave_key": key, "title": "Bản sẽ xóa", "schedule_inputs": {"opens_at": "2026-12-01T"}}
    headers = authorization()
    response = client.post("/teacher/exams", json=payload, headers=headers)
    exam_id = response.json()["exam_id"]
    path = f"/teacher/exams/{exam_id}"
    assert client.delete(path, headers=authorization(2)).status_code == 404
    assert client.get(path, headers=authorization(2)).status_code == 404
    assert client.put(path, headers=authorization(2), json={"version": 1}).status_code == 404
    assert client.delete(path, headers=headers).status_code == 204
    assert client.get("/teacher/exams/drafts", headers=headers).json() == []
    assert client.put(path, headers=headers, json={"title": "Lưu muộn", "version": 1}).status_code == 410
    assert client.post("/teacher/exams", json=payload, headers=headers).status_code == 410
    with session_factory() as db:
        deleted = db.get(Exam, exam_id)
        assert deleted.discarded_at is not None and deleted.title is None
        assert deleted.schedule_inputs is None


def test_partial_schedule_survives_reopen_and_can_be_completed(draft_api):
    client, _ = draft_api
    headers = authorization()
    schedule_inputs = {"opens_at": "2026-12-01T", "closes_at": "T20:00"}
    created = client.post("/teacher/exams", headers=headers, json={"schedule_inputs": schedule_inputs})
    assert created.status_code == 201
    path = f"/teacher/exams/{created.json()['exam_id']}"

    draft = client.get(path, headers=headers).json()
    assert draft["schedule_inputs"] == schedule_inputs
    assert draft["opens_at"] is None and draft["closes_at"] is None

    updated = client.put(path, headers=headers, json={
        "version": draft["version"], "opens_at": "2026-12-01T18:00",
        "schedule_inputs": {"closes_at": "T20:00"},
    })
    assert updated.status_code == 200
    assert updated.json()["opens_at"] == "2026-12-01T18:00:00+07:00"
    assert updated.json()["schedule_inputs"] == {"closes_at": "T20:00"}


def test_paper_picker_returns_only_the_teachers_papers(draft_api):
    client, _ = draft_api
    response = client.get("/teacher/exam-bank/papers", headers=authorization())
    assert response.status_code == 200
    assert response.json() == [{"paper_id": 11, "title": "Đề 11"}]
