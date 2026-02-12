"""Authentication service for user registration and login."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    InvalidCredentialsError,
)


class AuthService:
    """Service for handling authentication and user management."""

    @staticmethod
    async def register_user(
        db: AsyncSession,
        email: str,
        username: str,
        password: str
    ) -> User:
        """
        Create new user with hashed password.

        Args:
            db: Database session
            email: User email address
            username: Desired username
            password: Plain text password

        Returns:
            Created User object

        Raises:
            EmailAlreadyExistsError: If email is already registered
            UsernameAlreadyExistsError: If username is already taken
        """
        # Check if email already exists
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise EmailAlreadyExistsError(email)

        # Check if username already exists
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise UsernameAlreadyExistsError(username)

        # Hash password and create user
        hashed_pwd = hash_password(password)
        new_user = User(
            email=email,
            username=username,
            hashed_password=hashed_pwd,
            is_premium=False
        )

        try:
            db.add(new_user)
            return new_user
        except IntegrityError as e:
            await db.rollback()
            # Handle race conditions where duplicate was inserted between check and insert
            if "email" in str(e.orig):
                raise EmailAlreadyExistsError(email)
            elif "username" in str(e.orig):
                raise UsernameAlreadyExistsError(username)
            raise

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> tuple[User, str]:
        """
        Verify credentials and return user with access token.

        Args:
            db: Database session
            email: User email address
            password: Plain text password

        Returns:
            Tuple of (User object, JWT access token)

        Raises:
            InvalidCredentialsError: If email or password is incorrect
        """
        # Find user by email
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise InvalidCredentialsError()

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        # Generate access token with user ID as subject
        token_data = {"sub": str(user.id)}
        access_token = create_access_token(token_data)

        return user, access_token

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        """
        Fetch user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        """
        Fetch user by email address.

        Args:
            db: Database session
            email: User email address

        Returns:
            User object if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
