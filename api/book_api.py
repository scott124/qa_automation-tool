from .base_ws import BaseWSClient
import json

class BookWSAPI:
    def __init__(self, env="uat"):
        self.ws_client = BaseWSClient(env=env)

    def subscribe_book(self, instrument_name, depth=10, params=None, min_msgs=1):
        self.ws_client.connect()
        msg = {
            "id": 1,
            "method": "subscribe",
            "params": {
                "channels": [f"book.{instrument_name}.{depth}"]
            }
        }
        # 支援額外參數 ex: SNAPSHOT_AND_UPDATE
        if params:
            msg["params"].update(params)
        self.ws_client.send(msg)
        resps = self.ws_client.get_responses(min_count=min_msgs)
        self.ws_client.close()
        return [json.loads(r) for r in resps if r]
