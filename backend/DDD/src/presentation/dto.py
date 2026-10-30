"""HTTP request and response DTOs used only by FastAPI routes."""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    display_name: str = "User"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class AuthResponse(BaseModel):
    uid: str
    email: str
    token: str
    message: str


class CreateTodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    priority: Literal[
        "LOW", "MEDIUM", "HIGH", "low", "medium", "high"
    ] = "MEDIUM"


class TodoResponse(BaseModel):
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: str | None
    owner_uid: str
