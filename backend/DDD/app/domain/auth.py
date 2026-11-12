"""Authentication business rules, data, and persistence contract."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class ValidationException(Exception):
    """A safe authentication/input error that may be returned by the API."""


class InvalidEmailError(ValidationException):
    """Raised when an email cannot represent a valid account identity."""


class WeakPasswordError(ValidationException):
    """Raised when a new password breaks the signup password policy."""


class GoogleAccountConflictError(ValidationException):
    """Raised when an email is already linked to another Google account."""


class PasswordLoginRequiredError(ValidationException):
    """Raised when a third-party email cannot be linked automatically."""


@dataclass(frozen=True)
class EmailAddress:
    """What: Keep every authentication email normalized and valid.

    When: Signup, login, or verified Google data enters the domain.
    How: Remove outer spaces, lowercase the value, and require one valid @ split.
    """

    value: str

    def __post_init__(self) -> None:
        # Domain bhi validation karta hai taa-ke HTTP ke ilawa kisi aur entry
        # point se anay wali invalid email account state mein enter na kar sakay.
        clean_email = (self.value or "").strip().lower()
        local_part, separator, domain_part = clean_email.partition("@")
        if (
            separator != "@"
            or not local_part
            or not domain_part
            or "@" in domain_part
            or any(character.isspace() for character in clean_email)
        ):
            raise InvalidEmailError("Enter a valid email address.")
        object.__setattr__(self, "value", clean_email)


@dataclass(frozen=True)
class DisplayName:
    """Keep a clean display name and provide a safe default."""

    value: str

    def __post_init__(self) -> None:
        clean_name = (self.value or "").strip() or "User"
        object.__setattr__(self, "value", clean_name)


class PasswordPolicy:
    """Define the shared password rule independently of FastAPI and databases."""

    MIN_LENGTH = 6

    @classmethod
    def validate_for_signup(cls, password: str) -> None:
        """Require every newly created password to have at least six characters."""
        if not isinstance(password, str) or len(password) < cls.MIN_LENGTH:
            raise WeakPasswordError(
                f"Password must have at least {cls.MIN_LENGTH} characters."
            )


@dataclass(frozen=True)
class GoogleIdentity:
    """Trusted Google identity expressed as domain-friendly values."""

    subject: str
    email: EmailAddress
    display_name: DisplayName
    has_google_hosted_domain: bool

    @classmethod
    def create(
        cls,
        subject: str,
        email: str,
        display_name: str,
        has_google_hosted_domain: bool,
    ) -> "GoogleIdentity":
        """Build a valid identity after infrastructure verifies Google's token."""
        clean_subject = (subject or "").strip()
        if not clean_subject:
            raise ValidationException("Google account identity is missing.")

        clean_email = EmailAddress(email)
        # Google name optional ho sakta hai; email prefix readable fallback hai.
        fallback_name = clean_email.value.split("@", 1)[0]
        clean_name = DisplayName(display_name or fallback_name)
        return cls(
            subject=clean_subject,
            email=clean_email,
            display_name=clean_name,
            has_google_hosted_domain=has_google_hosted_domain,
        )

    @property
    def can_link_existing_password_account(self) -> bool:
        """Allow safe auto-linking only when Google controls the email identity."""
        return (
            self.email.value.endswith("@gmail.com")
            or self.has_google_hosted_domain
        )


class GoogleAccountPolicy:
    """Decide whether a verified Google identity may use an existing account."""

    @staticmethod
    def should_link(
        saved_google_subject: str | None,
        identity: GoogleIdentity,
    ) -> bool:
        """Validate account ownership and report whether a new link is needed."""
        # Different Google subject ko same email account lena allow nahi karte.
        if saved_google_subject:
            if saved_google_subject != identity.subject:
                raise GoogleAccountConflictError(
                    "This email belongs to another Google account."
                )
            return False

        # Gmail/Workspace mein Google email authority prove karta hai. Doosray
        # providers ke existing password accounts ko silently link nahi karte.
        if not identity.can_link_existing_password_account:
            raise PasswordLoginRequiredError(
                "Use your password for this non-Google-managed email account."
            )
        return True


@dataclass(frozen=True)
class UserData:
    """Database-independent authenticated user returned by repositories."""

    uid: str
    email: str
    token: str


class AuthRepository(ABC):
    """What: Define storage-independent authentication operations.

    When: AuthService needs signup, password login, Google login, or token verification.
    How: Each selected database provides its own concrete implementation.
    """

    # Domain sirf required operations batata hai. Actual Firestore/Mongo/SQL
    # code infrastructure layer mein in methods ko implement karta hai.
    @abstractmethod
    def signup(self, email: str, password: str, name: str) -> UserData:
        """Create one account in the selected database."""
        raise NotImplementedError

    @abstractmethod
    def login(self, email: str, password: str) -> UserData:
        """Verify selected-database credentials."""
        raise NotImplementedError

    @abstractmethod
    def login_with_google(self, credential: str) -> UserData:
        """Verify Google and create or find a user in the selected database."""
        raise NotImplementedError

    @abstractmethod
    def authenticate(self, token: str) -> UserData:
        """Verify a token and confirm its selected-database user exists."""
        raise NotImplementedError
