from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user


def require_permission(required_role: str):
    def permission_checker(current_user=Depends(get_current_user)):

        # if user has no role field
        if not hasattr(current_user, "role"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No role assigned"
            )

        # check role
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission"
            )

        return current_user

    return permission_checker
