class UserRole:
    ADMIN = "admin"
    USER = "user"
    
class Permission:
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"

# 角色权限映射
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.SHARE, Permission.ADMIN],
    UserRole.USER: [Permission.READ]
}

def check_permission(user_role, required_permission):
    """验证用户是否拥有所需权限"""
    return required_permission in ROLE_PERMISSIONS.get(user_role, [])
