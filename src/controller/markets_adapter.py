import requests
import aiohttp
import asyncio

from aiohttp import ClientSession
from .kalshi_api_adapter import KalshiApiAdapter


class MarketsAPI(KalshiApiAdapter):

    def __init__(self, base_url: str, header: str):
        return super().__init__(base_url, header)

    async def get_markets(
        self,
        client_session: ClientSession,
    ) -> dict:
        url = self.base_url + "markets"
        print(url)
        async with client_session as session:
            async with session.get(
                url, headers=self.header, params={"limit": 30, "status": "open"}
            ) as resp:
                res_dict = await resp.json()
        return res_dict

    async def get_market(self, client_session: ClientSession, ticker: str, params={}):
        url = self.base_url + "markets/" + ticker
        async with client_session as session:
            async with session.get(
                url, headers=self.header, params={"limit": 10}
            ) as resp:
                res_text = await resp.text()

    async def get_market_order_book(self, client_session: ClientSession, ticker: str):
        url = self.base_url + "markets/" + ticker + "/orderbook/"
        async with client_session as session:
            async with session.get(url, headers=self.header) as resp:
                return await resp.json()
