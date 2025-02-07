import time
from functools import wraps
import logging
from typing import Any, Callable
from . import config

def retry_on_failure(max_retries: int = None, delay: int = None) -> Callable:
    max_attempts = max_retries or config.MAX_RETRIES
    retry_delay = delay or config.RETRY_DELAY

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        logging.error(f"Max retries ({max_attempts}) reached for {func.__name__}: {str(e)}")
                        raise
                    logging.warning(f"Attempt {attempts}/{max_attempts} failed for {func.__name__}: {str(e)}")
                    time.sleep(retry_delay)
            return None
        return wrapper
    return decorator

def format_amount(amount: float, decimals: int = 8) -> str:
    return f"{amount:.{decimals}f}"

def calculate_gas_with_buffer(base_gas: float) -> float:
    return base_gas * config.GAS_ADJUSTMENT

def validate_address(address: str) -> bool:
    try:
        return len(address) == 44 or len(address) == 43
    except Exception:
        return False

class RateLimiter:
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.timestamps = []

    def can_call(self) -> bool:
        now = time.time()
        self.timestamps = [t for t in self.timestamps if now - t < self.period]
        
        if len(self.timestamps) < self.calls:
            self.timestamps.append(now)
            return True
        return False

    def wait_if_needed(self):
        while not self.can_call():
            time.sleep(0.1)