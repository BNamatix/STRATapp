def detect_latest_setup(df):
    if df is None or len(df) < 3:
        return None

    last_2 = df.tail(2)["strat"].tolist()
    last_1 = df.iloc[-1]["strat"]

    # Pending 2-1-2U
    # Yesterday/previous candle = 2D
    # Last closed candle = 1
    # Tomorrow trigger = 2U
    if last_2 == ["2D", "1"]:
        return "Pending 2-1-2U"

    # Pending 3-1-2U
    # Previous candle = 3
    # Last closed candle = 1
    # Tomorrow trigger = 2U
    if last_2 == ["3", "1"]:
        return "Pending 3-1-2U"

    # Pending 2D-2U Reversal
    # Last closed candle is 2D
    # Tomorrow trigger above its high
    if last_1 == "2D":
        return "Pending 2D-2U Reversal"

    return None


def calculate_trade_levels(df):
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    last_high = float(last_row["High"])
    last_low = float(last_row["Low"])

    prev_high = float(prev_row["High"])

    entry = round(last_high, 2)
    stop = round((last_high + last_low) / 2, 2)
    target = round(prev_high, 2)

    risk = entry - stop
    reward = target - entry

    if risk <= 0 or reward <= 0:
        return {
            "Entry": entry,
            "Stop": stop,
            "Target": target,
            "RR": None,
            "Risk $": None,
            "Reward $": None,
            "Risk %": None,
            "Reward %": None
        }

    rr = reward / risk

    return {
        "Entry": entry,
        "Stop": stop,
        "Target": target,
        "RR": round(rr, 2),
        "Risk $": round(risk, 2),
        "Reward $": round(reward, 2),
        "Risk %": round((risk / entry) * 100, 2),
        "Reward %": round((reward / entry) * 100, 2)
    }