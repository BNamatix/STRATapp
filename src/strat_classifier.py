def classify_candle(prev_row, current_row):
    prev_high = float(prev_row["High"])
    prev_low = float(prev_row["Low"])

    current_high = float(current_row["High"])
    current_low = float(current_row["Low"])

    if current_high <= prev_high and current_low >= prev_low:
        return "1"

    if current_high > prev_high and current_low < prev_low:
        return "3"

    if current_high > prev_high:
        return "2U"

    if current_low < prev_low:
        return "2D"

    return "NA"


def add_strat_labels(df):
    df = df.copy()
    labels = [None]

    for i in range(1, len(df)):
        label = classify_candle(df.iloc[i - 1], df.iloc[i])
        labels.append(label)

    df["strat"] = labels
    return df