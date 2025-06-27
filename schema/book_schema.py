book_snapshot_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "method": {"type": "string"},
        "code": {"type": "integer"},
        "result": {
            "type": "object",
            "properties": {
                "instrument_name": {"type": "string"},
                "subscription": {"type": "string"},
                "channel": {"type": "string"},  
                "depth": {"type": "integer"},
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "oneOf": [
                            {   
                                "properties": {
                                    "asks": {
                                        "type": "array",
                                        "items": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "minItems": 3,
                                            "maxItems": 3
                                        }
                                    },
                                    "bids": {
                                        "type": "array",
                                        "items": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "minItems": 3,
                                            "maxItems": 3
                                        }
                                    },
                                    "t": {"type": "integer"},
                                    "tt": {"type": "integer"},
                                    "u": {"type": "integer"},
                                    "cs": {"type": "integer"}
                                },
                                "required": ["asks", "bids", "t", "tt", "u"]
                            },
                            {   
                                "properties": {
                                    "update": {
                                        "type": "object",
                                        "properties": {
                                            "asks": {
                                                "type": "array",
                                                "items": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                    "minItems": 3,
                                                    "maxItems": 3
                                                }
                                            },
                                            "bids": {
                                                "type": "array",
                                                "items": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                    "minItems": 3,
                                                    "maxItems": 3
                                                }
                                            }
                                        },
                                        "required": ["asks", "bids"]
                                    },
                                    "t": {"type": "integer"},
                                    "tt": {"type": "integer"},
                                    "u": {"type": "integer"},
                                    "pu": {"type": "integer"}
                                },
                                "required": ["update", "t", "tt", "u", "pu"]
                            }
                        ]
                    }
                }
            },
            "required": ["instrument_name", "subscription", "channel", "depth", "data"]
        }
    },
    "required": ["id", "method", "code", "result"]
}
