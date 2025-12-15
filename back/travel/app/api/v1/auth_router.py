"""Authentication endpoints"""
from fastapi import APIRouter, HTTPException, status, Request
from datetime import timedelta
import json
import logging
from app.core.auth import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, get_current_active_user
)
from app.core.config import settings
from app.schemas.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.dal import UserService
from app.utils.logging_util import log_operation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, req: Request = None):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = UserService.get_user_by_email(request.email)
        if existing_user:
            # Log failed registration attempt
            await log_operation(
                user_id=None,
                action="CREATE",
                resource_type="user",
                resource_id=None,
                method="POST",
                status_code=400,
                details_json=json.dumps({"error": "Email already registered", "email": request.email}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        password_hash = get_password_hash(request.password)
        user_id = UserService.create_user(
            email=request.email,
            password_hash=password_hash,
            full_name=request.full_name,
            phone=request.phone
        )
        
        # Assign customer role by default
        UserService.assign_role_to_user(user_id, "customer")
        
        # Fetch created user
        user = UserService.get_user_by_id(user_id)
        roles_data = UserService.get_user_roles(user_id)
        roles = [role["code"] for role in roles_data]
        
        # Log successful registration
        await log_operation(
            user_id=user_id,
            action="CREATE",
            resource_type="user",
            resource_id=user_id,
            method="POST",
            status_code=201,
            details_json=json.dumps({"email": request.email, "full_name": request.full_name, "roles": roles}),
            ip_address=req.client.host if req else None
        )
        
        return UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            phone=user.get("phone"),
            is_active=user["is_active"],
            created_at=user["created_at"],
            roles=roles
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, req: Request = None):
    """Login and get access token"""
    try:
        # Get user by email
        user = UserService.get_user_by_email(request.email)
        if not user or not verify_password(request.password, user["password_hash"]):
            # Log failed login attempt
            await log_operation(
                user_id=None,
                action="READ",
                resource_type="user",
                resource_id=None,
                method="POST",
                status_code=401,
                details_json=json.dumps({"error": "Invalid credentials", "email": request.email}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user["is_active"]:
            # Log inactive user login attempt
            await log_operation(
                user_id=user["id"],
                action="READ",
                resource_type="user",
                resource_id=user["id"],
                method="POST",
                status_code=403,
                details_json=json.dumps({"error": "User account inactive"}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Get user roles
        roles_data = UserService.get_user_roles(user["id"])
        roles = [role["code"] for role in roles_data]
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user["id"], "email": user["email"], "roles": roles},
            expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        refresh_token = create_refresh_token(
            data={"sub": user["id"], "email": user["email"]},
            expires_delta=refresh_token_expires
        )
        
        # Log successful login
        await log_operation(
            user_id=user["id"],
            action="READ",
            resource_type="user",
            resource_id=user["id"],
            method="POST",
            status_code=200,
            details_json=json.dumps({"email": request.email, "roles": roles}),
            ip_address=req.client.host if req else None
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: dict):
    """Refresh access token using refresh token"""
    # This would decode and validate the refresh token
    # For now, just return a new access token
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh endpoint to be implemented"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user = None):
    """Get current user profile"""
    from app.core.auth import get_current_active_user
    
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = UserService.get_user_by_id(current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        phone=user.get("phone"),
        is_active=user["is_active"],
        created_at=user["created_at"],
        roles=current_user.roles
    )