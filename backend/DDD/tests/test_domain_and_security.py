"""Small repeatable tests for core domain and authentication rules."""

import unittest

from app.domain.auth import ValidationException
from app.domain.todo import (
    InvalidTaskTitleError,
    TaskAlreadyCompletedError,
    TodoItem,
)
from app.infrastructure.security import AuthSecurity


class TodoDomainTests(unittest.TestCase):
    """Verify rules that must behave the same for every database."""

    def test_create_trims_title_and_normalizes_priority(self) -> None:
        todo = TodoItem.create("  Learn DDD  ", "high", "owner-1")

        self.assertEqual(todo.title.value, "Learn DDD")
        self.assertEqual(todo.priority.value, "HIGH")
        self.assertFalse(todo.is_completed)

    def test_short_title_is_rejected(self) -> None:
        with self.assertRaises(InvalidTaskTitleError):
            TodoItem.create("x", "LOW", "owner-1")

    def test_completed_todo_cannot_complete_again(self) -> None:
        todo = TodoItem.create("Write tests", "MEDIUM", "owner-1")
        todo.complete()

        with self.assertRaises(TaskAlreadyCompletedError):
            todo.complete()


class AuthSecurityTests(unittest.TestCase):
    """Verify password and database-bound token behavior."""

    def setUp(self) -> None:
        self.postgresql = AuthSecurity("test-secret", "postgresql", 5)
        self.mongodb = AuthSecurity("test-secret", "mongodb", 5)

    def test_password_is_hashed_and_can_be_verified(self) -> None:
        password = "SimplePass123"
        saved_hash = self.postgresql.hash_password(password)

        self.assertNotIn(password, saved_hash)
        self.assertTrue(
            self.postgresql.password_matches(password, saved_hash)
        )
        self.assertFalse(
            self.postgresql.password_matches("wrong-password", saved_hash)
        )

    def test_token_is_valid_only_for_its_database(self) -> None:
        token = self.postgresql.create_token("user-1", "user@example.com")

        self.assertEqual(
            self.postgresql.read_token(token),
            ("user-1", "user@example.com"),
        )
        with self.assertRaises(ValidationException):
            self.mongodb.read_token(token)

    def test_modified_token_is_rejected(self) -> None:
        token = self.postgresql.create_token("user-1", "user@example.com")
        modified_token = token[:-1] + ("A" if token[-1] != "A" else "B")

        with self.assertRaises(ValidationException):
            self.postgresql.read_token(modified_token)


if __name__ == "__main__":
    unittest.main()
