from datetime import datetime, timezone

# 2014-04-29T05:12:46.221816+00:00
iso_date_format = '%Y-%m-%dT%H:%M:%S.%f'


def json_serializer(val):
    return val.isoformat() if isinstance(val, datetime) else val


def parse_datetime(val):
    if not val:
        return val
    val = val.rstrip('+00:00')  # FIXME
    d = datetime.strptime(val, iso_date_format)
    d = d.replace(tzinfo=timezone.utc)
    return d
