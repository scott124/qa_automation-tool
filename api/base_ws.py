import websocket
import json
import threading
import time
import toml
import os

class BaseWSClient:
    def __init__(self, env="uat", config_path=None, timeout=10):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "../config/config.toml")
        config = toml.load(config_path)
        ws_key = f"ws_{env}"
        self.ws_url = config[ws_key]['ws_url']
        self.ws = None
        self.timeout = timeout
        self.responses = []
        self._lock = threading.Lock() #確保多執行緒下資料一致

    def on_message(self, ws, message):
        with self._lock:
            self.responses.append(message)

    def on_error(self, ws, error):
        print(f"WS error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WS closed")

    def connect(self):
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.thread.start()
        time.sleep(1)

    def send(self, payload):
        self.ws.send(json.dumps(payload))

    def get_responses(self, min_count=1, timeout=None):
        timeout = timeout or self.timeout
        start = time.time()
        while len(self.responses) < min_count and time.time() - start < timeout:
            time.sleep(0.1)
        with self._lock:
            resps = self.responses[:]
            self.responses = []
        return resps

    def get_response(self, timeout=None):
        return self.get_responses(min_count=1, timeout=timeout)[0] if self.responses else None

    def close(self):
        if self.ws:
            self.ws.close()
    