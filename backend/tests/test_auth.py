import os
import tempfile
import uuid

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(
    tempfile.gettempdir(), "office_crew_auth_test.db"
).replace("\\", "/")
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only"

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database import SessionLocal
from main import app
from models import ClothingItem, User

_unique = uuid.uuid4().hex[:8]


def _email() -> str:
    return f"test-{uuid.uuid4().hex}@example.com"


def test_register_success() -> None:
    with TestClient(app) as client:
        resp = client.post(
            "/api/auth/register",
            json={"email": _email(), "password": "secure123"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] > 0
        assert "@" in body["email"]
        assert "password" not in body
        assert "hashed_password" not in body


def test_register_duplicate_email_returns_409() -> None:
    email = _email()
    with TestClient(app) as client:
        resp1 = client.post(
            "/api/auth/register",
            json={"email": email, "password": "secure123"},
        )
        assert resp1.status_code == 201
        resp2 = client.post(
            "/api/auth/register",
            json={"email": email, "password": "different"},
        )
        assert resp2.status_code == 409
        assert resp2.json()["detail"] == "Email already registered"


def test_login_success() -> None:
    email = _email()
    password = "secure123"
    with TestClient(app) as client:
        reg = client.post(
            "/api/auth/register",
            json={"email": email, "password": password},
        )
        assert reg.status_code == 201

        resp = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["access_token"].startswith("ey")


def test_login_wrong_password_returns_401() -> None:
    email = _email()
    with TestClient(app) as client:
        reg = client.post(
            "/api/auth/register",
            json={"email": email, "password": "secret"},
        )
        assert reg.status_code == 201

        resp = client.post(
            "/api/auth/login",
            json={"email": email, "password": "wrong"},
        )
        assert resp.status_code == 401


def test_login_nonexistent_email_returns_401() -> None:
    with TestClient(app) as client:
        resp = client.post(
            "/api/auth/login",
            json={"email": _email(), "password": "whatever"},
        )
        assert resp.status_code == 401


def test_get_me_authenticated() -> None:
    email = _email()
    password = "secure123"
    with TestClient(app) as client:
        reg = client.post(
            "/api/auth/register",
            json={"email": email, "password": password},
        )
        assert reg.status_code == 201

        login_resp = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        token = login_resp.json()["access_token"]

        resp = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == email
        assert "password" not in body
        assert "hashed_password" not in body


def test_get_me_unauthenticated_returns_401() -> None:
    with TestClient(app) as client:
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401


def test_delete_me_authenticated() -> None:
    email = _email()
    password = "secure123"
    with TestClient(app) as client:
        reg = client.post(
            "/api/auth/register",
            json={"email": email, "password": password},
        )
        assert reg.status_code == 201

        login_resp = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        token = login_resp.json()["access_token"]

        resp = client.delete(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204
        assert resp.content == b""

        me_resp = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 401


def test_delete_me_unauthenticated_returns_401() -> None:
    with TestClient(app) as client:
        resp = client.delete("/api/auth/me")
        assert resp.status_code == 401


def test_bcrypt_hash_format_ac10() -> None:
    email = _email()
    with TestClient(app) as client:
        resp = client.post(
            "/api/auth/register",
            json={"email": email, "password": "test1234"},
        )
        assert resp.status_code == 201

        db: Session = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            assert user is not None
            pw = user.hashed_password
            assert pw.startswith("$2b$") or pw.startswith("$2a$"), (
                f"hash does not start with $2b$ or $2a$: {pw[:10]}..."
            )
            assert len(pw) >= 50, f"hash too short: {len(pw)} chars"
        finally:
            db.query(User).filter(User.email == email).delete()
            db.commit()
            db.close()


def test_delete_account_removes_images_ac21() -> None:
    os.makedirs("uploads", exist_ok=True)
    filename = f"ac21-test-{uuid.uuid4().hex}.png"
    filepath = os.path.join("uploads", filename)
    with open(filepath, "wb") as f:
        f.write(b"fake image data")

    email = _email()
    password = "secure123"

    with TestClient(app) as client:
        reg = client.post(
            "/api/auth/register",
            json={"email": email, "password": password},
        )
        assert reg.status_code == 201
        user_id = reg.json()["id"]

        db: Session = SessionLocal()
        try:
            item = ClothingItem(
                user_id=user_id,
                name="Test Item",
                category="top",
                image_filename=filename,
            )
            db.add(item)
            db.commit()
        finally:
            db.close()

        login_resp = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        token = login_resp.json()["access_token"]

        del_resp = client.delete(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert del_resp.status_code == 204

        assert not os.path.exists(filepath), f"Image file {filename} should have been deleted"


def test_delete_account_cascade_removes_items() -> None:
    email = _email()
    password = "secure123"

    with TestClient(app) as client:
        reg = client.post(
            "/api/auth/register",
            json={"email": email, "password": password},
        )
        assert reg.status_code == 201
        user_id = reg.json()["id"]

        db: Session = SessionLocal()
        try:
            item1 = ClothingItem(user_id=user_id, name="Shirt", category="top")
            item2 = ClothingItem(user_id=user_id, name="Pants", category="bottom")
            db.add_all([item1, item2])
            db.commit()
        finally:
            db.close()

        login_resp = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        token = login_resp.json()["access_token"]

        del_resp = client.delete(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert del_resp.status_code == 204

        db = SessionLocal()
        try:
            remaining = db.query(ClothingItem).filter(ClothingItem.user_id == user_id).count()
            assert remaining == 0, "Clothing items should be cascade-deleted"
        finally:
            db.close()


def test_login_token_can_be_used_for_protected_route() -> None:
    email = _email()
    password = "secure123"
    with TestClient(app) as client:
        reg = client.post(
            "/api/auth/register",
            json={"email": email, "password": password},
        )
        assert reg.status_code == 201

        login_resp = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        token = login_resp.json()["access_token"]

        me_resp = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == email
