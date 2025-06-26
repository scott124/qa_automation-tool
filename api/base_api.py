import requests
import toml
import os

class BaseAPI:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "../config/config.toml")
        config = toml.load(config_path)
        self.base_url = config['default']['base_url']
        self.timeout = config['default'].get('timeout', 10)

    def _get(self, path, params=None): #設定get方法
        url = self.base_url + path
        resp = requests.get(url, params=params, timeout=self.timeout)
        return resp
