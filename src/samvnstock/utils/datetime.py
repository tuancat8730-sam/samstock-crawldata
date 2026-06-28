from datetime import datetime, timedelta

_DATE_FORMAT = "%Y-%m-%d"


def parse_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, _DATE_FORMAT)
    except ValueError as exc:
        raise ValueError(f"Định dạng ngày không hợp lệ: {value}. Dùng YYYY-MM-DD.") from exc


def count_business_days(start: datetime, end: datetime) -> int:
    """Count weekdays (Mon-Fri) between start and end inclusive."""
    if end < start:
        raise ValueError("Thời gian bắt đầu không thể lớn hơn thời gian kết thúc.")
    days = (end - start).days + 1
    full_weeks, remainder = divmod(days, 7)
    count = full_weeks * 5
    weekday = start.weekday()
    for _ in range(remainder):
        if weekday < 5:
            count += 1
        weekday = (weekday + 1) % 7
    return count


def end_of_day_timestamp(dt: datetime) -> int:
    """Unix timestamp for the end of the given day, matching VCI's `to` param."""
    return int((dt + timedelta(days=1)).timestamp())
