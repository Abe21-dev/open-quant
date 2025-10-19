import os
import csv
import logging

from datetime import date, datetime
from models.compact_markets import MarketCompat
from api.kalshi_client import MarketsAPI


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class LoadOHLC:
    def __init__(self, marketAPI: MarketsAPI):
        self.period_interval = 1
        self.marketAPI = marketAPI

    def load_OHLC(self, market: MarketCompat):
        time_intervals = self.__get_intervals(market)
        logger.info(f"Number of requests to get market OHLC: {len(time_intervals)}")
        resp_json: dict[str, list] = None
        for period in time_intervals:
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

            logger.info(f"LOADED: {len(resp_json["candlesticks"])} ")

        logger.info(f"write dat to csv")
        file_name = str(date.today()) + "_OHLC.csv"
        dir_name = "data"
        rows = self.__json_to_csv(resp_json, file_name)

        with open(os.path.join(dir_name, file_name), "w") as f:
            writer = csv.DictWriter(f)
            writer.writeheader()
            writer.writerows(rows)

        pass

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

        for candle in json_data["candlesticks"]:
            # Convert timestamp to YYYY-MM-DD
            date = datetime.fromtimestamp(candle["end_period_ts"]).strftime("%Y-%m-%d")

            row = {
                "market_ticker": ticker,
                "date": date,
                "ask_open": float(candle["yes_ask"]["open_dollars"]),
                "ask_high": float(candle["yes_ask"]["high_dollars"]),
                "ask_low": float(candle["yes_ask"]["low_dollars"]),
                "ask_close": float(candle["yes_ask"]["close_dollars"]),
                "ask_volume": candle["volume"],
                "bid_open": float(candle["yes_bid"]["open_dollars"]),
                "bid_high": float(candle["yes_bid"]["high_dollars"]),
                "bid_low": float(candle["yes_bid"]["low_dollars"]),
                "bid_close": float(candle["yes_bid"]["close_dollars"]),
                "bid_volume": candle["volume"],
            }
            rows.append(row)
