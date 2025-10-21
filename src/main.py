import asyncio
import aiohttp
import os
import logging


from core.back_tester import BackTester, LoadOHLC
from api.kalshi_client import KalshiClient
from utils.helpers import *
from dotenv import load_dotenv

# Load environment variables from the .env file (if present)
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
API_KEY_ID = os.getenv("API_KEY_ID")
request_header = get_header(api_key_id=API_KEY_ID, key_path=PRIVATE_KEY_PATH)


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    market_client = KalshiClient(base_url=BASE_URL, header=request_header)
    loader = LoadOHLC(market_client.marketAPI)
    ## past your kalshi.com link here
    loader.find_load_OHLC(
        "https://kalshi.com/markets/kxsongsoncharttswift2/talor-swift-holds-top-2/kxsongsoncharttswift2-25oct25"
    )


if __name__ == "__main__":
    main()
