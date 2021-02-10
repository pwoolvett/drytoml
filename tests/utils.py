import json
from datetime import date
from datetime import datetime


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()

        return super().default(o)
