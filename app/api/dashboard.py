from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_current_admin
from app.database import get_db
from app.models.user import User

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

# ---------------- USER DASHBOARD ----------------
@router.get("/user")
def user_dashboard(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Welcome {current_user.email}",
        "role": current_user.role,
        "dashboard": "User Dashboard"
    }

# ---------------- ADMIN DASHBOARD ----------------
@router.get("/admin")
def admin_dashboard(admin: User = Depends(get_current_admin)):
    return {
        "message": f"Welcome Admin {admin.email}",
        "dashboard": "Admin Dashboard"
    }

# ---------------- ADMIN: VIEW ALL USERS ----------------
@router.get("/admin/all-users")
def get_all_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role
        }
        for u in users
    ]

# ---------------- SUPER ADMIN ONLY ----------------
@router.delete("/superadmin/delete-user/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin only")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": f"User {user.email} deleted"}
