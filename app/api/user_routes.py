from fastapi import APIRouter, Depends
from app.core.roles import require_role

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/profile")
def user_profile(current_user = Depends(require_role("user"))):
    return {
        "message": f"Welcome User {current_user.email}"
    }
