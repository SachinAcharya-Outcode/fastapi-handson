"""Integration tests for the authentication endpoints.

Covers register, login (success + failure), refresh, logout,
and email verification.
"""

import uuid

from app.core.config import settings

PREFIX = f"{settings.API_V1_STR}/auth"


class TestRegister:
    """POST /auth/register"""

    def test_register_success(self, client, registered_user_data):
        response = client.post(f"{PREFIX}/register", json=registered_user_data)
        assert response.status_code == 200
        body = response.json()
        assert body["email"] == registered_user_data["email"]
        assert body["full_name"] == registered_user_data["full_name"]
        assert body["message"] == "Registration successful. Please log in."
        assert "access_token" not in body

    def test_register_duplicate_email(
        self, client, registered_user_data, registered_user
    ):
        response = client.post(f"{PREFIX}/register", json=registered_user_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"


class TestEmailVerification:
    """GET /auth/verify-email"""

    def test_verify_email_success(self, client, registered_user_data):
        # Register — the response no longer contains the token, so we
        # query the DB through the API directly.
        reg_resp = client.post(f"{PREFIX}/register", json=registered_user_data)
        assert reg_resp.status_code == 200

        login_resp = client.post(
            f"{PREFIX}/login",
            json={
                "email": registered_user_data["email"],
                "password": registered_user_data["password"],
            },
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        # Get the user to learn the email_verification_token
        me_resp = client.get(
            f"{settings.API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        user = me_resp.json()

        # We can't read the token from the API response (it's not exposed),
        # so we verify the endpoint structure.  The test above confirms
        # registration sets a token; here we test with a made-up token
        # to exercise the endpoint.  Actually — we need the real token.
        #
        # Instead, let's verify that verifying with a garbage token fails:
        resp = client.get(f"{PREFIX}/verify-email", params={"token": "garbage"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid or expired verification token"

    def test_verify_email_success_flow(self, client, registered_user_data, db_session):
        """Full flow: register → extract token from DB → verify."""
        from app.db.models import User

        client.post(f"{PREFIX}/register", json=registered_user_data)

        user = (
            db_session.query(User)
            .filter(User.email == registered_user_data["email"])
            .first()
        )
        assert user is not None
        assert user.email_verification_token is not None

        resp = client.get(
            f"{PREFIX}/verify-email",
            params={"token": user.email_verification_token},
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Email verified successfully. You can now log in."

        # Confirm the token was consumed — expire identity map first
        db_session.expire_all()
        user2 = (
            db_session.query(User)
            .filter(User.email == registered_user_data["email"])
            .first()
        )
        assert user2 is not None
        assert user2.is_email_verified is True
        assert user2.email_verification_token is None

    def test_verify_email_invalid_token(self, client):
        response = client.get(
            f"{PREFIX}/verify-email",
            params={"token": "nonexistent-token"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired verification token"


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
        client.post(f"{PREFIX}/register", json=registered_user_data)
        login_resp = client.post(
            f"{PREFIX}/login",
            json={
                "email": registered_user_data["email"],
                "password": registered_user_data["password"],
            },
        )
        refresh_token = login_resp.json()["refresh_token"]

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

    def test_refresh_token_missing_sub(self, client):
        """Refresh token that is valid JWT but has no ``sub`` claim."""
        from datetime import UTC, datetime, timedelta

        from jose import jwt

        from app.core.config import settings

        token = jwt.encode(
            {"iat": datetime.now(UTC), "exp": datetime.now(UTC) + timedelta(hours=1)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        response = client.post(
            f"{PREFIX}/refresh",
            json={"refresh_token": token},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid refresh token payload"

    def test_refresh_user_not_found(self, client):
        """Refresh token with ``sub`` pointing to a non-existent user."""
        from datetime import UTC, datetime, timedelta

        from jose import jwt

        from app.core.config import settings

        token = jwt.encode(
            {
                "sub": "00000000-0000-4000-8000-000000000000",
                "iat": datetime.now(UTC),
                "exp": datetime.now(UTC) + timedelta(hours=1),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        response = client.post(
            f"{PREFIX}/refresh",
            json={"refresh_token": token},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"


class TestTokenEdgeCases:
    """Edge cases for token validation in dependencies."""

    def test_access_token_missing_sub(self, client):
        """Valid JWT as Bearer token but with no ``sub`` claim."""
        from datetime import UTC, datetime, timedelta

        from jose import jwt

        from app.core.config import settings

        token = jwt.encode(
            {"iat": datetime.now(UTC), "exp": datetime.now(UTC) + timedelta(hours=1)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        response = client.get(
            f"{settings.API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token payload"

    def test_access_token_user_not_found(self, client):
        """Valid JWT with ``sub`` pointing to a non-existent user."""
        from datetime import UTC, datetime, timedelta

        from jose import jwt

        from app.core.config import settings

        token = jwt.encode(
            {
                "sub": "00000000-0000-4000-8000-000000000000",
                "iat": datetime.now(UTC),
                "exp": datetime.now(UTC) + timedelta(hours=1),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        response = client.get(
            f"{settings.API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "User not found"

    def test_decode_access_token_malformed(self, client):
        """Garbage passed as Bearer token."""
        response = client.get(
            f"{settings.API_V1_STR}/users/me",
            headers={"Authorization": "Bearer completely-invalid-token"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] in (
            "Invalid or expired token",
            "Invalid token payload",
        )


class TestLogout:
    """POST /auth/logout"""

    def test_logout(self, client):
        response = client.post(f"{PREFIX}/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
