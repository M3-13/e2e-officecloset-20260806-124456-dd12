import contextlib
import os
import uuid

os.environ["DATABASE_URL"] = "sqlite:///./test_run.db"
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only"

from fastapi.testclient import TestClient
from jose import jwt as jose_jwt

from main import app


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_cors_allowed_origin() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:5173"},
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_disallowed_origin_not_reflected() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/health",
            headers={"Origin": "http://evil.example.com"},
        )
        assert response.status_code == 200
        acao = response.headers.get("access-control-allow-origin")
        assert acao != "http://evil.example.com"
        assert acao != "*"


def test_cors_no_wildcard() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:5173"},
        )
        assert response.headers["access-control-allow-origin"] != "*"


def test_protected_images_401_without_token() -> None:
    with TestClient(app) as client:
        response = client.get("/api/wardrobe/images/test.png")
        assert response.status_code == 401


def test_protected_images_200_with_valid_token() -> None:
    os.makedirs("uploads", exist_ok=True)
    test_content = b"fake image binary"
    filepath = "uploads/test_auth_image.png"
    with open(filepath, "wb") as f:
        f.write(test_content)

    from database import SessionLocal
    from models import User

    email = f"img-test-{uuid.uuid4().hex}@example.com"
    user_id: int | None = None

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            db = SessionLocal()
            user = User(email=email, hashed_password="dummy")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id
            db.close()

            token = jose_jwt.encode(
                {"sub": str(user_id), "exp": 9999999999},
                os.environ["JWT_SECRET"],
                algorithm="HS256",
            )
            response = client.get(
                "/api/wardrobe/images/test_auth_image.png",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200
            assert response.content == test_content

            db = SessionLocal()
            db.query(User).filter(User.id == user_id).delete()
            db.commit()
            db.close()
    finally:
        with contextlib.suppress(OSError):
            os.remove(filepath)
        if user_id is not None:
            with contextlib.suppress(Exception):
                db = SessionLocal()
                db.query(User).filter(User.id == user_id).delete()
                db.commit()
                db.close()


def _delete_user_by_email(email: str) -> None:
    from database import SessionLocal
    from models import User

    with contextlib.suppress(Exception):
        db = SessionLocal()
        db.query(User).filter(User.email == email).delete()
        db.commit()
        db.close()


def test_500_handler_no_stacktrace() -> None:
    route_path = "/__test_raise_500"
    if not any(hasattr(r, "path") and r.path == route_path for r in app.routes):

        @app.get(route_path)
        async def _raise() -> dict:
            raise RuntimeError("secret details must be hidden")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(route_path)
        assert response.status_code == 500
        body = response.json()
        assert body == {"detail": "Internal server error"}
        assert "RuntimeError" not in str(body)
        assert "secret details" not in str(body)


def test_auth_register_route_exists() -> None:
    with TestClient(app) as client:
        resp = client.post("/api/auth/register", json={"email": "a@b.com", "password": "x"})
        assert resp.status_code != 404


def test_auth_login_route_exists() -> None:
    with TestClient(app) as client:
        resp = client.post("/api/auth/login", json={"email": "a@b.com", "password": "x"})
        assert resp.status_code != 404


def test_wardrobe_items_route_exists() -> None:
    with TestClient(app) as client:
        resp = client.get("/api/wardrobe/items")
        assert resp.status_code != 404


def test_wardrobe_images_route_exists() -> None:
    with TestClient(app) as client:
        resp = client.get("/api/wardrobe/images/test.png")
        assert resp.status_code != 404


def test_outfits_route_exists() -> None:
    with TestClient(app) as client:
        resp = client.get("/api/outfits")
        assert resp.status_code != 404
