from datetime import datetime, timezone


iso_date_format = '%Y-%m-%dT%H:%M:%S.%f+00:00'


def json_serializer(val):
    return val.isoformat() if isinstance(val, datetime) else val


def parse_datetime(val):
    if not val:
        return val
    d = datetime.strptime(val, iso_date_format)
    d = d.replace(tzinfo=timezone.utc)
    return d
