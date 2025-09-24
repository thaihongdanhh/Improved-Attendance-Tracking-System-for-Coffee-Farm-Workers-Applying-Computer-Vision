from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.core.config import settings
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    print(f"[Auth] Token received: {token[:20]}..." if token and len(token) > 20 else f"[Auth] Token: {token}")
    
    payload = decode_token(token)
    if payload is None:
        print("[Auth] Failed to decode token")
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        print("[Auth] No user_id in token payload")
        raise credentials_exception
    
    print(f"[Auth] User authenticated: {user_id}")
    return {
        "id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role", "user")
    }

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user