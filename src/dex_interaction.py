from solana.rpc.api import Client
from solana.transaction import Transaction
import logging
from typing import Optional
from . import config
from .wallet import SolanaWallet

class DexInteraction:
    def __init__(self, wallet: SolanaWallet):
        self.wallet = wallet
        self.client = Client(config.SOLANA_RPC_URL)

    def _build_swap_transaction(self, dex_address: str, amount: float, is_buy: bool) -> Optional[Transaction]:
        try:
            recent_blockhash = self.client.get_recent_blockhash()['result']['value']['blockhash']
            
            transaction = Transaction()
            transaction.recent_blockhash = recent_blockhash
            transaction.fee_payer = self.wallet.keypair.public_key
            
            return transaction
        except Exception as e:
            logging.error(f"Failed to build swap transaction: {str(e)}")
            return None

    def execute_swap(self, dex_address: str, amount: float, is_buy: bool) -> bool:
        try:
            transaction = self._build_swap_transaction(dex_address, amount, is_buy)
            if not transaction:
                return False

            signed_transaction = self.wallet.sign_transaction(transaction)
            tx_hash = self.wallet.send_transaction(signed_transaction)
            
            confirmation = self.client.confirm_transaction(tx_hash)
            if confirmation['result']:
                logging.info(f"Swap {'buy' if is_buy else 'sell'} successful on {dex_address}")
                return True
            else:
                logging.error(f"Swap failed on {dex_address}")
                return False

        except Exception as e:
            logging.error(f"Failed to execute swap: {str(e)}")
            return False

    def check_liquidity(self, dex_address: str, amount: float) -> bool:
        try:
            return True
        except Exception as e:
            logging.error(f"Failed to check liquidity: {str(e)}")
            return False