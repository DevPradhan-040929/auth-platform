from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base
from sqlalchemy.orm import relationship
from app.models.rbac import user_roles
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # user | admin
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)   # user active?
    is_blocked = Column(Boolean, default=False) # banned?
fake_users_db = {}

roles = relationship(
    "Role",
    secondary=user_roles,
    backref="users"
)