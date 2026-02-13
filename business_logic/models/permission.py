from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"

ROLE_PERMISSIONS = {
    UserRole.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.SHARE, Permission.ADMIN],
    UserRole.USER: [Permission.READ, Permission.SHARE]
}

PROTECTED_PATHS = ["/config", "/admin", "/system", "/logs"]

@dataclass
class User:
    username: str
    role: UserRole
    
    def has_permission(self, permission: Permission) -> bool:
        return permission in ROLE_PERMISSIONS.get(self.role, [])

def check_permission(user_role: UserRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(user_role, [])

def validate_path_access(user_role: UserRole, path: str) -> bool:
    if user_role == UserRole.ADMIN:
        return True
    for protected_path in PROTECTED_PATHS:
        if path.startswith(protected_path):
            return False
    return True
