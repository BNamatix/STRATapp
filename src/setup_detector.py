def is_valid_212u(df):
    last_2 = df.tail(2)["strat"].tolist()

    if last_2 != ["2D", "1"]:
        return False

    trigger_candle = df.iloc[-1]
    signal_candle = df.iloc[-2]

    trigger_high = float(trigger_candle["High"])
    trigger_low = float(trigger_candle["Low"])

    signal_high = float(signal_candle["High"])
    signal_low = float(signal_candle["Low"])

    inside_bar = (
            trigger_high <= signal_high
            and trigger_low >= signal_low
    )

    if not inside_bar:
        return False

    inside_range = trigger_high - trigger_low
    signal_range = signal_high - signal_low

    if inside_range < (signal_range * 0.25):
        return False

    return True


def is_valid_312u(df):
    last_2 = df.tail(2)["strat"].tolist()

    if last_2 != ["3", "1"]:
        return False

    inside_candle = df.iloc[-1]
    outside_candle = df.iloc[-2]

    inside_high = float(inside_candle["High"])
    inside_low = float(inside_candle["Low"])

    outside_high = float(outside_candle["High"])
    outside_low = float(outside_candle["Low"])

    inside_bar = (
            inside_high <= outside_high
            and inside_low >= outside_low
    )

    if not inside_bar:
        return False

    inside_range = inside_high - inside_low
    outside_range = outside_high - outside_low

    if inside_range < (outside_range * 0.25):
        return False

    return True


def detect_latest_setup(df):
    if df is None or len(df) < 3:
        return None

    last_2 = df.tail(2)["strat"].tolist()

    if is_valid_212u(df):
        return "Pending 2-1-2U"

    # Pending 3-1-2U
    if is_valid_312u(df):
        return "Pending 3-1-2U"

    # Temporarily disabled - too broad for valid long setups
    # if df.iloc[-1]["strat"] == "2D":
    #     return "Pending 2D-2U Reversal"

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
