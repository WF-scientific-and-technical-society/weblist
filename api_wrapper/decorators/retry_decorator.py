import time
import functools
from typing import Callable, Any, Tuple, Type

def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            raise last_exception
        return wrapper
    return decorator

class RetryDecorator:
    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = self.delay
            
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        time.sleep(current_delay)
                        current_delay *= self.backoff
            
            raise last_exception
        return wrapper

ERROR_MAPPING = {
    401: "认证失败，请检查API密钥",
    403: "权限不足，无法访问",
    404: "文件或目录不存在",
    429: "请求过于频繁，请稍后再试",
    500: "服务器内部错误",
    503: "服务暂时不可用"
}

def get_error_message(code: int) -> str:
    return ERROR_MAPPING.get(code, f"未知错误: {code}")
