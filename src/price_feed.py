import requests
import logging
import time
from typing import Optional, Tuple
from . import config

class PriceFeed:
    def __init__(self):
        self.session = requests.Session()
        self.last_raydium_price = None
        self.last_orca_price = None
        self.last_update_time = 0

    def _get_raydium_price(self) -> Optional[float]:
        try:
            response = self.session.get(
                f"https://api.raydium.io/v2/main/price",
                params={"token": config.TOKEN_ADDRESS},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
        except Exception as e:
            logging.error(f"Failed to fetch Raydium price: {str(e)}")
            return None

    def _get_orca_price(self) -> Optional[float]:
        try:
            response = self.session.get(
                f"https://api.orca.so/v1/token/price",
                params={"token": config.TOKEN_ADDRESS},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
        except Exception as e:
            logging.error(f"Failed to fetch Orca price: {str(e)}")
            return None

    def get_prices(self) -> Tuple[Optional[float], Optional[float]]:
        current_time = time.time()
        
        if current_time - self.last_update_time < config.PRICE_CHECK_INTERVAL:
            return self.last_raydium_price, self.last_orca_price

        raydium_price = self._get_raydium_price()
        orca_price = self._get_orca_price()

        if raydium_price is not None:
            self.last_raydium_price = raydium_price
        if orca_price is not None:
            self.last_orca_price = orca_price
        self.last_update_time = current_time

        return raydium_price, orca_price

    def calculate_price_difference(self, price1: float, price2: float) -> float:
        if price1 <= 0 or price2 <= 0:
            return 0
        return abs(price1 - price2) / min(price1, price2) * 100