from datetime import datetime

def parse_date(date_str):
    """Convert string date to datetime object"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None
