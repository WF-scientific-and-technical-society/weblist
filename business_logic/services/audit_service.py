import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

class AuditLogger:
    def __init__(self, log_file: str = "audit.log"):
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_operation(
        self,
        user_role: str,
        operation: str,
        path: str,
        details: Optional[Dict[str, Any]] = None,
        ip: str = None
    ) -> None:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_role": user_role,
            "operation": operation,
            "path": path,
            "ip": ip or "unknown",
            "details": details or {}
        }
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_login(self, username: str, success: bool, ip: str = None) -> None:
        self.log_operation(
            user_role="system",
            operation="login" if success else "login_failed",
            path="/auth",
            details={"username": username, "success": success},
            ip=ip
        )
    
    def log_file_operation(
        self,
        user_role: str,
        operation: str,
        file_path: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
        ip: str = None
    ) -> None:
        log_details = {"success": success}
        if details:
            log_details.update(details)
        self.log_operation(user_role, operation, file_path, log_details, ip)
    
    def log_config_change(
        self,
        user_role: str,
        section: str,
        changes: Dict[str, Any],
        ip: str = None
    ) -> None:
        self.log_operation(
            user_role=user_role,
            operation="config_update",
            path=f"/config/{section}",
            details={"changes": changes},
            ip=ip
        )
    
    def get_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        start_time: str = None,
        end_time: str = None,
        operation: str = None
    ) -> Dict[str, Any]:
        try:
            log_file = self.logger.handlers[0].baseFilename if self.logger.handlers else "audit.log"
            if not os.path.exists(log_file):
                return {"logs": [], "total": 0, "page": page, "page_size": page_size}
            
            logs = []
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        parts = line.split(' - ', 3)
                        if len(parts) >= 4:
                            log_data = json.loads(parts[3])
                            logs.append({
                                "timestamp": parts[0],
                                "level": parts[2],
                                **log_data
                            })
                    except (json.JSONDecodeError, IndexError):
                        continue
            
            if start_time:
                logs = [l for l in logs if l.get("timestamp", "") >= start_time]
            if end_time:
                logs = [l for l in logs if l.get("timestamp", "") <= end_time]
            if operation:
                logs = [l for l in logs if l.get("operation") == operation]
            
            logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            total = len(logs)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            return {
                "logs": logs[start_idx:end_idx],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            return {"logs": [], "total": 0, "error": str(e)}

class UsageStatistics:
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
    
    def get_storage_stats(self, file_list: Dict[str, Any]) -> Dict[str, Any]:
        try:
            stats = {
                "total_files": 0,
                "total_folders": 0,
                "total_size": 0,
                "file_types": {},
                "largest_files": [],
                "recent_files": []
            }
            
            for item in file_list.get("files", []):
                stats["total_files"] += 1
                size = item.get("size", 0)
                stats["total_size"] += size
                
                ext = item.get("extension", "")
                stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                
                stats["largest_files"].append({
                    "name": item.get("name"),
                    "size": size
                })
            
            stats["total_folders"] = len(file_list.get("folders", []))
            
            stats["largest_files"] = sorted(
                stats["largest_files"],
                key=lambda x: x.get("size", 0),
                reverse=True
            )[:10]
            
            return {"success": True, "data": stats}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_operation_stats(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            stats = {
                "total_operations": len(logs),
                "operations_by_type": {},
                "operations_by_user": {},
                "errors": 0
            }
            
            for log in logs:
                op = log.get("operation", "unknown")
                stats["operations_by_type"][op] = stats["operations_by_type"].get(op, 0) + 1
                
                user = log.get("user_role", "unknown")
                stats["operations_by_user"][user] = stats["operations_by_user"].get(user, 0) + 1
                
                if not log.get("details", {}).get("success", True):
                    stats["errors"] += 1
            
            return {"success": True, "data": stats}
        except Exception as e:
            return {"success": False, "error": str(e)}
