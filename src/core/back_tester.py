import csv
import os
import logging

from datetime import datetime, timedelta
from core.OHLC_loader import LoadOHLC
from models.compact_markets import MarketCompat
from pprint import pprint
from api.kalshi_client import KalshiClient


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class BackTester:
    MAX_EVENTS_PER_REQUEST = 200

    def __init__(
        self,
        api_client: KalshiClient,
        num_markets: int = 100,
    ):
        self.all_events: list[dict] = []
        self.all_markets: list[dict] = []
        self.api_client = api_client
        self.start_date = datetime.today() - timedelta(days=500)

    def run_back_test(
        self,
        reuse_data: bool = True,
    ):

        # load from cached runs if reuse_data true
        self.load_new_market_data()
        self.write_date_to_csv()

        loader = LoadOHLC(self.api_client.marketAPI)
        random_market = MarketCompat(
            event_ticker="KXNFLGAME-25OCT16PITCIN",
            series_ticker="KXNFLGAME",
            market_ticker="KXNFLGAME-25OCT16PITCIN-PIT",
            start_ts=int("1759949940"),
            end_ts=int("1761869700"),
        )
        loader.load_OHLC(market=random_market)

    def load_new_market_data(self, series_ticker: str = "KXNFLGAME") -> list[dict]:
        # load the first 200 nfl events from the past year
        cursor, events = self.api_client.marketAPI.get_events(
            limit=BackTester.MAX_EVENTS_PER_REQUEST,
            include_markets=True,
            series_ticker=series_ticker,
            min_close_ts=int(self.start_date.timestamp()),
        )
        # append to list
        self.all_events.extend(events)

        # get the rest of the events until you can't find anymore events fro the year
        while len(events) != 0 and len(cursor) != 0:
            if len(events) >= 1000:
                logger.warning("Hard limit on events number reached (1000)")
            cursor, events = self.api_client.marketAPI.get_events(
                limit=BackTester.MAX_EVENTS_PER_REQUEST,
                series_ticker=series_ticker,
                include_markets=True,
                cursor=cursor,
                min_close_ts=int(self.start_date.timestamp()),
            )

        current_date = datetime.today()

        # TODO: this might be memory inefficient by who cares rn
        tb_removed = set()
        logger.info(
            f"Processing {len(self.all_events)} events | Filtering active markets..."
        )

        for event in self.all_events:
            for market in event["markets"]:
                market_close_time = datetime.fromisoformat(
                    market["close_time"]
                ).replace(tzinfo=None)
                if (
                    current_date < market_close_time
                    or market["market_type"] != "binary"
                ):
                    tb_removed.add(event["event_ticker"])

        # filter the tb_removed
        self.all_events = list(
            filter(lambda x: x["event_ticker"] not in tb_removed, self.all_events)
        )
        logger.info(
            f"Filtered to {len(self.all_events)} closed events ({len(tb_removed)} active events removed)"
        )

        return self.all_events

    def write_date_to_csv(self):
        logger.info("Writing data to CSV files...")
        # TODO: there has to be a better way to part nested dict, i want a lang that is typed so bad
        # extract markets
        for event in self.all_events:
            for m in event["markets"]:
                m["event_ticker"] = event["event_ticker"]
                m["series_ticker"] = event["series_ticker"]
                del m["early_close_condition"]
                del m["previous_price_dollars"]
                del m["rules_secondary"]
                m = {k: v for k, v in m.items() if type(m[k]) is not dict}
                self.all_markets.append(m)

        # create market_data folder
        directory_name = "data"

        try:
            os.mkdir(directory_name)
        except FileExistsError:
            logger.info(f"Using existing '{directory_name}' directory")

        # write the events to csv
        event_csv_file_name = (
            "binary_events_" + str(datetime.today().strftime("%Y-%m-%dT%H")) + ".csv"
        )

        writeable_event_keys = [
            "category",
            "collateral_return_type",
            "event_ticker",
            "mutually_exclusive",
            "series_ticker",
            "sub_title",
            "title",
            "available_on_brokers",
        ]

        with open(os.path.join(directory_name, event_csv_file_name), "w") as f:
            f.write(",".join(writeable_event_keys))
            f.write("\n")
            for e in self.all_events:
                for k in writeable_event_keys:
                    f.write(str(e[k]) + ",")
                f.write("\n")

        logger.info(
            f"Events written to: {os.path.join(directory_name, event_csv_file_name)}"
        )

        # write markets to csv
        markets_csv_file_name = (
            "binary_markets_" + str(datetime.today().strftime("%Y-%m-%dT%H")) + ".csv"
        )
        with open(os.path.join(directory_name, markets_csv_file_name), "w") as f:
            w = csv.DictWriter(f, self.all_markets[0].keys())
            w.writeheader()
            for m in self.all_markets:
                w.writerow(m)

        logger.info(
            f"Markets written to: {os.path.join(directory_name, markets_csv_file_name)}"
        )
        logger.info(
            f"Backtest data export complete! ({len(self.all_events)} events, {len(self.all_markets)} markets)"
        )
