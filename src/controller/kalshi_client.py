from aiohttp import ClientSession
from .markets_adapter import MarketsAPI


class KalshiClient:
    def __init__(self, base_url: str, header: dict):
        self.marketAPI = MarketsAPI(base_url, header)
