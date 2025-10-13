import csv

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from controller.kalshi_client import KalshiClient


class BackTester:
    def __init__(
        self,
        api_client: KalshiClient,
        num_markets: int = 100,
        market_type: str = "binary",
        market_category: str = "Sport",
    ):
        self.markets: list[dict] = []
        self.market_type = market_type
        self.num_markets = num_markets
        self.market_category = market_category
        self.api_client = api_client
        self.start_date = datetime.today() - timedelta(days=365)

    def run_back_test(
        self,
        reuse_data: bool = True,
        custom_date: datetime = None,
    ):
        if custom_date != None:
            self.start_date = custom_date
        # load from cached runs if reuse_data true

        self._load_new_market_data()
        pass

    def _load_new_market_data(self):
        all_events = []
        cursor, events = self.api_client.marketAPI.get_events(
            limit=200,
            with_nested_markets=True,
            series_ticker="KXNFLGAME",
            min_close_ts=int(self.start_date.timestamp()),
            status="closed",
        )
        all_events.extend(events)
        print(len(all_events))

        while len(events) != 0:
            cursor, events = self.api_client.marketAPI.get_events(
                limit=200,
                with_nested_markets=True,
                series_ticker="KXNFLGAME",
                cursor=cursor,
                min_close_ts=int(self.start_date.timestamp()),
                status="closed",
            )

            all_events.extend(events)
            print(len(all_events))
        high = (datetime.today() - timedelta(days=1)).replace(tzinfo=None)
        low = (datetime.today() - timedelta(days=30)).replace(tzinfo=None)

        for e in all_events:
            if "markets" in e:
                for market in e["markets"]:

                    # self.markets.append(market["close_time"])
                    cur_date = datetime.fromisoformat(market["close_time"]).replace(
                        tzinfo=None
                    )
                    if cur_date > low and cur_date <= high:
                        print(
                            "this: ",
                            market["close_time"],
                            e["title"],
                            e["series_ticker"],
                        )
