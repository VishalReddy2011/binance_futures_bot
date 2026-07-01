import os
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from bot.logging_config import logger

class BinanceFuturesClient:
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        
        if self.api_key:
            self.api_key = self.api_key.strip()
        if self.api_secret:
            self.api_secret = self.api_secret.strip()

        if not self.api_key or not self.api_secret:
            logger.error("API Key or Secret missing.")
            raise ValueError("Binance API Key and Secret are required.")

        try:
            logger.info("Connecting to Binance Testnet...")
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            
            # Simple server check
            server_time = self.client.futures_time()
            logger.info(f"Handshake successful. Server time: {server_time.get('serverTime')}")
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e.message} (code: {e.code})")
            raise ConnectionError(f"Binance API Error: {e.message}") from e
        except BinanceRequestException as e:
            logger.error(f"Network error: {str(e)}")
            raise ConnectionError(f"Network connection failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected setup error: {str(e)}")
            raise RuntimeError(f"Client setup failed: {str(e)}") from e

    def get_client(self) -> Client:
        return self.client
