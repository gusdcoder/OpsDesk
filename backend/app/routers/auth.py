from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import structlog

from app.schemas import LoginRequest, TokenResponse, MFASetupResponse, UserResponse
from app.models import User
from app.utils.auth_utils import (
    verify_password, create_access_token, hash_password,
    generate_mfa_secret, get_totp_provisioning_uri, verify_totp
)
from app.main import SessionLocal

router = APIRouter()
logger = structlog.get_logger()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        logger.warning("login_failed_user_not_found", email=request.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not verify_password(request.password, user.password_hash):
        logger.warning("login_failed_invalid_password", email=request.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Check MFA if enabled
    if user.mfa_enabled:
        if not request.totp_code:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="MFA code required")
        if not verify_totp(user.mfa_secret, request.totp_code):
            logger.warning("login_failed_invalid_totp", email=request.email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")
    
    # Create tokens
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    logger.info("login_success", email=request.email, user_id=user.id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds())
    )

@router.post("/logout")
async def logout():
    """Logout (client-side JWT invalidation)"""
    logger.info("logout_success")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(db: Session = Depends(get_db)):
    """Get current authenticated user"""
    # This would be populated by auth middleware in real implementation
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
