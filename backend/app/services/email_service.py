import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, recipient_name: str, reset_url: str) -> bool:
    """
    Sends a password reset email using standard Python smtplib if SMTP is configured.
    If SMTP settings are not provided, logs the reset URL to application logs without failing.

    Returns:
        True if email was dispatched via SMTP, False otherwise.
    """
    if not settings.smtp_host:
        logger.info(
            "SMTP_HOST not configured. Password reset link for '%s' (%s): %s",
            recipient_name,
            to_email,
            reset_url,
        )
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Reset Your Password - Student Skill Gap Analyzer"
        msg["From"] = settings.smtp_from_email
        msg["To"] = to_email

        text_content = (
            f"Hello {recipient_name},\n\n"
            f"We received a request to reset your password for Student Skill Gap Analyzer.\n"
            f"Please click the link below or paste it into your browser to set a new password:\n\n"
            f"{reset_url}\n\n"
            f"This link will expire in 15 minutes. If you did not request this, you can safely ignore this email.\n"
        )

        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; rounded: 12px;">
              <h2 style="color: #2563eb;">Password Reset Request</h2>
              <p>Hello <strong>{recipient_name}</strong>,</p>
              <p>We received a request to reset your password for your Student Skill Gap Analyzer account.</p>
              <p style="margin: 24px 0;">
                <a href="{reset_url}" style="background-color: #2563eb; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                  Reset Password
                </a>
              </p>
              <p style="font-size: 13px; color: #64748b;">
                Or copy and paste this link in your browser:<br>
                <a href="{reset_url}" style="color: #2563eb;">{reset_url}</a>
              </p>
              <p style="font-size: 12px; color: #94a3b8; margin-top: 30px;">
                This link expires in 15 minutes. If you did not make this request, no action is needed.
              </p>
            </div>
          </body>
        </html>
        """

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.ehlo()
            if server.has_extn("STARTTLS"):
                server.starttls()
                server.ehlo()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, [to_email], msg.as_string())

        logger.info("Password reset email sent successfully to %s", to_email)
        return True
    except Exception as exc:
        logger.error("Failed to deliver password reset email to %s: %s", to_email, str(exc))
        return False
