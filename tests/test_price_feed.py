import pytest
from src.price_feed import PriceFeed

def test_price_feed_initialization():
    price_feed = PriceFeed()
    assert price_feed is not None
    assert price_feed.last_raydium_price is None
    assert price_feed.last_orca_price is None

def test_get_prices():
    price_feed = PriceFeed()
    raydium_price, orca_price = price_feed.get_prices()
    
    # Prices should either be None or positive numbers
    if raydium_price is not None:
        assert raydium_price > 0
    if orca_price is not None:
        assert orca_price > 0

def test_calculate_price_difference():
    price_feed = PriceFeed()
    
    # Test normal case
    diff = price_feed.calculate_price_difference(1.1, 1.0)
    assert diff == 10.0
    
    # Test equal prices
    diff = price_feed.calculate_price_difference(1.0, 1.0)
    assert diff == 0.0
    
    # Test zero price handling
    diff = price_feed.calculate_price_difference(0, 1.0)
    assert diff == 0.0