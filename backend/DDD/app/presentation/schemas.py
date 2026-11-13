"""HTTP request and response schemas used only by FastAPI routes."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


# Yeh models sirf HTTP JSON contract hain. Application layer apne plain DTOs
# use karti hai taa-ke use cases FastAPI/Pydantic se independent rahen.
class SignupRequest(BaseModel):
    """Validate the JSON body received by POST /auth/signup."""

    email: EmailStr
    password: str = Field(min_length=6)
    display_name: str = "User"


class LoginRequest(BaseModel):
    """Validate the JSON body received by POST /auth/login."""

    email: EmailStr
    password: str = Field(min_length=6)


class GoogleLoginRequest(BaseModel):
    """Validate the Google ID token received by POST /auth/google."""

    credential: str = Field(min_length=20)


class AuthResponse(BaseModel):
    """Define the public JSON returned after signup or login."""

    uid: str
    email: str
    token: str
    message: str


class CreateTodoRequest(BaseModel):
    """Validate title length and priority at the HTTP boundary."""

    title: str = Field(min_length=3, max_length=120)
    # Client lowercase ya uppercase bhej sakta hai; domain canonical uppercase banata hai.
    priority: Literal[
        "LOW", "MEDIUM", "HIGH", "low", "medium", "high"
    ] = "MEDIUM"
    due_at: datetime | None = None
    reminder_option: Literal[
        "NONE", "1_MINUTE", "1_HOUR", "1_DAY", "3_DAYS", "CUSTOM"
    ] = "NONE"
    custom_reminder_at: datetime | None = None


class TodoResponse(BaseModel):
    """Define the consistent todo JSON returned by todo endpoints."""

    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: str | None
    owner_uid: str
    due_at: str | None
    reminder_at: str | None
    reminder_sent_at: str | None
    reminder_option: str
