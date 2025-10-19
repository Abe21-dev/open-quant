from dataclasses import dataclass


@dataclass
class MarketCompat:
    event_ticker: str
    series_ticker: str
    market_ticker: str
    start_ts: int
    end_ts: int
