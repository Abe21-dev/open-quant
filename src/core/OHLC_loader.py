import os
import csv
import sys
import time

from datetime import date, datetime, timedelta
from pprint import pprint
from models.compact_markets import MarketCompat
from api.kalshi_client import MarketsAPI


class LoadOHLC:
    def __init__(self, marketAPI: MarketsAPI):
        self.period_interval = 1
        self.marketAPI = marketAPI

    def find_load_OHLC(self, kalshi_url: str):
        event_id = kalshi_url.split("/")[-1].upper()
        print(event_id)
        code, resp = self.marketAPI.get_event(event_id)
        if code != 200:
            raise Exception("Invalid event id")
        pprint(resp)
        start_ts = datetime.today() - timedelta(days=5)
        start_ts = int(start_ts.timestamp())
        end_ts = int(datetime.today().timestamp())
        market = MarketCompat(
            resp["event"]["event_ticker"],
            resp["event"]["series_ticker"],
            resp["markets"][0]["ticker"],
            start_ts,
            end_ts,
        )
        self.load_OHLC(market)

    def load_OHLC(self, market: MarketCompat):
        time_intervals = self.__get_intervals(market)

        print(f"\n{'='*60}")
        print(f"Number of requests to get market OHLC: {len(time_intervals)}")
        print(f"{'='*60}\n")

        # API data loading with progress
        api_start = time.time()
        resp_json: dict[str, list] = None

        for idx, period in enumerate(time_intervals, 1):
            progress = idx / len(time_intervals)
            bar_length = 40
            filled = int(bar_length * progress)
            bar = "#" * filled + "-" * (bar_length - filled)

            sys.stdout.write(f"\rAPI Loading [{bar}] {idx}/{len(time_intervals)}")
            sys.stdout.flush()

            code, curr_resp_json = self.marketAPI.get_market_candle_stick(
                market.series_ticker,
                market.market_ticker,
                start_ts=period[0],
                end_ts=period[1],
            )

            if code != 200:
                break
            if resp_json is None:
                resp_json = curr_resp_json
            else:
                resp_json["candlesticks"].extend(curr_resp_json["candlesticks"])

            sys.stdout.write(f' | Records: {len(resp_json["candlesticks"])}')
            sys.stdout.flush()

        api_elapsed = time.time() - api_start
        print(f"\n{'='*60}")
        print(f"API data loaded: {len(resp_json['candlesticks'])} candlesticks")
        print(f"Time taken: {api_elapsed:.2f}s")
        print(f"{'='*60}\n")

        # JSON to CSV conversion
        print("Converting JSON to CSV...")
        convert_start = time.time()

        file_name = market.market_ticker + str(date.today()) + "_OHLC.csv"
        dir_name = "data"
        rows = self.__json_to_csv(resp_json, file_name)

        convert_elapsed = time.time() - convert_start
        print(f"Conversion complete: {len(rows)} rows | Time: {convert_elapsed:.2f}s\n")

        # Writing CSV file
        print("Writing to CSV file...")
        write_start = time.time()

        with open(os.path.join(dir_name, file_name), "w") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        write_elapsed = time.time() - write_start
        print(
            f"File written: {os.path.join(dir_name, file_name)} | Time: {write_elapsed:.2f}s"
        )

        total_elapsed = api_elapsed + convert_elapsed + write_elapsed
        print(f"\n{'='*60}")
        print(f"TOTAL TIME: {total_elapsed:.2f}s")
        print(f"{'='*60}\n")

    def __get_intervals(self, market: MarketCompat):
        periods = []
        for i in range(market.start_ts, market.end_ts, 4000):
            periods.append((i, i + 4000))

        return periods

    # this is the only code written by AI i was tired and didn't want to convert json to csv
    # this won't happen again
    def __json_to_csv(self, json_data: dict, output_file: str):
        """Convert candlestick JSON to Option 2 CSV format."""
        ticker = json_data["ticker"]
        rows = []

        total_candles = len(json_data["candlesticks"])
        for idx, candle in enumerate(json_data["candlesticks"], 1):
            if idx % 100 == 0 or idx == total_candles:
                progress = idx / total_candles
                bar_length = 40
                filled = int(bar_length * progress)
                bar = "#" * filled + "-" * (bar_length - filled)
                sys.stdout.write(f"\rProcessing [{bar}] {idx}/{total_candles}")
                sys.stdout.flush()

            date = datetime.fromtimestamp(candle["end_period_ts"])

            row = {
                "market_ticker": ticker,
                "date": str(date),
                "ask_open": float(candle["yes_ask"]["open_dollars"]),
                "ask_high": float(candle["yes_ask"]["high_dollars"]),
                "ask_low": float(candle["yes_ask"]["low_dollars"]),
                "ask_close": float(candle["yes_ask"]["close_dollars"]),
                "bid_open": float(candle["yes_bid"]["open_dollars"]),
                "bid_high": float(candle["yes_bid"]["high_dollars"]),
                "bid_low": float(candle["yes_bid"]["low_dollars"]),
                "bid_close": float(candle["yes_bid"]["close_dollars"]),
                "volume": candle["volume"],
            }
            rows.append(row)

        print()  # New line after progress bar

        return rows
