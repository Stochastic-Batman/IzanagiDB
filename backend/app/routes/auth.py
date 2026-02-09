import logging

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from tables import User, RefreshToken
from schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    generate_refresh_token,
    get_refresh_token_expiry
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


async def get_refresh_token_from_cookie(refresh_token: Optional[str] = Cookie(None)) -> str:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )
    return refresh_token


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.username}")
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    # Find user by username
    result = await db.execute(select(User).where(User.username == user_credentials.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.user_id), "username": user.username})
    
    # Create refresh token
    refresh_token_hex = generate_refresh_token()
    refresh_token_expiry = get_refresh_token_expiry()
    
    # Store refresh token in database
    new_refresh_token = RefreshToken(
        user_id=user.user_id,
        token_hex=refresh_token_hex,
        expires_at=refresh_token_expiry
    )
    db.add(new_refresh_token)
    await db.commit()
    
    # Set refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token_hex,
        httponly=True,
        secure=False,  # Should be set to True in production with HTTPS
        samesite="lax",
        max_age=2592000  # 30 days in seconds
    )
    
    logger.info(f"User logged in: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(response: Response, refresh_token: str = Depends(get_refresh_token_from_cookie), db: AsyncSession = Depends(get_db)):
    # Find refresh token in database
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hex == refresh_token))
    db_token = result.scalar_one_or_none()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if token is expired
    if db_token.expires_at < datetime.now(timezone.utc):
        await db.delete(db_token)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    # Get associated user
    result = await db.execute(select(User).where(User.user_id == db_token.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(user.user_id), "username": user.username})
    
    logger.info(f"Access token refreshed for user: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response, refresh_token: Optional[str] = Cookie(None), db: AsyncSession = Depends(get_db)):
    if refresh_token:
        # Delete refresh token from database
        result = await db.execute(select(RefreshToken).where(RefreshToken.token_hex == refresh_token))
        db_token = result.scalar_one_or_none()
        
        if db_token:
            await db.delete(db_token)
            await db.commit()
    
    # Clear cookie
    response.delete_cookie(key="refresh_token")
    
    logger.info("User logged out")
    return {"message": "Successfully logged out"}
