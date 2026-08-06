import contextlib
import os
import uuid

os.environ["DATABASE_URL"] = "sqlite:///./test_run.db"
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only"

from fastapi.testclient import TestClient
from jose import jwt as jose_jwt

from database import Base, SessionLocal, engine
from main import app
from models import ClothingItem, User

Base.metadata.create_all(bind=engine)


def _make_token(user_id: int) -> str:
    return jose_jwt.encode(
        {"sub": str(user_id), "exp": 9999999999},
        os.environ["JWT_SECRET"],
        algorithm="HS256",
    )


def _create_user(email: str | None = None) -> User:
    if email is None:
        email = f"outfit-test-{uuid.uuid4().hex}@example.com"
    db = SessionLocal()
    user = User(email=email, hashed_password="dummy")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def _create_item(user: User, name: str = "Test Shirt") -> ClothingItem:
    db = SessionLocal()
    item = ClothingItem(
        user_id=user.id,
        name=name,
        category="top",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    db.close()
    return item


def _delete_user(user_id: int) -> None:
    with contextlib.suppress(Exception):
        db = SessionLocal()
        user = db.get(User, user_id)
        if user is not None:
            db.delete(user)
            db.commit()
        db.close()


def _delete_users(user_ids: list[int]) -> None:
    for uid in user_ids:
        _delete_user(uid)


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------


def test_create_outfit_returns_201_with_items() -> None:
    user = _create_user()
    item1 = _create_item(user, "Silk Blouse")
    item2 = _create_item(user, "Evening Gown")
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            resp = client.post(
                "/api/outfits",
                json={"name": "Abendlook", "item_ids": [item1.id, item2.id]},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 201
            body = resp.json()
            assert body["name"] == "Abendlook"
            assert len(body["items"]) == 2
            item_names = {it["name"] for it in body["items"]}
            assert item_names == {"Silk Blouse", "Evening Gown"}
            assert "id" in body
            assert "created_at" in body
    finally:
        _delete_user(user.id)


def test_create_outfit_unauthenticated_returns_401() -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.post(
            "/api/outfits",
            json={"name": "Test", "item_ids": [1]},
        )
        assert resp.status_code == 401


def test_create_outfit_with_foreign_item_returns_400() -> None:
    user_a = _create_user()
    user_b = _create_user()
    item_b = _create_item(user_b, "B's Item")
    token = _make_token(user_a.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            resp = client.post(
                "/api/outfits",
                json={"name": "Stolen", "item_ids": [item_b.id]},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 400
    finally:
        _delete_users([user_a.id, user_b.id])


def test_create_outfit_with_nonexistent_item_returns_400() -> None:
    user = _create_user()
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            resp = client.post(
                "/api/outfits",
                json={"name": "Ghost", "item_ids": [99999]},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 400
    finally:
        _delete_user(user.id)


def test_create_outfit_empty_items() -> None:
    user = _create_user()
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            resp = client.post(
                "/api/outfits",
                json={"name": "Empty Look", "item_ids": []},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 201
            body = resp.json()
            assert body["name"] == "Empty Look"
            assert body["items"] == []
    finally:
        _delete_user(user.id)


# ---------------------------------------------------------------------------
# LIST
# ---------------------------------------------------------------------------


def test_list_outfits_empty() -> None:
    user = _create_user()
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            resp = client.get(
                "/api/outfits",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            assert resp.json() == []
    finally:
        _delete_user(user.id)


def test_list_outfits_unauthenticated_returns_401() -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/api/outfits")
        assert resp.status_code == 401


def test_list_outfits_shows_created_outfits() -> None:
    user = _create_user()
    item1 = _create_item(user, "Hat")
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            resp = client.post(
                "/api/outfits",
                json={"name": "Hat Look", "item_ids": [item1.id]},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 201

            resp = client.get(
                "/api/outfits",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert len(body) == 1
            assert body[0]["name"] == "Hat Look"
            assert len(body[0]["items"]) == 1
            assert body[0]["items"][0]["name"] == "Hat"
    finally:
        _delete_user(user.id)


def test_list_outfits_scoped_to_user() -> None:
    user_a = _create_user()
    user_b = _create_user()
    item_a = _create_item(user_a, "A's Item")
    item_b = _create_item(user_b, "B's Item")
    token_a = _make_token(user_a.id)
    token_b = _make_token(user_b.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            client.post(
                "/api/outfits",
                json={"name": "A's Look", "item_ids": [item_a.id]},
                headers={"Authorization": f"Bearer {token_a}"},
            )
            client.post(
                "/api/outfits",
                json={"name": "B's Look", "item_ids": [item_b.id]},
                headers={"Authorization": f"Bearer {token_b}"},
            )

            resp = client.get(
                "/api/outfits",
                headers={"Authorization": f"Bearer {token_a}"},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert len(body) == 1
            assert body[0]["name"] == "A's Look"
    finally:
        _delete_users([user_a.id, user_b.id])


# ---------------------------------------------------------------------------
# GET single
# ---------------------------------------------------------------------------


def test_get_outfit_returns_200() -> None:
    user = _create_user()
    item = _create_item(user, "Scarf")
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            create_resp = client.post(
                "/api/outfits",
                json={"name": "Scarf Look", "item_ids": [item.id]},
                headers={"Authorization": f"Bearer {token}"},
            )
            outfit_id = create_resp.json()["id"]

            resp = client.get(
                f"/api/outfits/{outfit_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["name"] == "Scarf Look"
            assert len(body["items"]) == 1
            assert body["items"][0]["name"] == "Scarf"
    finally:
        _delete_user(user.id)


def test_get_outfit_not_found_returns_404() -> None:
    user = _create_user()
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            resp = client.get(
                "/api/outfits/99999",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 404
    finally:
        _delete_user(user.id)


def test_get_outfit_belongs_to_other_user_returns_404() -> None:
    user_a = _create_user()
    user_b = _create_user()
    item_a = _create_item(user_a, "A's Item")
    token_a = _make_token(user_a.id)
    token_b = _make_token(user_b.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            create_resp = client.post(
                "/api/outfits",
                json={"name": "A's Look", "item_ids": [item_a.id]},
                headers={"Authorization": f"Bearer {token_a}"},
            )
            outfit_id = create_resp.json()["id"]

            resp = client.get(
                f"/api/outfits/{outfit_id}",
                headers={"Authorization": f"Bearer {token_b}"},
            )
            assert resp.status_code == 404
    finally:
        _delete_users([user_a.id, user_b.id])


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------


def test_update_outfit_rename() -> None:
    user = _create_user()
    item = _create_item(user, "Watch")
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            create_resp = client.post(
                "/api/outfits",
                json={"name": "Old Name", "item_ids": [item.id]},
                headers={"Authorization": f"Bearer {token}"},
            )
            outfit_id = create_resp.json()["id"]

            resp = client.put(
                f"/api/outfits/{outfit_id}",
                json={"name": "New Name"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["name"] == "New Name"
            assert len(body["items"]) == 1
            assert body["items"][0]["name"] == "Watch"
    finally:
        _delete_user(user.id)


def test_update_outfit_replace_items() -> None:
    user = _create_user()
    item1 = _create_item(user, "Shoes")
    item2 = _create_item(user, "Dress")
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            create_resp = client.post(
                "/api/outfits",
                json={"name": "Look", "item_ids": [item1.id]},
                headers={"Authorization": f"Bearer {token}"},
            )
            outfit_id = create_resp.json()["id"]

            resp = client.put(
                f"/api/outfits/{outfit_id}",
                json={"item_ids": [item2.id, item1.id]},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert len(body["items"]) == 2
            assert body["items"][0]["name"] == "Dress"
            assert body["items"][1]["name"] == "Shoes"
    finally:
        _delete_user(user.id)


def test_update_outfit_not_found_returns_404() -> None:
    user = _create_user()
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            resp = client.put(
                "/api/outfits/99999",
                json={"name": "Ghost"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 404
    finally:
        _delete_user(user.id)


def test_update_outfit_unauthenticated_returns_401() -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.put(
            "/api/outfits/1",
            json={"name": "Test"},
        )
        assert resp.status_code == 401


def test_update_outfit_foreign_items_returns_400() -> None:
    user_a = _create_user()
    user_b = _create_user()
    item_a = _create_item(user_a, "A's Item")
    item_b = _create_item(user_b, "B's Item")
    token_a = _make_token(user_a.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            create_resp = client.post(
                "/api/outfits",
                json={"name": "A's Look", "item_ids": [item_a.id]},
                headers={"Authorization": f"Bearer {token_a}"},
            )
            outfit_id = create_resp.json()["id"]

            resp = client.put(
                f"/api/outfits/{outfit_id}",
                json={"item_ids": [item_b.id]},
                headers={"Authorization": f"Bearer {token_a}"},
            )
            assert resp.status_code == 400
    finally:
        _delete_users([user_a.id, user_b.id])


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------


def test_delete_outfit_returns_204() -> None:
    user = _create_user()
    item = _create_item(user, "Belt")
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            create_resp = client.post(
                "/api/outfits",
                json={"name": "Belt Look", "item_ids": [item.id]},
                headers={"Authorization": f"Bearer {token}"},
            )
            outfit_id = create_resp.json()["id"]

            resp = client.delete(
                f"/api/outfits/{outfit_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 204

            resp = client.get(
                f"/api/outfits/{outfit_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 404
    finally:
        _delete_user(user.id)


def test_delete_outfit_not_found_returns_404() -> None:
    user = _create_user()
    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            resp = client.delete(
                "/api/outfits/99999",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 404
    finally:
        _delete_user(user.id)


def test_delete_outfit_unauthenticated_returns_401() -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.delete("/api/outfits/1")
        assert resp.status_code == 401


def test_delete_outfit_other_user_returns_404() -> None:
    user_a = _create_user()
    user_b = _create_user()
    item_a = _create_item(user_a, "A's Item")
    token_a = _make_token(user_a.id)
    token_b = _make_token(user_b.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            create_resp = client.post(
                "/api/outfits",
                json={"name": "A's Look", "item_ids": [item_a.id]},
                headers={"Authorization": f"Bearer {token_a}"},
            )
            outfit_id = create_resp.json()["id"]

            resp = client.delete(
                f"/api/outfits/{outfit_id}",
                headers={"Authorization": f"Bearer {token_b}"},
            )
            assert resp.status_code == 404
    finally:
        _delete_users([user_a.id, user_b.id])


# ---------------------------------------------------------------------------
# Image URL in embedded items
# ---------------------------------------------------------------------------


def test_outfit_items_have_image_url() -> None:
    user = _create_user()
    db = SessionLocal()
    item = ClothingItem(
        user_id=user.id,
        name="Fancy Hat",
        category="accessory",
        image_filename="hat_abc123.png",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    db.close()

    token = _make_token(user.id)

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            create_resp = client.post(
                "/api/outfits",
                json={"name": "Hat Look", "item_ids": [item.id]},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert create_resp.status_code == 201
            body = create_resp.json()
            assert len(body["items"]) == 1
            assert body["items"][0]["image_url"] == "/api/wardrobe/images/hat_abc123.png"
    finally:
        _delete_user(user.id)
