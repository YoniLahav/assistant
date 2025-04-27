from datetime import datetime

def extract_date(date_dict):
    date_str = date_dict.get('dateTime', date_dict.get('date'))
    if date_str:
        return datetime.fromisoformat(date_str).date()
    else:
        return None

def extract_time(date_dict):
    date_str = date_dict.get('dateTime', '')
    if date_str:
        return datetime.fromisoformat(date_str).time()
    else:
        return None