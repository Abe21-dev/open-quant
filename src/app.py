import asyncio
import aiohttp
import os


from controller.markets_adapter import MarketsAPI
from controller.kalshi_api_adapter import KalshiApiAdapter
from utils import *
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables from the .env file (if present)
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
API_KEY_ID = os.getenv("API_KEY_ID")
request_header = get_header(api_key_id=API_KEY_ID, key_path=PRIVATE_KEY_PATH)


async def main():
    market_client = MarketsAPI(base_url=BASE_URL, header=request_header)
    async with aiohttp.ClientSession() as session:
        market_info = await market_client.get_market_order_book(
            session, "KXNFLGAME-25OCT12DENNYJ-NYJ"
        )
        pprint(market_info)


if __name__ == "__main__":
    asyncio.run(main())
