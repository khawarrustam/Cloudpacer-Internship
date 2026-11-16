"""GitHub OAuth code exchange and verified-profile adapter."""

import requests

from app.domain.auth import GitHubIdentity, ValidationException


class GitHubOAuthClient:
    """What: Turn a short-lived GitHub OAuth code into a trusted identity.

    When: A selected-database auth repository handles GitHub login.
    How: Exchange code server-side, then read profile and verified primary email.
    """

    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_URL = "https://api.github.com/user"
    EMAILS_URL = "https://api.github.com/user/emails"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> None:
        self.client_id = client_id.strip()
        self.client_secret = client_secret.strip()
        self.redirect_uri = redirect_uri.strip()
        self.session = requests.Session()

    def verify_code(self, code: str) -> GitHubIdentity:
        """Exchange one code and return GitHub's stable ID and verified email."""
        self._validate_configuration()
        clean_code = (code or "").strip()
        if not clean_code:
            raise ValidationException("GitHub did not return a login code.")

        try:
            token_response = self.session.post(
                self.TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": clean_code,
                    "redirect_uri": self.redirect_uri,
                },
                timeout=10,
            )
            token_response.raise_for_status()
            token_data = token_response.json()
            if not isinstance(token_data, dict):
                raise ValidationException("GitHub returned an invalid token response.")
            access_token = token_data.get("access_token")
            if not access_token:
                raise ValidationException(
                    "GitHub login code is invalid or expired. Please try again."
                )

            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {access_token}",
                "X-GitHub-Api-Version": "2026-03-10",
                "User-Agent": "TodoFlow",
            }
            profile = self._get_json(self.USER_URL, headers)
            if not isinstance(profile, dict):
                raise ValidationException("GitHub returned an invalid user profile.")
            email = self._verified_email(
                self._get_json(self.EMAILS_URL, headers)
            )
        except ValidationException:
            raise
        except (requests.RequestException, ValueError, TypeError) as error:
            raise ValidationException(
                "GitHub login is temporarily unavailable."
            ) from error

        # Numeric GitHub user ID stable hai; username future mein change ho sakta hai.
        return GitHubIdentity.create(
            subject=str(profile.get("id") or ""),
            email=email,
            display_name=str(profile.get("name") or profile.get("login") or ""),
        )

    def _get_json(self, url: str, headers: dict) -> object:
        """Call one authenticated GitHub API endpoint and return JSON."""
        response = self.session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def _validate_configuration(self) -> None:
        """Fail clearly before making an incomplete OAuth request."""
        values = (self.client_id, self.client_secret, self.redirect_uri)
        if any(not value or value.startswith("replace-with-") for value in values):
            raise ValidationException(
                "GitHub login is not configured. Add GitHub OAuth settings."
            )

    @staticmethod
    def _verified_email(emails: object) -> str:
        """Prefer the verified primary email, then any verified email."""
        if not isinstance(emails, list):
            raise ValidationException("GitHub account email could not be verified.")
        verified = [
            item
            for item in emails
            if isinstance(item, dict) and item.get("verified") is True
        ]
        primary = next(
            (item for item in verified if item.get("primary") is True),
            None,
        )
        selected = primary or (verified[0] if verified else None)
        email = selected.get("email") if selected else None
        if not isinstance(email, str) or not email:
            raise ValidationException("GitHub account email could not be verified.")
        return email
