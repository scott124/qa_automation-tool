from .base_api import BaseAPI

class CandlestickAPI(BaseAPI):
    def get_candlestick(self, instrument_name, timeframe="M1", count=None, start_ts=None, end_ts=None):
        path = "/public/get-candlestick"
        params = {
            "instrument_name": instrument_name,
            "timeframe": timeframe
        }
        if count: params["count"] = count
        if start_ts: params["start_ts"] = start_ts
        if end_ts: params["end_ts"] = end_ts
        return self._get(path, params)
