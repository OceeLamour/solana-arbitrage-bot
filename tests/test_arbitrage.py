import pytest
from src.arbitrage import ArbitrageBot
from src.config import *

def test_calculate_profit():
    bot = ArbitrageBot()
    
    # Test positive profit scenario
    profit = bot._calculate_profit(1.0, 1.1)
    assert profit > 0
    
    # Test negative profit scenario
    profit = bot._calculate_profit(1.1, 1.0)
    assert profit < 0
    
    # Test zero profit scenario
    profit = bot._calculate_profit(1.0, 1.0)
    assert profit == 0

def test_should_execute_trade():
    bot = ArbitrageBot()
    
    # Test below minimum profit threshold
    assert not bot._should_execute_trade(0.0001, RAYDIUM_ROUTER_ADDRESS)
    
    # Test above minimum profit threshold
    assert bot._should_execute_trade(0.1, RAYDIUM_ROUTER_ADDRESS)

def test_handle_error():
    bot = ArbitrageBot()
    
    # Test error handling
    error = Exception("Test error")
    bot._handle_error(error)
    assert bot.consecutive_errors == 1
    
    # Test error cooldown
    for _ in range(MAX_CONSECUTIVE_ERRORS):
        bot._handle_error(error)
    assert bot.consecutive_errors == 0