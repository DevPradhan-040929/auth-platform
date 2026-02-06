from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# ---------------- ROLE TABLE ----------------
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles"
    )


# ---------------- PERMISSION TABLE ----------------
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions"
    )


# ---------------- ROLE-PERMISSION LINK ----------------
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id")),
    Column("permission_id", Integer, ForeignKey("permissions.id")),
)


# ---------------- USER-ROLE LINK ----------------
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
)
