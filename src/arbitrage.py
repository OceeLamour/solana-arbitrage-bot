import logging
import time
from typing import Tuple
from . import config
from .price_feed import PriceFeed
from .dex_interaction import DexInteraction
from .wallet import SolanaWallet

class ArbitrageBot:
    def __init__(self):
        self.price_feed = PriceFeed()
        self.wallet = SolanaWallet()
        self.dex = DexInteraction(self.wallet)
        self.consecutive_errors = 0
        self.last_error_time = 0

    def _calculate_profit(self, buy_price: float, sell_price: float) -> float:
        """Calculate potential profit after fees and slippage"""
        gross_profit = (sell_price - buy_price) * config.TRADE_AMOUNT
        estimated_fees = (buy_price + sell_price) * config.TRADE_AMOUNT * 0.003
        return gross_profit - estimated_fees

    def _should_execute_trade(self, profit: float, buy_dex: str) -> bool:
        """Determine if a trade should be executed based on various criteria"""
        if profit <= config.MIN_PROFIT_THRESHOLD:
            return False

        balance = self.wallet.get_balance()
        if balance is None or balance < config.TRADE_AMOUNT:
            logging.warning("Insufficient balance for trade")
            return False

        if not self.dex.check_liquidity(buy_dex, config.TRADE_AMOUNT):
            logging.warning(f"Insufficient liquidity on {buy_dex}")
            return False

        return True

    def execute_arbitrage(self, buy_dex: str, sell_dex: str) -> bool:
        """Execute the arbitrage trades"""
        try:
            if not self.dex.execute_swap(buy_dex, config.TRADE_AMOUNT, True):
                logging.error("Buy trade failed")
                return False

            if not self.dex.execute_swap(sell_dex, config.TRADE_AMOUNT, False):
                logging.error("Sell trade failed")
                return False

            logging.info(f"Arbitrage successfully executed between {buy_dex} and {sell_dex}")
            return True

        except Exception as e:
            logging.error(f"Failed to execute arbitrage: {str(e)}")
            return False

    def _handle_error(self, error: Exception):
        """Handle errors and implement cooldown if needed"""
        self.consecutive_errors += 1
        current_time = time.time()
        
        if self.consecutive_errors >= config.MAX_CONSECUTIVE_ERRORS:
            if current_time - self.last_error_time < config.ERROR_COOLDOWN_PERIOD:
                logging.error(f"Too many consecutive errors. Entering cooldown for {config.ERROR_COOLDOWN_PERIOD} seconds")
                time.sleep(config.ERROR_COOLDOWN_PERIOD)
            self.consecutive_errors = 0
            self.last_error_time = current_time

        logging.error(f"Error occurred: {str(error)}")

    def check_opportunity(self) -> bool:
        """Check for and execute arbitrage opportunities"""
        try:
            raydium_price, orca_price = self.price_feed.get_prices()
            
            if raydium_price is None or orca_price is None:
                logging.warning("Failed to get prices from one or both DEXes")
                return False

            raydium_to_orca_profit = self._calculate_profit(raydium_price, orca_price)
            orca_to_raydium_profit = self._calculate_profit(orca_price, raydium_price)

            if raydium_to_orca_profit > orca_to_raydium_profit and self._should_execute_trade(raydium_to_orca_profit, config.RAYDIUM_ROUTER_ADDRESS):
                logging.info(f"Executing Raydium -> Orca arbitrage (Profit: {raydium_to_orca_profit})")
                return self.execute_arbitrage(config.RAYDIUM_ROUTER_ADDRESS, config.ORCA_ROUTER_ADDRESS)

            elif orca_to_raydium_profit > raydium_to_orca_profit and self._should_execute_trade(orca_to_raydium_profit, config.ORCA_ROUTER_ADDRESS):
                logging.info(f"Executing Orca -> Raydium arbitrage (Profit: {orca_to_raydium_profit})")
                return self.execute_arbitrage(config.ORCA_ROUTER_ADDRESS, config.RAYDIUM_ROUTER_ADDRESS)

            return False

        except Exception as e:
            self._handle_error(e)
            return False

    def run(self):
        """Main bot loop"""
        logging.info("Starting arbitrage bot...")
        
        while True:
            try:
                self.check_opportunity()
                time.sleep(config.PRICE_CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logging.info("Stopping arbitrage bot...")
                break
                
            except Exception as e:
                self._handle_error(e)
                continue