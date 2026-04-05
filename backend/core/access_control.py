from fastapi import Depends, HTTPException, status
from models.auth import UserRole
from dependencies import get_current_user

def require_roles(*roles: UserRole):
    
    allowed = set(roles)

    async def dependency(current_user=Depends(get_current_user)):
        current_role = current_user.role

        if isinstance(current_role, str):
            current_role = UserRole(current_role)

        if current_role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return current_user

    return dependency
