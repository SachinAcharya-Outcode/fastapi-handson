"""Integration tests for the authentication endpoints.

Covers register, login (success + failure), refresh, and logout.
"""

from app.core.config import settings

PREFIX = f"{settings.API_V1_STR}/auth"


class TestRegister:
    """POST /auth/register"""

    def test_register_success(self, client, registered_user_data):
        response = client.post(f"{PREFIX}/register", json=registered_user_data)
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    def test_register_duplicate_email(
        self, client, registered_user_data, registered_user
    ):
        response = client.post(f"{PREFIX}/register", json=registered_user_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"


class TestLogin:
    """POST /auth/login"""

    def test_login_success(self, client, registered_user_data):
        client.post(f"{PREFIX}/register", json=registered_user_data)
        response = client.post(
            f"{PREFIX}/login",
            json={
                "email": registered_user_data["email"],
                "password": registered_user_data["password"],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert "refresh_token" in body

    def test_login_invalid_password(self, client, registered_user_data):
        client.post(f"{PREFIX}/register", json=registered_user_data)
        response = client.post(
            f"{PREFIX}/login",
            json={
                "email": registered_user_data["email"],
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_login_nonexistent_user(self, client):
        response = client.post(
            f"{PREFIX}/login",
            json={
                "email": "noone@example.com",
                "password": "doesnotmatter",
            },
        )
        assert response.status_code == 401


class TestRefresh:
    """POST /auth/refresh"""

    def test_refresh_success(self, client, registered_user_data):
        reg_resp = client.post(f"{PREFIX}/register", json=registered_user_data)
        refresh_token = reg_resp.json()["refresh_token"]

        response = client.post(
            f"{PREFIX}/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert "refresh_token" in body

    def test_refresh_invalid_token(self, client):
        response = client.post(
            f"{PREFIX}/refresh",
            json={"refresh_token": "garbage-token"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired refresh token"


class TestLogout:
    """POST /auth/logout"""

    def test_logout(self, client):
        response = client.post(f"{PREFIX}/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
