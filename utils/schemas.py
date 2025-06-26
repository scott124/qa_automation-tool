candlestick_schema = {
    "type": "object",
    "required": ["id", "method", "code", "result"],
    "properties": {
        "id": {"type": "integer"},
        "method": {"type": "string"},
        "code": {"type": "integer"},
        "result": {
            "type": "object",
            "required": ["interval", "data", "instrument_name"],
            "properties": {
                "interval": {"type": "string"},
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["o", "h", "l", "c", "v", "t"],
                        "properties": {
                            "o": {"type": "string"},
                            "h": {"type": "string"},
                            "l": {"type": "string"},
                            "c": {"type": "string"},
                            "v": {"type": "string"},
                            "t": {"type": "integer"}
                        }
                    }
                },
                "instrument_name": {"type": "string"}
            }
        }
    }
}
