import requests
import toml
import os

class BaseAPI:
    def __init__(self, env="uat", config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "../config/config.toml")
        config = toml.load(config_path)
        self.base_url = config[env]['base_url']
        self.timeout = config[env].get('timeout', 10)
        
    def _get(self, path, params=None): #設定get方法
        url = self.base_url + path
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp
        except Exception as e:
            print(f"[API ERROR] {url} | params={params} | {e}")
            raise