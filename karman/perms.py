from karman.models.auth import register_permissions

MANAGE_USERS = "manage users"
MANAGE_PERMISSIONS = "manage permissions"

register_permissions(MANAGE_USERS)
register_permissions(MANAGE_PERMISSIONS)
