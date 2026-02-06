from fastapi import APIRouter, HTTPException, status, Depends
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.config import settings
from app.core.jwt import create_access_token
from app.models.user import User
from fastapi.security import OAuth2PasswordBearer
from app.models.token_blacklist import TokenBlacklist
router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


# ---------------- REFRESH TOKEN ----------------
@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    blacklisted = TokenBlacklist(token=token)
    db.add(blacklisted)
    db.commit()

    return {"message": "Logged out successfully"}