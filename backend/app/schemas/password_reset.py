from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class ForgotPasswordRequest(BaseModel):
    """Payload for requesting a password reset token."""
    email: EmailStr = Field(..., description="Registered student email address")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class ForgotPasswordResponse(BaseModel):
    """Neutral response confirming password reset instructions."""
    message: str = "If an account exists for this email address, password reset instructions will be sent."
    reset_token: str | None = None  # Returned for local development/testing when SMTP is not configured
    reset_url: str | None = None


class ResetPasswordRequest(BaseModel):
    """Payload for setting a new password using a single-use token."""
    token: str = Field(..., min_length=10, description="Secure password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password (minimum 8 characters)")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Confirmation of new password")

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("New password and confirmation password do not match.")
        return self


class ResetPasswordResponse(BaseModel):
    """Response returned upon successful password update."""
    message: str = "Your password has been successfully reset. You can now log in with your new password."
    success: bool = True
