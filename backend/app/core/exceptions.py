"""Custom exception classes for the application."""


class EmailAlreadyExistsError(Exception):
    """Raised when attempting to register with an email that already exists."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email already registered: {email}")


class UsernameAlreadyExistsError(Exception):
    """Raised when attempting to register with a username that already exists."""

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Username already taken: {username}")


class InvalidCredentialsError(Exception):
    """Raised when authentication fails due to invalid email or password."""

    def __init__(self):
        super().__init__("Invalid email or password")


class UserNotFoundError(Exception):
    """Raised when a user cannot be found."""

    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"User not found: {identifier}")
