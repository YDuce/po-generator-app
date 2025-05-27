from datetime import datetime
from dateutil.relativedelta import relativedelta

def add_months(dt: datetime, months: int) -> datetime:
    return dt + relativedelta(months=months) 