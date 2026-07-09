"""Email service — send transactional emails via SMTP.

Designed for MailHog in development.  Uses the built-in ``smtplib``
module and runs synchronously; call it from ``BackgroundTasks`` to
avoid blocking the HTTP response.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TYPE_CHECKING

from app.core.config import settings

if TYPE_CHECKING:
    from app.db.models import User


def send_activation_email(user: "User") -> None:
    """Send an email verification link to *user*."""
    verify_url = (
        f"{settings.API_V1_STR}/auth/verify-email"
        f"?token={user.email_verification_token}"
    )
    subject = "Please verify your email address"
    body = (
        f"Hi {user.full_name},\n\n"
        f"Thank you for registering. Please click the link below "
        f"to verify your email address:\n\n{verify_url}\n\n"
        f"If you did not create an account, please ignore this email."
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = user.email
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        timeout=10,
    ) as server:
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL, [user.email], msg.as_string())
