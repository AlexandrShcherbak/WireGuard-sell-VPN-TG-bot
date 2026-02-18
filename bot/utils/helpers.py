from datetime import datetime


def fmt_dt(dt: datetime | None) -> str:
    if not dt:
        return '—'
    return dt.strftime('%d.%m.%Y %H:%M')
