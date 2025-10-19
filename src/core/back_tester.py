import csv
import os
import sys
import time

from datetime import datetime, timedelta
from core.OHLC_loader import LoadOHLC
from models.compact_markets import MarketCompat
from pprint import pprint
from api.kalshi_client import KalshiClient


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
        print(f"\n{'='*60}")
        print(f"LOADING MARKET DATA")
        print(
            f"Series: {series_ticker} | Start date: {self.start_date.strftime('%Y-%m-%d')}"
        )
        print(f"{'='*60}\n")

        api_start = time.time()

        # load the first 200 nfl events from the past year
        print("Fetching initial batch of events...")
        cursor, events = self.api_client.marketAPI.get_events(
            limit=BackTester.MAX_EVENTS_PER_REQUEST,
            include_markets=True,
            series_ticker=series_ticker,
            min_close_ts=int(self.start_date.timestamp()),
        )
        # append to list
        self.all_events.extend(events)
        print(f"Initial batch: {len(events)} events loaded\n")

        # get the rest of the events until you can't find anymore events fro the year
        batch_num = 1
        while len(events) != 0 and len(cursor) != 0:
            if len(events) >= 1000:
                print(f"\n[WARNING] Hard limit on events number reached (1000)\n")
                break

            sys.stdout.write(f"\rFetching batch {batch_num}...")
            sys.stdout.flush()

            cursor, events = self.api_client.marketAPI.get_events(
                limit=BackTester.MAX_EVENTS_PER_REQUEST,
                series_ticker=series_ticker,
                include_markets=True,
                cursor=cursor,
                min_close_ts=int(self.start_date.timestamp()),
            )

            if len(events) > 0:
                self.all_events.extend(events)
                sys.stdout.write(
                    f" | {len(events)} events | Total: {len(self.all_events)}"
                )
                sys.stdout.flush()
                batch_num += 1

        if batch_num > 1:
            print()  # New line after progress

        api_elapsed = time.time() - api_start
        print(
            f"\nAPI fetch complete: {len(self.all_events)} total events | Time: {api_elapsed:.2f}s\n"
        )

        current_date = datetime.today()

        # TODO: this might be memory inefficient by who cares rn
        tb_removed = set()
        print(f"Processing {len(self.all_events)} events...")
        print("Filtering active markets...\n")

        filter_start = time.time()

        for idx, event in enumerate(self.all_events, 1):
            if idx % 10 == 0 or idx == len(self.all_events):
                progress = idx / len(self.all_events)
                bar_length = 40
                filled = int(bar_length * progress)
                bar = "#" * filled + "-" * (bar_length - filled)
                sys.stdout.write(f"\rFiltering [{bar}] {idx}/{len(self.all_events)}")
                sys.stdout.flush()

            for market in event["markets"]:
                market_close_time = datetime.fromisoformat(
                    market["close_time"]
                ).replace(tzinfo=None)
                if (
                    current_date < market_close_time
                    or market["market_type"] != "binary"
                ):
                    tb_removed.add(event["event_ticker"])

        print()  # New line after progress bar

        # filter the tb_removed
        self.all_events = list(
            filter(lambda x: x["event_ticker"] not in tb_removed, self.all_events)
        )

        filter_elapsed = time.time() - filter_start
        print(
            f"\nFiltered to {len(self.all_events)} closed events | Removed: {len(tb_removed)} active | Time: {filter_elapsed:.2f}s\n"
        )

        return self.all_events

    def write_date_to_csv(self):
        print(f"{'='*60}")
        print("WRITING DATA TO CSV")
        print(f"{'='*60}\n")

        write_start = time.time()

        # TODO: there has to be a better way to part nested dict, i want a lang that is typed so bad
        # extract markets
        print("Extracting market data from events...\n")
        extract_start = time.time()

        for idx, event in enumerate(self.all_events, 1):
            if idx % 10 == 0 or idx == len(self.all_events):
                progress = idx / len(self.all_events)
                bar_length = 40
                filled = int(bar_length * progress)
                bar = "#" * filled + "-" * (bar_length - filled)
                sys.stdout.write(f"\rExtracting [{bar}] {idx}/{len(self.all_events)}")
                sys.stdout.flush()

            for m in event["markets"]:
                m["event_ticker"] = event["event_ticker"]
                m["series_ticker"] = event["series_ticker"]
                del m["early_close_condition"]
                del m["previous_price_dollars"]
                del m["rules_secondary"]
                m = {k: v for k, v in m.items() if type(m[k]) is not dict}
                self.all_markets.append(m)

        print()  # New line after progress bar
        extract_elapsed = time.time() - extract_start
        print(
            f"Extracted {len(self.all_markets)} markets | Time: {extract_elapsed:.2f}s\n"
        )

        # create market_data folder
        directory_name = "data"

        try:
            os.mkdir(directory_name)
        except FileExistsError:
            print(f"Using existing '{directory_name}' directory\n")

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

        print("Writing events to CSV...")
        events_write_start = time.time()

        with open(os.path.join(directory_name, event_csv_file_name), "w") as f:
            f.write(",".join(writeable_event_keys))
            f.write("\n")
            for e in self.all_events:
                for k in writeable_event_keys:
                    f.write(str(e[k]) + ",")
                f.write("\n")

        events_write_elapsed = time.time() - events_write_start
        print(f"Events file: {os.path.join(directory_name, event_csv_file_name)}")
        print(f"Time: {events_write_elapsed:.2f}s\n")

        # write markets to csv
        markets_csv_file_name = (
            "binary_markets_" + str(datetime.today().strftime("%Y-%m-%dT%H")) + ".csv"
        )

        print("Writing markets to CSV...")
        markets_write_start = time.time()

        with open(os.path.join(directory_name, markets_csv_file_name), "w") as f:
            w = csv.DictWriter(f, self.all_markets[0].keys())
            w.writeheader()
            for m in self.all_markets:
                w.writerow(m)

        markets_write_elapsed = time.time() - markets_write_start
        print(f"Markets file: {os.path.join(directory_name, markets_csv_file_name)}")
        print(f"Time: {markets_write_elapsed:.2f}s\n")

        total_elapsed = time.time() - write_start
        print(f"{'='*60}")
        print(
            f"EXPORT COMPLETE | Events: {len(self.all_events)} | Markets: {len(self.all_markets)} | Time: {total_elapsed:.2f}s"
        )
        print(f"{'='*60}\n")
