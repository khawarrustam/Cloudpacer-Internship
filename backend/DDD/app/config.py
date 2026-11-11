"""Typed application settings loaded from environment variables and .env."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# .env aur Firebase key ko current terminal folder ke bajaye backend folder se
# resolve karte hain. Is se command kisi bhi folder se run ho sakti hai.
BASE_DIRECTORY = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """What: Hold every external application setting in typed form.

    When: The composition root loads settings once during application startup.
    How: Pydantic reads `.env`, applies terminal overrides, and converts types.
    """

    # App/server ki har value .env se required hai. Pydantic strings ko declared
    # int/bool types mein convert aur validate karta hai.
    app_name: str
    app_architecture: str
    backend_host: str
    backend_port: int
    backend_reload: bool
    cors_origins: str
    log_level: str

    # Yeh one switch users aur todos dono ke repository adapters select karta hai.
    database: str
    auth_token_secret: str
    auth_token_expire_minutes: int

    # Har database group sirf tab use hota hai jab DATABASE us driver ko select kare.
    mongodb_uri: str
    mongodb_database: str
    mongodb_todo_collection: str
    mongodb_user_collection: str

    postgresql_url: str

    firebase_credentials_path: str
    firestore_api_url: str
    firestore_database_id: str
    firestore_user_collection: str
    firestore_auth_collection: str
    firestore_todo_collection: str
    firestore_page_size: int

    # Terminal environment variables .env ki values ko override kar sakti hain.
    model_config = SettingsConfigDict(
        env_file=BASE_DIRECTORY / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def selected_database(self) -> str:
        """What: Return one supported, normalized database name.

        When: Repository wiring and health responses need the active database.
        How: The beginner-friendly `firebase` alias maps to `firestore`.
        """
        # User FIREBASE bhi likhe toh internally one canonical name use ho.
        database = self.database.strip().lower()
        if database == "firebase":
            database = "firestore"
        if database not in {"firestore", "mongodb", "postgresql"}:
            raise ValueError(
                "DATABASE must be firestore, mongodb, or postgresql."
            )
        return database

    @property
    def allowed_origins(self) -> list[str]:
        """Return clean CORS origins from the comma-separated setting."""
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def firebase_credential_file(self) -> Path:
        """Return an absolute path for the Firestore service-account file."""
        path = Path(self.firebase_credentials_path)
        if path.is_absolute():
            return path
        return BASE_DIRECTORY / path


@lru_cache
def get_settings() -> Settings:
    """What: Build and cache the validated settings object.

    When: Any startup component needs configuration.
    How: One cached instance prevents repeated `.env` reads.
    """
    # Cache ki wajah se har request par .env dobara read nahi hoti.
    return Settings()
