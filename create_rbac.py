from app.database import SessionLocal
from app.models.rbac import Role, Permission

db = SessionLocal()

# create permissions
p1 = Permission(name="view_admin")
p2 = Permission(name="delete_user")
p3 = Permission(name="ban_user")

db.add_all([p1, p2, p3])
db.commit()

# create roles
admin = Role(name="admin")
user = Role(name="user")

db.add_all([admin, user])
db.commit()

# assign permissions to admin
admin.permissions.append(p1)
admin.permissions.append(p2)
admin.permissions.append(p3)

db.commit()

print("RBAC setup done")
