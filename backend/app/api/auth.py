import logging
import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    InvalidCredentialsError,
)
from app.services import AuthService
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    try:
        logger.info(f"Registration attempt for email: {user_in.email}, username: {user_in.username}")
        user = await AuthService.register_user(
            db=db,
            email=user_in.email,
            username=user_in.username,
            password=user_in.password
        )
        # Flush to generate ID and created_at, then refresh to load values
        await db.flush()
        await db.refresh(user)
        logger.info(f"User registered successfully: {user_in.email}")
        return user
    except EmailAlreadyExistsError as e:
        logger.warning(f"Registration failed - email already exists: {user_in.email}")
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")
    except UsernameAlreadyExistsError as e:
        logger.warning(f"Registration failed - username already exists: {user_in.username}")
        raise HTTPException(status_code=400, detail="이미 사용 중인 사용자명입니다")
    except Exception as e:
        logger.error(f"Unexpected error during registration for {user_in.email}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return access token."""
    try:
        logger.info(f"Login attempt for email: {user_in.email}")
        user, token = await AuthService.authenticate_user(
            db=db,
            email=user_in.email,
            password=user_in.password
        )
        logger.info(f"User logged in successfully: {user_in.email}")
        return TokenResponse(access_token=token)
    except InvalidCredentialsError as e:
        logger.warning(f"Login failed - invalid credentials for email: {user_in.email}")
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다"
        )
    except Exception as e:
        logger.error(f"Unexpected error during login for {user_in.email}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current user profile."""
    try:
        logger.info(f"Fetching user profile for user_id: {user_id}")
        user = await AuthService.get_user_by_id(db=db, user_id=user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        logger.info(f"User profile fetched successfully: {user_id}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching user profile for {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user profile: {str(e)}"
        )
