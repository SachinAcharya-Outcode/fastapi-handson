"""Integration tests for the user CRUD endpoints.

Covers the full lifecycle — create, get-me, list (with filters/sort),
retrieve, update, delete, profile picture upload, and password update.
"""

import io
from pathlib import Path

from PIL import Image

from app.core.config import settings

PREFIX = f"{settings.API_V1_STR}/users"
MISSING_UUID = "00000000-0000-4000-8000-000000000000"


class TestGetMe:
    """GET /users/me"""

    def test_get_me_success(self, client, auth_headers):
        response = client.get(f"{PREFIX}/me", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert "email" in body
        assert body["email"] == "test@example.com"

    def test_get_me_unauthorized(self, client):
        response = client.get(f"{PREFIX}/me")
        assert response.status_code == 401


class TestCreateUser:
    """POST /users"""

    def test_create_user_success(self, client, auth_headers, second_user_data):
        response = client.post(
            f"{PREFIX}/",
            json=second_user_data,
            headers=auth_headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["email"] == second_user_data["email"]

    def test_create_user_duplicate_email(
        self,
        client,
        auth_headers,
        registered_user_data,
    ):
        response = client.post(
            f"{PREFIX}/",
            json=registered_user_data,
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_create_user_unauthorized(self, client, second_user_data):
        response = client.post(f"{PREFIX}/", json=second_user_data)
        assert response.status_code == 401


class TestListUsers:
    """GET /users"""

    def test_list_users(self, client, auth_headers):
        response = client.get(f"{PREFIX}/", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert "items" in body
        assert "total" in body
        assert "page" in body
        assert "size" in body
        assert body["total"] >= 1

    def test_list_users_filter_by_search(
        self,
        client,
        auth_headers,
        second_user_data,
    ):
        client.post(f"{PREFIX}/", json=second_user_data, headers=auth_headers)
        response = client.get(
            f"{PREFIX}/",
            headers=auth_headers,
            params={"search": "second"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["email"] == second_user_data["email"]

    def test_list_users_filter_by_is_active(
        self, client, auth_headers, second_user_data
    ):
        """Filter by ``is_active`` status."""
        client.post(f"{PREFIX}/", json=second_user_data, headers=auth_headers)
        response = client.get(
            f"{PREFIX}/",
            headers=auth_headers,
            params={"is_active": "true"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["total"] >= 2

        response = client.get(
            f"{PREFIX}/",
            headers=auth_headers,
            params={"is_active": "false"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 0

    def test_list_users_unauthorized(self, client):
        response = client.get(f"{PREFIX}/")
        assert response.status_code == 401


class TestRetrieveUser:
    """GET /users/{id}"""

    def test_retrieve_user_success(self, client, auth_headers):
        list_resp = client.get(f"{PREFIX}/", headers=auth_headers)
        user_id = list_resp.json()["items"][0]["id"]
        response = client.get(f"{PREFIX}/{user_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == user_id

    def test_retrieve_user_not_found(self, client, auth_headers):
        response = client.get(
            f"{PREFIX}/{MISSING_UUID}",
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"


class TestUpdateUser:
    """PATCH /users/{id}"""

    def test_update_user_success(self, client, auth_headers):
        list_resp = client.get(f"{PREFIX}/", headers=auth_headers)
        user_id = list_resp.json()["items"][0]["id"]
        response = client.patch(
            f"{PREFIX}/{user_id}",
            json={"full_name": "Updated Name"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"

    def test_update_password(self, client, auth_headers):
        """Updating the password field should succeed."""
        list_resp = client.get(f"{PREFIX}/", headers=auth_headers)
        user_id = list_resp.json()["items"][0]["id"]
        response = client.patch(
            f"{PREFIX}/{user_id}",
            json={"password": "newpassword123"},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Verify we can log in with the new password
        login_resp = client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={"email": "test@example.com", "password": "newpassword123"},
        )
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

    def test_update_user_not_found(self, client, auth_headers):
        response = client.patch(
            f"{PREFIX}/{MISSING_UUID}",
            json={"full_name": "Nope"},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestDeleteUser:
    """DELETE /users/{id}"""

    def test_delete_user_success(self, client, auth_headers, second_user_data):
        create_resp = client.post(
            f"{PREFIX}/",
            json=second_user_data,
            headers=auth_headers,
        )
        user_id = create_resp.json()["id"]
        response = client.delete(f"{PREFIX}/{user_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "success"

    def test_delete_user_not_found(self, client, auth_headers):
        response = client.delete(
            f"{PREFIX}/{MISSING_UUID}",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestProfilePicture:
    """POST /users/{id}/profile-picture"""

    def test_upload_profile_picture(self, client, auth_headers):
        """Upload a JPEG image as a profile picture."""
        list_resp = client.get(f"{PREFIX}/", headers=auth_headers)
        user_id = list_resp.json()["items"][0]["id"]

        img = Image.new("RGB", (200, 200), color="red")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        response = client.post(
            f"{PREFIX}/{user_id}/profile-picture",
            headers=auth_headers,
            files={"file": ("test.jpg", buf, "image/jpeg")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["profile_picture_url"] == f"/{settings.UPLOAD_DIR}/{user_id}.jpg"

        # Clean up the created file
        filepath = Path(settings.UPLOAD_DIR) / f"{user_id}.jpg"
        if filepath.exists():
            filepath.unlink()
