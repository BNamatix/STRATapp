import base64
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import pytz
import streamlit as st

from src.scanner import run_scan
from src.data_loader import get_stock_data


st.set_page_config(
    page_title="The STRATapp Scanner",
    layout="wide"
)


# ---------- MARKET STATUS ----------

ny_time = datetime.now(pytz.timezone("US/Eastern"))
hour = ny_time.hour
minute = ny_time.minute
weekday = ny_time.weekday()

market_open = (
    weekday < 5
    and (hour > 9 or (hour == 9 and minute >= 30))
    and hour < 16
)

if market_open:
    market_status = "🟢 MARKET OPEN"
    market_color = "#16a34a"
else:
    market_status = "🔴 MARKET CLOSED"
    market_color = "#dc2626"


# ---------- LOGO ----------

with open("assets/bnamatix_logo.png", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()


# ---------- CSS ----------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 0.5rem !important;
    }

    .brand-header {
        max-width: 760px;
        margin: 0 auto 18px auto;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }

    .brand-logo {
        width: 300px;
    }

    .market-badge {
        padding: 4px 18px;
        border-radius: 999px;
        font-size: 14px;
        font-weight: 800;
        white-space: nowrap;
        margin-top: 70px;
    }

    .main-title {
        text-align: center;
        font-size: 56px;
        font-weight: 900;
        color: white;
        margin-top: 18px;
        margin-bottom: 10px;
        line-height: 1.1;
    }

    .sub-title {
        text-align: center;
        font-size: 18px;
        color: #94a3b8;
        margin-bottom: 28px;
    }

    div.stButton > button:first-child {
        width: 100% !important;
        max-width: 520px !important;
        margin: auto !important;
        display: block !important;
        height: 82px !important;
        border-radius: 22px !important;
        border: none !important;
        background: linear-gradient(135deg, #2563eb, #16a34a) !important;
        color: white !important;
        box-shadow: 0px 12px 34px rgba(37,99,235,0.38) !important;
        transition: 0.25s !important;
    }

    div.stButton > button:first-child p {
        font-size: 42px !important;
        font-weight: 900 !important;
        color: white !important;
    }

    div.stButton > button:first-child:hover {
        transform: scale(1.03);
        color: white;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------- HEADER ----------

st.markdown(
    f"""
    <div class="brand-header">
        <img class="brand-logo" src="data:image/png;base64,{logo_base64}">
        <div
            class="market-badge"
            style="
                background:{market_color}22;
                color:{market_color};
                border:1px solid {market_color}55;
            "
        >
            {market_status}
        </div>
    </div>

    <div class="main-title">
        The STRATapp Scanner
    </div>

    <div class="sub-title">
        AI-ranked STRAT setups for active traders.
    </div>
    """,
    unsafe_allow_html=True
)


# ---------- CHART ----------

def plot_trade_chart(ticker, entry, stop, target):
    df = get_stock_data(ticker, period="2mo", interval="1d")

    if df is None or df.empty:
        st.warning("No chart data available")
        return

    df = df.tail(6).copy()
    df = df.reset_index(drop=True)
    df["x"] = list(range(len(df)))

    strat_labels = []

    for i in range(len(df)):
        if i == 0:
            strat_labels.append("")
            continue

        prev_high = float(df.iloc[i - 1]["High"])
        prev_low = float(df.iloc[i - 1]["Low"])
        current_high = float(df.iloc[i]["High"])
        current_low = float(df.iloc[i]["Low"])

        if current_high <= prev_high and current_low >= prev_low:
            strat_labels.append("1")
        elif current_high > prev_high and current_low < prev_low:
            strat_labels.append("3")
        elif current_high > prev_high:
            strat_labels.append("2U")
        elif current_low < prev_low:
            strat_labels.append("2D")
        else:
            strat_labels.append("?")

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df["x"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name=ticker,
            increasing_line_color="#39ff14",
            decreasing_line_color="#ff3333",
            increasing_fillcolor="#39ff14",
            decreasing_fillcolor="#ff3333",
            increasing_line_width=2,
            decreasing_line_width=2
        )
    )

    for i in range(len(df)):
        label = strat_labels[i]

        if label == "":
            continue

        candle_high = float(df.iloc[i]["High"])

        color = "white"
        if label == "1":
            color = "yellow"
        elif label == "2U":
            color = "#00bfff"
        elif label == "2D":
            color = "#ff5555"
        elif label == "3":
            color = "orange"

        fig.add_annotation(
            x=df.iloc[i]["x"],
            y=candle_high * 1.003,
            text=label,
            showarrow=False,
            font=dict(size=18, color=color)
        )

    last_x = df.iloc[-1]["x"]
    prev_x = df.iloc[-2]["x"]
    line_end_x = last_x + 2.4

    fig.add_shape(
        type="line",
        x0=prev_x,
        x1=line_end_x,
        y0=target,
        y1=target,
        line=dict(color="green", width=2)
    )

    fig.add_shape(
        type="line",
        x0=last_x,
        x1=line_end_x,
        y0=entry,
        y1=entry,
        line=dict(color="orange", width=2)
    )

    fig.add_shape(
        type="line",
        x0=last_x,
        x1=line_end_x,
        y0=stop,
        y1=stop,
        line=dict(color="red", width=2)
    )

    fig.add_annotation(
        x=line_end_x,
        y=target,
        text=f"TARGET {target}",
        showarrow=False,
        font=dict(color="green", size=13),
        xanchor="left"
    )

    fig.add_annotation(
        x=line_end_x,
        y=entry,
        text=f"ENTRY {entry}",
        showarrow=False,
        font=dict(color="orange", size=13),
        xanchor="left"
    )

    fig.add_annotation(
        x=line_end_x,
        y=stop,
        text=f"STOP {stop}",
        showarrow=False,
        font=dict(color="red", size=13),
        xanchor="left"
    )

    price_min = min(df["Low"].min(), stop)
    price_max = max(df["High"].max(), target)
    padding = (price_max - price_min) * 0.15

    fig.update_xaxes(
        range=[-0.3, line_end_x + 0.9],
        tickmode="array",
        tickvals=df["x"],
        ticktext=[d.strftime("%m-%d") for d in pd.to_datetime(df["Date"])],
        showgrid=True
    )

    fig.update_yaxes(
        range=[price_min - padding, price_max + padding],
        showgrid=True
    )

    fig.update_layout(
        title=f"{ticker} — Trade Setup",
        height=600,
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        showlegend=False,
        margin=dict(l=20, r=150, t=40, b=20),
        bargap=0.08
    )

    st.plotly_chart(fig, width="stretch")


# ---------- ACTION AREA ----------

if "scan_results" not in st.session_state:
    st.session_state.scan_results = None

left, center, right = st.columns([1.5, 1, 1.5])

with center:
    run_clicked = st.button(
        "Find Best Setups",
        width="stretch"
    )

    if run_clicked:
        with st.spinner("Scanning and ranking best setups..."):
            st.session_state.scan_results = run_scan()

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#94a3b8;
            font-size:14px;
            font-weight:500;
            margin-top:18px;
            margin-bottom:28px;
        ">
            Educational use only • Not financial advice • Trade at your own risk
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------- RESULTS ----------

if st.session_state.scan_results:
    df_results = pd.DataFrame(st.session_state.scan_results)

    best = df_results.iloc[0]

    st.markdown(
        """
        <div style="
            display:inline-block;
            padding:10px 18px;
            background-color:#123524;
            color:#4cff88;
            border-radius:10px;
            font-weight:600;
            margin-bottom:15px;
        ">
            Top 5 setups found
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("⭐ Highest Probability Setup")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Ticker", best["Ticker"])

    short_setup = (
        best["Setup"]
        .replace("Pending ", "")
        .replace("Reversal", "REV")
    )

    col2.metric("Setup", short_setup)
    col3.metric("Score", int(best["Score"]))
    col4.metric("Entry", best["Entry"])
    col5.metric("Target", best["Target"])

    st.dataframe(
        df_results.style
        .format({
            "Last Price": "{:.2f}",
            "Entry": "{:.2f}",
            "Stop": "{:.2f}",
            "Target": "{:.2f}",
            "RR": "{:.2f}",
            "Risk $": "{:.2f}",
            "Reward $": "{:.2f}",
            "Risk %": "{:.2f}",
            "Reward %": "{:.2f}",
            "Score": "{:.0f}"
        })
        .set_properties(**{
            "text-align": "center"
        }),
        width="stretch"
    )

    selected_ticker = st.radio(
        "Select setup",
        df_results["Ticker"].tolist(),
        horizontal=True
    )

    selected_row = df_results[df_results["Ticker"] == selected_ticker].iloc[0]

    st.subheader(f"{selected_row['Ticker']} Trade Plan")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Entry", selected_row["Entry"])
    col2.metric("Stop", selected_row["Stop"])
    col3.metric("Target", selected_row["Target"])
    col4.metric("RR", selected_row["RR"])

    plot_trade_chart(
        ticker=selected_row["Ticker"],
        entry=selected_row["Entry"],
        stop=selected_row["Stop"],
        target=selected_row["Target"]
    )