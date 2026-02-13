from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class FileInfo:
    id: str
    name: str
    type: str
    size: int
    size_formatted: str
    modified: Optional[datetime] = None
    extension: str = ""
    path: str = ""
    download_url: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "size_formatted": self.size_formatted,
            "modified": self.modified.isoformat() if self.modified else None,
            "extension": self.extension,
            "path": self.path,
            "download_url": self.download_url
        }

@dataclass
class FolderInfo:
    id: str
    name: str
    path: str = ""
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": "folder",
            "path": self.path
        }

@dataclass
class UploadResult:
    success: bool
    message: str
    file_id: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        result = {"success": self.success, "message": self.message}
        if self.file_id:
            result["file_id"] = self.file_id
        if self.error:
            result["error"] = self.error
        return result
