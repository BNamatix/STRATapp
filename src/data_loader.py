import pandas as pd
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta


def load_universe():
    df = pd.read_csv("data/universe.csv")
    return df["Ticker"].tolist()


def fix_columns(df):
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)
    return df


@st.cache_data(ttl=60 * 60)
def get_stock_data(ticker, period="6mo", interval="1d"):
    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False
        )

        if df.empty:
            return None

        df = fix_columns(df)
        df.reset_index(inplace=True)

        return df

    except Exception as e:
        print(f"Error loading {ticker}: {e}")
        return None


@st.cache_data(ttl=60 * 60)
def get_weekly_data(ticker, period="1y"):
    try:
        df = yf.download(
            ticker,
            period=period,
            interval="1wk",
            auto_adjust=False,
            progress=False
        )

        if df.empty:
            return None

        df = fix_columns(df)
        df.reset_index(inplace=True)

        return df

    except Exception as e:
        print(f"Weekly data error for {ticker}: {e}")
        return None


@st.cache_data(ttl=60 * 60 * 6)
def has_upcoming_earnings(ticker, days_ahead=3):
    try:
        stock = yf.Ticker(ticker)
        earnings_dates = stock.get_earnings_dates(limit=8)

        if earnings_dates is None or earnings_dates.empty:
            return False, None

        today = datetime.now().date()
        max_date = today + timedelta(days=days_ahead)

        for earnings_date in earnings_dates.index:
            earnings_day = earnings_date.date()

            if today <= earnings_day <= max_date:
                return True, earnings_day

        return False, None

    except Exception as e:
        print(f"Earnings check error for {ticker}: {e}")
        return False, None