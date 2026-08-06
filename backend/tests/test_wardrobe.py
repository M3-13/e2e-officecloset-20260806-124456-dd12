import io
import os
import os.path
import uuid

import pytest
from fastapi.testclient import TestClient
from jose import jwt as jose_jwt

from main import app
from models import User
from wardrobe.service import UPLOADS_DIR, _check_magic_bytes


def _create_jpeg_bytes() -> bytes:
    return b"\xff\xd8\xff\xe0" + b"\x00" * 100


def _create_png_bytes() -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


def _create_webp_bytes() -> bytes:
    header = b"RIFF"
    size = (100).to_bytes(4, "little")
    webp = b"WEBP"
    return header + size + webp + b"\x00" * 100


def _create_user_and_token(db_session, email_prefix: str = "wardrobe") -> tuple[int, str]:
    email = f"{email_prefix}-{uuid.uuid4().hex}@example.com"
    user = User(email=email, hashed_password="dummy-hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = jose_jwt.encode(
        {"sub": str(user.id), "exp": 9999999999},
        os.environ["JWT_SECRET"],
        algorithm="HS256",
    )
    return user.id, token


@pytest.fixture
def auth_headers() -> dict:
    from database import SessionLocal

    db = SessionLocal()
    try:
        _, token = _create_user_and_token(db)
        return {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Service-layer tests
# ---------------------------------------------------------------------------


class TestMagicBytes:
    def test_jpeg_magic_bytes(self) -> None:
        data = _create_jpeg_bytes()
        ext = _check_magic_bytes(data)
        assert ext == ".jpg"

    def test_png_magic_bytes(self) -> None:
        data = _create_png_bytes()
        ext = _check_magic_bytes(data)
        assert ext == ".png"

    def test_webp_magic_bytes(self) -> None:
        data = _create_webp_bytes()
        ext = _check_magic_bytes(data)
        assert ext == ".webp"

    def test_non_image_rejected(self) -> None:
        assert _check_magic_bytes(b"not an image at all") is None

    def test_empty_data_rejected(self) -> None:
        assert _check_magic_bytes(b"") is None

    def test_too_short_data_rejected(self) -> None:
        assert _check_magic_bytes(b"AB") is None


class TestCrudService:
    def test_create_and_get_item(self) -> None:
        from database import Base, SessionLocal, engine
        from wardrobe.service import (
            create_item as svc_create,
        )
        from wardrobe.service import (
            get_item as svc_get,
        )
        from wardrobe.service import (
            get_items as svc_list,
        )

        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            _, _token = _create_user_and_token(db, "crud")
            user = db.query(User).order_by(User.id.desc()).first()
            jpeg = _create_jpeg_bytes()
            fake_file = io.BytesIO(jpeg)
            fake_file.name = "test.jpg"

            class FakeUploadFile:
                file = fake_file
                filename = "test.jpg"

            item = svc_create(
                db,
                user,
                name="Test Shirt",
                category="top",
                color="red",
                image_file=FakeUploadFile(),
            )
            assert item.id > 0
            assert item.name == "Test Shirt"
            assert item.image_filename is not None

            result = svc_get(db, user, item.id)
            assert result.name == "Test Shirt"
            assert result.image_url == f"/api/wardrobe/images/{item.image_filename}"

            items = svc_list(db, user)
            assert len(items) >= 1
            found = [i for i in items if i.id == item.id]
            assert len(found) == 1

            svc_list(db, user, category_filter="top")
            svc_list(db, user, category_filter="dress")
        finally:
            db.close()

    def test_get_item_not_found(self) -> None:
        from database import Base, SessionLocal, engine
        from wardrobe.service import get_item as svc_get

        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            _, _token = _create_user_and_token(db, "nf")
            user = db.query(User).order_by(User.id.desc()).first()
            with pytest.raises(LookupError, match="Item not found"):
                svc_get(db, user, 99999)
        finally:
            db.close()

    def test_delete_item_removes_image(self) -> None:
        from database import Base, SessionLocal, engine
        from wardrobe.service import create_item as svc_create
        from wardrobe.service import delete_item as svc_delete

        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            _, _token = _create_user_and_token(db, "del")
            user = db.query(User).order_by(User.id.desc()).first()
            jpeg = _create_jpeg_bytes()
            fake_file = io.BytesIO(jpeg)
            fake_file.name = "test.jpg"

            class FakeUploadFile:
                file = fake_file
                filename = "test.jpg"

            item = svc_create(
                db, user, name="To Delete", category="shoes", image_file=FakeUploadFile()
            )
            filename = item.image_filename
            assert filename is not None
            filepath = os.path.join(UPLOADS_DIR, filename)
            assert os.path.isfile(filepath)

            svc_delete(db, user, item.id)
            assert not os.path.isfile(filepath)
        finally:
            db.close()

    def test_update_item_replaces_image(self) -> None:
        from database import Base, SessionLocal, engine
        from wardrobe.service import create_item as svc_create
        from wardrobe.service import update_item as svc_update

        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            _, _token = _create_user_and_token(db, "upd")
            user = db.query(User).order_by(User.id.desc()).first()
            jpeg = _create_jpeg_bytes()
            png = _create_png_bytes()

            class FakeUploadFile:
                def __init__(self, data: bytes, name: str):
                    self.file = io.BytesIO(data)
                    self.filename = name

            item = svc_create(
                db, user, name="Old", category="top", image_file=FakeUploadFile(jpeg, "old.jpg")
            )
            old_filename = item.image_filename
            assert old_filename is not None
            old_path = os.path.join(UPLOADS_DIR, old_filename)
            assert os.path.isfile(old_path)

            result = svc_update(
                db, user, item.id, name="New", image_file=FakeUploadFile(png, "new.png")
            )
            assert result.name == "New"
            assert result.image_url is not None
            new_filename = result.image_url.rsplit("/", 1)[-1]

            assert new_filename != old_filename
            assert not os.path.isfile(old_path)
            assert os.path.isfile(os.path.join(UPLOADS_DIR, new_filename))
        finally:
            db.close()

    def test_update_item_partial(self) -> None:
        from database import Base, SessionLocal, engine
        from wardrobe.service import create_item as svc_create
        from wardrobe.service import update_item as svc_update

        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            _, _token = _create_user_and_token(db, "part")
            user = db.query(User).order_by(User.id.desc()).first()

            class FakeUploadFile:
                def __init__(self, data: bytes, name: str):
                    self.file = io.BytesIO(data)
                    self.filename = name

            item = svc_create(
                db,
                user,
                name="Original",
                category="accessory",
                color="gold",
                notes="fancy",
                image_file=FakeUploadFile(_create_jpeg_bytes(), "o.jpg"),
            )
            result = svc_update(db, user, item.id, color="silver")
            assert result.name == "Original"
            assert result.color == "silver"
            assert result.notes == "fancy"
            assert result.image_url is not None
        finally:
            db.close()


# ---------------------------------------------------------------------------
# Router-level / integration tests
# ---------------------------------------------------------------------------


class TestWardrobeRouter:
    def test_list_items_requires_auth(self) -> None:
        with TestClient(app) as client:
            resp = client.get("/api/wardrobe/items")
            assert resp.status_code == 401

    def test_create_item_requires_auth(self) -> None:
        with TestClient(app) as client:
            resp = client.post("/api/wardrobe/items", data={"name": "x", "category": "top"})
            assert resp.status_code == 401

    def test_create_and_list_item(self) -> None:
        with TestClient(app) as client:
            from database import SessionLocal

            db = SessionLocal()
            try:
                _, token = _create_user_and_token(db, "router-create")
                headers = {"Authorization": f"Bearer {token}"}

                jpeg = _create_jpeg_bytes()
                resp = client.post(
                    "/api/wardrobe/items",
                    data={"name": "Schwarzes Kleid", "category": "dress"},
                    files={"image": ("dress.jpg", io.BytesIO(jpeg), "image/jpeg")},
                    headers=headers,
                )
                assert resp.status_code == 201, resp.text
                body = resp.json()
                assert body["name"] == "Schwarzes Kleid"
                assert body["category"] == "dress"
                assert body["image_url"] is not None
                assert body["image_url"].startswith("/api/wardrobe/images/")

                resp2 = client.get("/api/wardrobe/items", headers=headers)
                assert resp2.status_code == 200
                items = resp2.json()
                assert len(items) >= 1
                found = [i for i in items if i["name"] == "Schwarzes Kleid"]
                assert len(found) == 1
                assert found[0]["image_url"] == body["image_url"]

                image_url = body["image_url"]
                resp3 = client.get(image_url, headers=headers)
                assert resp3.status_code == 200
                assert resp3.content == jpeg
            finally:
                db.close()

    def test_get_item_by_id(self) -> None:
        with TestClient(app) as client:
            from database import SessionLocal

            db = SessionLocal()
            try:
                _, token = _create_user_and_token(db, "router-get")
                headers = {"Authorization": f"Bearer {token}"}
                png = _create_png_bytes()
                resp = client.post(
                    "/api/wardrobe/items",
                    data={"name": "Blue Shoes", "category": "shoes", "color": "blue"},
                    files={"image": ("shoes.png", io.BytesIO(png), "image/png")},
                    headers=headers,
                )
                assert resp.status_code == 201
                item_id = resp.json()["id"]

                resp2 = client.get(f"/api/wardrobe/items/{item_id}", headers=headers)
                assert resp2.status_code == 200
                assert resp2.json()["name"] == "Blue Shoes"
            finally:
                db.close()

    def test_get_item_not_found(self) -> None:
        with TestClient(app) as client:
            from database import SessionLocal

            db = SessionLocal()
            try:
                _, token = _create_user_and_token(db, "router-404")
                headers = {"Authorization": f"Bearer {token}"}
                resp = client.get("/api/wardrobe/items/99999", headers=headers)
                assert resp.status_code == 404
            finally:
                db.close()

    def test_delete_item(self) -> None:
        with TestClient(app) as client:
            from database import SessionLocal

            db = SessionLocal()
            try:
                _, token = _create_user_and_token(db, "router-del")
                headers = {"Authorization": f"Bearer {token}"}
                png = _create_png_bytes()
                resp = client.post(
                    "/api/wardrobe/items",
                    data={"name": "Delete Me", "category": "accessory"},
                    files={"image": ("x.png", io.BytesIO(png), "image/png")},
                    headers=headers,
                )
                item_id = resp.json()["id"]
                filename = resp.json()["image_url"].rsplit("/", 1)[-1]

                resp2 = client.delete(f"/api/wardrobe/items/{item_id}", headers=headers)
                assert resp2.status_code == 204

                filepath = os.path.join(UPLOADS_DIR, filename)
                assert not os.path.isfile(filepath)
            finally:
                db.close()

    def test_delete_item_not_found(self) -> None:
        with TestClient(app) as client:
            from database import SessionLocal

            db = SessionLocal()
            try:
                _, token = _create_user_and_token(db, "router-del-nf")
                headers = {"Authorization": f"Bearer {token}"}
                resp = client.delete("/api/wardrobe/items/99999", headers=headers)
                assert resp.status_code == 404
            finally:
                db.close()

    def test_update_item(self) -> None:
        with TestClient(app) as client:
            from database import SessionLocal

            db = SessionLocal()
            try:
                _, token = _create_user_and_token(db, "router-upd")
                headers = {"Authorization": f"Bearer {token}"}
                png = _create_png_bytes()
                resp = client.post(
                    "/api/wardrobe/items",
                    data={"name": "Old Name", "category": "top", "color": "red"},
                    files={"image": ("old.png", io.BytesIO(png), "image/png")},
                    headers=headers,
                )
                item_id = resp.json()["id"]
                old_filename = resp.json()["image_url"].rsplit("/", 1)[-1]

                jpeg = _create_jpeg_bytes()
                resp2 = client.put(
                    f"/api/wardrobe/items/{item_id}",
                    data={"name": "New Name", "color": "blue"},
                    files={"image": ("new.jpg", io.BytesIO(jpeg), "image/jpeg")},
                    headers=headers,
                )
                assert resp2.status_code == 200
                body = resp2.json()
                assert body["name"] == "New Name"
                assert body["color"] == "blue"
                new_filename = body["image_url"].rsplit("/", 1)[-1]
                assert new_filename != old_filename
                assert not os.path.isfile(os.path.join(UPLOADS_DIR, old_filename))
                assert os.path.isfile(os.path.join(UPLOADS_DIR, new_filename))
            finally:
                db.close()

    def test_update_item_not_found(self) -> None:
        with TestClient(app) as client:
            from database import SessionLocal

            db = SessionLocal()
            try:
                _, token = _create_user_and_token(db, "router-upd-nf")
                headers = {"Authorization": f"Bearer {token}"}
                resp = client.put(
                    "/api/wardrobe/items/99999",
                    data={"name": "x"},
                    headers=headers,
                )
                assert resp.status_code == 404
            finally:
                db.close()

    def test_category_filter(self) -> None:
        with TestClient(app) as client:
            from database import SessionLocal

            db = SessionLocal()
            try:
                _, token = _create_user_and_token(db, "router-cat")
                headers = {"Authorization": f"Bearer {token}"}
                png = _create_png_bytes()
                client.post(
                    "/api/wardrobe/items",
                    data={"name": "Shirt A", "category": "top"},
                    files={"image": ("a.png", io.BytesIO(png), "image/png")},
                    headers=headers,
                )
                client.post(
                    "/api/wardrobe/items",
                    data={"name": "Pants B", "category": "bottom"},
                    files={"image": ("b.png", io.BytesIO(png), "image/png")},
                    headers=headers,
                )

                resp = client.get("/api/wardrobe/items?category=top", headers=headers)
                assert resp.status_code == 200
                items = resp.json()
                for item in items:
                    assert item["category"] == "top"

                resp2 = client.get("/api/wardrobe/items?category=dress", headers=headers)
                assert resp2.status_code == 200
                items2 = resp2.json()
                for item in items2:
                    assert item["category"] == "dress"
            finally:
                db.close()

    def test_magic_bytes_rejection(self) -> None:
        with TestClient(app) as client:
            from database import SessionLocal

            db = SessionLocal()
            try:
                _, token = _create_user_and_token(db, "router-magic")
                headers = {"Authorization": f"Bearer {token}"}
                resp = client.post(
                    "/api/wardrobe/items",
                    data={"name": "Bad File", "category": "top"},
                    files={"image": ("bad.txt", io.BytesIO(b"not an image"), "text/plain")},
                    headers=headers,
                )
                assert resp.status_code == 400
                assert (
                    "JPEG" in resp.json()["detail"]
                    or "PNG" in resp.json()["detail"]
                    or "WebP" in resp.json()["detail"]
                )
            finally:
                db.close()

    def test_size_rejection(self) -> None:
        import wardrobe.service as svc_mod

        original = svc_mod.MAX_IMAGE_SIZE
        try:
            svc_mod.MAX_IMAGE_SIZE = 10
            with TestClient(app) as client:
                from database import SessionLocal

                db = SessionLocal()
                try:
                    _, token = _create_user_and_token(db, "router-size")
                    headers = {"Authorization": f"Bearer {token}"}
                    resp = client.post(
                        "/api/wardrobe/items",
                        data={"name": "Big File", "category": "top"},
                        files={
                            "image": ("big.jpg", io.BytesIO(_create_jpeg_bytes()), "image/jpeg")
                        },
                        headers=headers,
                    )
                    assert resp.status_code == 413
                finally:
                    db.close()
        finally:
            svc_mod.MAX_IMAGE_SIZE = original

    def test_image_endpoint_requires_auth(self) -> None:
        with TestClient(app) as client:
            resp = client.get("/api/wardrobe/images/test.png")
            assert resp.status_code == 401

    def test_image_endpoint_404(self) -> None:
        with TestClient(app) as client:
            from database import SessionLocal

            db = SessionLocal()
            try:
                _, token = _create_user_and_token(db, "router-img404")
                headers = {"Authorization": f"Bearer {token}"}
                resp = client.get("/api/wardrobe/images/nonexistent_abc123.png", headers=headers)
                assert resp.status_code == 404
            finally:
                db.close()

    def test_traversal_filename_rejected(self) -> None:
        with TestClient(app) as client:
            from database import SessionLocal

            db = SessionLocal()
            try:
                _, token = _create_user_and_token(db, "router-trav")
                headers = {"Authorization": f"Bearer {token}"}
                resp = client.get("/api/wardrobe/images/evil.png", headers=headers)
                assert resp.status_code == 404
            finally:
                db.close()
