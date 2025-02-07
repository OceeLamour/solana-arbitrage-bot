import pytest
import time
from src.utils import retry_on_failure, format_amount, calculate_gas_with_buffer, validate_address, RateLimiter

def test_retry_on_failure():
    @retry_on_failure(max_retries=3, delay=0)
    def failing_function():
        raise Exception("Test failure")
    
    with pytest.raises(Exception):
        failing_function()

def test_format_amount():
    assert format_amount(1.23456789, 2) == "1.23"
    assert format_amount(1.23456789, 4) == "1.2346"
    assert format_amount(1.23456789, 8) == "1.23456789"

def test_calculate_gas_with_buffer():
    assert calculate_gas_with_buffer(1.0) > 1.0

def test_validate_address():
    # Test valid address length
    assert validate_address("x" * 44)
    assert validate_address("x" * 43)
    
    # Test invalid address length
    assert not validate_address("x" * 42)
    assert not validate_address("x" * 45)

def test_rate_limiter():
    limiter = RateLimiter(calls=2, period=1)
    
    # First two calls should succeed
    assert limiter.can_call()
    assert limiter.can_call()
    
    # Third call should fail
    assert not limiter.can_call()
    
    # Wait for period to expire
    time.sleep(1)
    
    # Should be able to call again
    assert limiter.can_call()