from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request

from app.core.permissions import require_permission
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token
from app.core.deps import get_current_user, get_current_admin
from app.core.jwt import create_email_verification_token
from jose import jwt, JWTError
from app.core.config import settings
from app.core.jwt import create_password_reset_token
from jose import jwt, JWTError
from app.core.config import settings
from slowapi.util import get_remote_address
from slowapi import Limiter
from fastapi import Request
from app.core.logger import log_info, log_error
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

# ---------------- REGISTER ----------------
@router.post("/register", response_model=UserOut, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    verification_token = create_email_verification_token(
    data={"sub": user.email}
)

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role if user.role else "user",
        verification_token=verification_token,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    print("\n==== EMAIL VERIFICATION LINK ====")
    print(f"http://127.0.0.1:8000/users/verify-email?token={verification_token}")
    db.refresh(new_user)

    return new_user


# ---------------- LOGIN ----------------

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not db_user.is_verified:
       raise HTTPException(
           status_code=403,
           detail="Please verify your email first"
    )
    if db_user.is_blocked:
      raise HTTPException(status_code=403, detail="Account blocked by admin")

    log_info(f"User logged in: {db_user.email}")
    log_error("Failed login attempt")

    access_token = create_access_token(
        data={"sub": str(db_user.id)}
    )

    refresh_token = create_refresh_token(
        data={"sub": str(db_user.id)}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=400, detail="Token expired or invalid")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    user.verification_token = None

    db.commit()

    return {"message": "Email verified successfully"}


# ---------------- CURRENT USER ----------------
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }


# ---------------- ADMIN CHECK ----------------
@router.get("/admin")
def admin_only(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    return {"message": "Welcome admin"}


# ---------------- ADMIN VIA DEP ----------------
@router.get("/admin-only")
def admin_data(admin: User = Depends(get_current_admin)):
    return {"message": f"Welcome Admin {admin.email}"}

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_password_reset_token(data={"sub": user.email})
    user.reset_token = reset_token
    db.commit()

    print("\n==== PASSWORD RESET LINK ====")
    print(f"http://127.0.0.1:8000/users/reset-password?token={reset_token}")
    print("=============================\n")

    return {"message": "Password reset link sent"}

@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=400, detail="Token expired or invalid")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(new_password)
    user.reset_token = None

    db.commit()

    return {"message": "Password reset successful"}

# ---------------- USER DASHBOARD ----------------
@router.get("/dashboard")
def user_dashboard(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Welcome {current_user.email}",
        "role": current_user.role
    }


# ---------------- ADMIN DASHBOARD ----------------
@router.get("/admin/dashboard")
def admin_dashboard(admin: User = Depends(get_current_admin)):
    return {
        "message": f"Admin panel for {admin.email}",
        "controls": [
            "View all users",
            "Delete users",
            "Block users",
            "View logs"
        ]
    }

# ---------------- VIEW ALL USERS (ADMIN) ----------------
@router.get("/all-users")
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    users = db.query(User).all()

    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "active": u.is_active,
            "blocked": u.is_blocked
        }
        for u in users
    ]

# ---------------- BLOCK USER ----------------
@router.put("/block/{user_id}")
def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_blocked = True
    db.commit()

    return {"message": f"User {user.email} blocked"}

# ---------------- DELETE USER ----------------
@router.delete("/delete/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}
@router.get("/super-admin")
def super_admin_data(
    user = Depends(require_permission("delete_user"))
):
    return {"message": "You have delete_user permission"}