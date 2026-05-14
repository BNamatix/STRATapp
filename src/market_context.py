from datetime import datetime
import pytz


def is_market_open():
    ny_time = datetime.now(pytz.timezone("US/Eastern"))

    hour = ny_time.hour
    minute = ny_time.minute
    weekday = ny_time.weekday()

    return (
        weekday < 5
        and (hour > 9 or (hour == 9 and minute >= 30))
        and hour < 16
    )


def get_analysis_df(df):
    if df is None or df.empty:
        return df

    if is_market_open() and len(df) > 1:
        return df.iloc[:-1].copy()

    return df.copy()