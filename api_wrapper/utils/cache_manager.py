import time
import threading
from typing import Any, Optional, Dict
from collections import OrderedDict

class CacheManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, ttl: int = 300, max_size: int = 100):
        if not hasattr(self, '_initialized'):
            self._cache: OrderedDict = OrderedDict()
            self._ttl = ttl
            self._max_size = max_size
            self._initialized = True
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                self._cache.move_to_end(key)
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)
        self._cache[key] = (value, time.time())
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        self._cache.clear()
    
    def exists(self, key: str) -> bool:
        return self.get(key) is not None
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "ttl": self._ttl
        }
    
    def invalidate_pattern(self, pattern: str) -> int:
        keys_to_delete = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self._cache[key]
        return len(keys_to_delete)
    
    def get_or_set(self, key: str, factory: callable) -> Any:
        value = self.get(key)
        if value is None:
            value = factory()
            if value is not None:
                self.set(key, value)
        return value

file_list_cache = CacheManager(ttl=300, max_size=50)
config_cache = CacheManager(ttl=60, max_size=10)
