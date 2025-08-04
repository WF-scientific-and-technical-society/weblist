import os
import logging
from pathlib import Path
from config.settings import AppConfig
from ..models.permission import UserRole, Permission
from ..utils.permission_middleware import require_permission

logger = logging.getLogger(__name__)

class SecureFileService:
    def __init__(self, api_client, config=None):
        self.api = api_client
        self.config = config or AppConfig
        self.validator = FileValidator(self.config)
        self.audit_log = AuditLogger(self.config.AUDIT_LOG)

    @require_permission(Permission.WRITE)
    def secure_upload(self, user, file_obj, target_path):
        """安全文件上传"""
        try:
            if not self._validate_path(user.role, target_path):
                raise PermissionError("Path access denied")

            filename = secure_filename(file_obj.filename)
            filepath = Path(self.config.UPLOAD_FOLDER) / filename
            file_obj.save(filepath)

            validation = self.validator.validate(filepath)
            if not validation['valid']:
                os.remove(filepath)
                return {
                    "success": False,
                    "errors": validation['errors'],
                    "file": filename
                }

            result = self.api.upload(str(filepath), target_path)

            self.audit_log.log(
                action="upload",
                user=user.name,
                path=target_path,
                details={
                    "file": filename,
                    "size": os.path.getsize(filepath),
                    "status": "success" if result.success else "failed"
                }
            )

            os.remove(filepath)

            return {
                "success": True,
                "data": {
                    "id": result.file_id,
                    "path": target_path
                }
            }

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            self.audit_log.log(
                action="upload",
                user=user.name,
                path=target_path,
                details={
                    "error": str(e),
                    "status": "failed"
                }
            )
            raise

    def _validate_path(self, role, path):
        """验证路径权限"""
        if role == UserRole.ADMIN:
            return True

        blocked = ['/system', '/config']
        return not any(path.startswith(p) for p in blocked)
