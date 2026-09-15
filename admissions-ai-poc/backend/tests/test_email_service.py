"""
Unit tests for the email service's three-way priority (SendGrid -> SMTP ->
console fallback). Uses mocking for the SMTP path so tests never make a
real network call or need live credentials.
"""

from unittest.mock import patch, MagicMock
import importlib


def _reload_with_env(env: dict):
    """Reload settings + email_service with a patched environment so the
    module-level constants (read at import time) pick up the new values."""
    with patch.dict("os.environ", env, clear=False):
        from app.config import settings
        importlib.reload(settings)
        from app.notifications import email_service
        importlib.reload(email_service)
        return email_service


def test_console_fallback_when_nothing_configured():
    email_service = _reload_with_env({"SENDGRID_API_KEY": "", "SMTP_USERNAME": "", "SMTP_PASSWORD": ""})
    result = email_service.send_recommendation_email(
        to_email="student@example.com",
        student_name="Test Student",
        recommendation_items=[{"university_id": "1", "university_name": "U", "score": 0.9, "explanation": "Fit."}],
    )
    assert result.status == "console_logged"


def test_smtp_used_when_configured_and_no_sendgrid_key():
    email_service = _reload_with_env({
        "SENDGRID_API_KEY": "",
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USERNAME": "myaccount@gmail.com",
        "SMTP_PASSWORD": "fake-app-password",
    })

    with patch("smtplib.SMTP") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        result = email_service.send_recommendation_email(
            to_email="student@example.com",
            student_name="Test Student",
            recommendation_items=[{"university_id": "1", "university_name": "U", "score": 0.9, "explanation": "Fit."}],
        )

        assert result.status == "sent"
        mock_smtp_cls.assert_called_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("myaccount@gmail.com", "fake-app-password")
        assert mock_server.sendmail.called


def test_smtp_auth_failure_reported_without_crashing():
    email_service = _reload_with_env({
        "SENDGRID_API_KEY": "",
        "SMTP_USERNAME": "myaccount@gmail.com",
        "SMTP_PASSWORD": "wrong-password",
    })

    with patch("smtplib.SMTP") as mock_smtp_cls:
        import smtplib
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"bad credentials")
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        result = email_service.send_recommendation_email(
            to_email="student@example.com",
            student_name="Test Student",
            recommendation_items=[{"university_id": "1", "university_name": "U", "score": 0.9, "explanation": "Fit."}],
        )

        assert result.status == "failed"
        assert "App Password" in result.detail
