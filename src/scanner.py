from src.data_loader import (
    load_universe,
    get_stock_data,
    get_weekly_data,
    has_upcoming_earnings
)

from src.strat_classifier import add_strat_labels

from src.setup_detector import (
    detect_latest_setup,
    calculate_trade_levels
)
from src.market_context import get_analysis_df

def calculate_score(setup, rr, volume, weekly_ok):
    score = 0

    # Setup quality
    if setup == "Pending 3-1-2U":
        score += 30

    elif setup == "Pending 2-1-2U":
        score += 27

    elif setup == "Pending 2D-2U Reversal":
        score += 24

    # Weekly continuity
    if weekly_ok:
        score += 25

    # RR
    if rr >= 3:
        score += 20

    elif rr >= 2:
        score += 15

    elif rr >= 1.5:
        score += 10

    # Volume
    if volume >= 10_000_000:
        score += 15

    elif volume >= 5_000_000:
        score += 12

    elif volume >= 1_000_000:
        score += 8

    # Earnings safety
    score += 10

    return score


def check_weekly_continuity(df_weekly):
    if df_weekly is None or len(df_weekly) < 2:
        return False

    last_row = df_weekly.iloc[-1]
    prev_row = df_weekly.iloc[-2]

    if float(last_row["Close"]) > float(last_row["Open"]):
        return True

    if float(last_row["Close"]) > float(prev_row["Close"]):
        return True

    return False


def run_scan():
    results = []

    tickers = load_universe()

    for ticker in tickers:

        # Earnings filter - temporarily disabled for faster development
        has_earnings = False
        earnings_date = None

        # Later we will enable this back:
        # has_earnings, earnings_date = has_upcoming_earnings(
        #     ticker=ticker,
        #     days_ahead=3
        # )
        #
        # if has_earnings:
        #     continue

        df_raw = get_stock_data(ticker)

        if df_raw is None or len(df_raw) < 5:
            continue

        df = get_analysis_df(df_raw)

        if df is None or len(df) < 5:
            continue

        df = add_strat_labels(df)

        setup = detect_latest_setup(df)

        if not setup:
            continue

        levels = calculate_trade_levels(df)

        # Reject invalid / tiny moves
        if levels is None:
            continue

        if levels.get("Reward $") is None:
            continue

        if levels.get("RR") is None:
            continue

        if levels["Reward $"] < 0.5:
            continue

        if levels["RR"] < 1.0:
            continue

        last_row = df.iloc[-1]

        candle_range = float(last_row["High"]) - float(last_row["Low"])

        # Ignore weak narrow candles
        if candle_range < 1:
            continue

        volume = float(last_row["Volume"])

        df_weekly = get_weekly_data(ticker)
        weekly_ok = check_weekly_continuity(df_weekly)

        score = calculate_score(
            setup=setup,
            rr=levels["RR"],
            volume=volume,
            weekly_ok=weekly_ok
        )

        results.append({
            "Ticker": ticker,
            "Setup": setup,
            "Weekly Continuity": "Yes" if weekly_ok else "No",
            "Earnings": "No upcoming earnings",
            "Last Price": round(float(last_row["Close"]), 2),
            "Entry": levels["Entry"],
            "Stop": levels["Stop"],
            "Target": levels["Target"],
            "RR": levels["RR"],
            "Risk $": levels["Risk $"],
            "Reward $": levels["Reward $"],
            "Risk %": levels["Risk %"],
            "Reward %": levels["Reward %"],
            "Volume": int(volume),
            "Score": score
        })

    results = sorted(
        results,
        key=lambda x: x["Score"],
        reverse=True
    )

    return results[:5]
