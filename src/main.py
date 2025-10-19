import asyncio
import aiohttp
import os
import logging


from core.back_tester import BackTester
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
    tester = BackTester(market_client)
    tester.run_back_test()


if __name__ == "__main__":
    main()
