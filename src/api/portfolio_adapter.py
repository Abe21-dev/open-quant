import requests

from .base_adapter import BaseApiAdapter

"""

1. make a simple order
2. can your order be partially filled
3. create order groups for limits
4. implement algoritim


payload = {
    "action": "buy",
    "buy_max_cost": 23,
    "cancel_order_on_pause": True,
    "client_order_id": "<string>",
    "count": 1,
    "expiration_ts": "in a minute",
    "post_only": True,
    "side": "yes",
    "ticker": "<string>",
    "yes_price_dollars": "0.2300",
}


"""


class PortfolioAPI(BaseApiAdapter):

    def __init__(self, base_url: str, header: str):
        return super().__init__(base_url, header)

    def create_order(self, body: dict = None):
        body = {
            "ticker": "KXNFLGAME-25OCT26MIAATL-MIA",
            "side": "yes",
            "action": "buy",
            "count": 1,
            "yes_price": 22,
        }
        url = self.base_url + "portfolio/orders"

        resp = requests.post(url, json=body, headers=self.header)
        return resp.status_code, resp.json()
