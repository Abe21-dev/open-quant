import requests

from .base_adapter import BaseApiAdapter


class MarketsAPI(BaseApiAdapter):

    def __init__(self, base_url: str, header: str):
        return super().__init__(base_url, header)

    async def get_markets(
        self,
    ) -> dict:
        url = self.base_url + "markets"
        pass

    async def get_market(
        self,
        cursor: str = None,
        event_ticker: str = None,
        series_ticker: str = None,
        status: str = None,
        tickers: str = None,
        limit=100,
    ):
        params = {
            "limit": limit,
            "cursor": cursor,
            "event_ticker": event_ticker,
            "series_ticker": series_ticker,
            "status": status,
            "ticker": tickers,
        }
        params = dict(filter(lambda x: x[1] != None, params.items()))
        url = self.base_url + "markets"

    def get_events(
        self,
        limit: int = None,
        cursor: str = None,
        with_nested_markets: bool = None,
        status: str = None,
        series_ticker: str = None,
        min_close_ts: int = None,
    ):
        params = {
            "limit": limit,
            "cursor": cursor,
            "with_nested_markets": with_nested_markets,
            "series_ticker": series_ticker,
            "status": status,
            "min_close_ts": min_close_ts,
        }
        print(params["series_ticker"])
        params = dict(filter(lambda x: x[1] != None, params.items()))
        print(params)
        url = self.base_url + "events"

        resp = requests.get(url, params=params, headers=self.header).json()
        return resp["cursor"], resp["events"]
