import base64
from datetime import datetime
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import pytz
import streamlit as st
from textwrap import dedent
from src.scanner import run_scan
from src.data_loader import get_stock_data
from src.market_context import is_market_open
from streamlit_gtag import st_gtag

st.set_page_config(
    page_title="The STRATapp Scanner",
    layout="wide"
)

st_gtag(
    gtag_id="G-3PTS6JR0EP",
    config={
        "send_page_view": True
    }
)

st.markdown(
    """
    <style>
    .top-ticker-wrap {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 28px;
        overflow: hidden;
        background: #020617;
        z-index: 999999999;
        border-bottom: 1px solid rgba(148,163,184,0.15);
    }

    .top-ticker {
        display: inline-block;
        white-space: nowrap;
        color: #7dd3fc;
        font-size: 13px;
        font-weight: 700;
        line-height: 28px;
        animation: tickerMove 18s linear infinite;
    }

    @keyframes tickerMove {
        from {
            transform: translateX(100vw);
        }
        to {
            transform: translateX(-100%);
        }
    }

    .block-container {
        padding-top: 1.8rem !important;
    }
    </style>

    <div class="top-ticker-wrap">
        <div class="top-ticker">
            Educational use only • Not financial advice • Trade at your own risk
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

components.html(
    """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-3PTS6JR0EP"></script>

    <script>
      window.dataLayer = window.dataLayer || [];

      function gtag(){
          dataLayer.push(arguments);
      }

      gtag('js', new Date());

      gtag('config', 'G-3PTS6JR0EP');
    </script>
    """,
    height=0
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
        margin-left: -60px;
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
        margin-bottom: 18px;
        margin-left: 150px;
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
        
    </div>
    
    
    <div style='
        text-align:center;
        margin-top:-6px;
        margin-bottom:18px;
    '>
        <span style='
            padding:4px 10px;
            border-radius:999px;
            background:rgba(59,130,246,0.12);
            border:1px solid rgba(59,130,246,0.25);
            color:#7dd3fc;
            font-size:11px;
            font-weight:800;
            letter-spacing:0.5px;
        '>
            BETA v1
        </span>
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
    df_raw = get_stock_data(ticker, period="2mo", interval="1d")

    from src.market_context import get_analysis_df

    df = get_analysis_df(df_raw)

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
        loader = st.empty()

        loader.markdown("""
        <div style='
            text-align:center;
            color:#cbd5e1;
            font-size:18px;
            margin-top:18px;
            font-weight:700;
        '>
            Scanning market data... please wait
        </div>
        """, unsafe_allow_html=True)

        try:
            results = run_scan()

            if results:
                st.session_state.scan_results = results
                loader.empty()
            else:
                loader.empty()
                st.markdown("""
                <div style="
                    text-align:center;
                    color:#ff6b6b;
                    font-size:15px;
                    margin-top:18px;
                    margin-bottom:10px;
                ">
                    No valid setups found in current market conditions.
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            loader.empty()
            st.error("Scan failed. Check terminal logs.")
            st.exception(e)

    market_is_open = is_market_open()

    if market_is_open:
        st.markdown(
            """
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                margin-top: 50px;
                margin-bottom: 20px;
            ">
                <div style="
                    padding: 8px 24px;
                    border-radius: 30px;
                    background: rgba(22, 163, 74, 0.08);
                    border: 1px solid rgba(34, 197, 94, 0.25);
                    color: #94a3b8;
                    font-size: 13px;
                    white-space: nowrap;
                    display: inline-flex;
                    align-items: center;
                    gap: 10px;
                ">
                    <span style="font-weight: 700; color: #4ade80;">● Market is open</span>
                    <span style="border-left: 1px solid rgba(148, 163, 184, 0.3); padding-left: 10px;">
                        Scanner results are based on the last fully closed daily candle.
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            """
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                margin-top: 50px; /* הוספנו מרווח משמעותי מלמעלה */
                margin-bottom: 20px;
            ">
                <div style="
                    padding: 8px 24px;
                    border-radius: 30px; /* עיגול חזק יותר למראה מודרני */
                    background: rgba(220, 38, 38, 0.08);
                    border: 1px solid rgba(248, 113, 113, 0.2);
                    color: #94a3b8;
                    font-size: 13px;
                    white-space: nowrap;
                    display: inline-flex;
                    align-items: center;
                    gap: 10px;
                ">
                    <span style="font-weight: 700; color: #f87171;">● Market is closed</span>
                    <span style="border-left: 1px solid rgba(148, 163, 184, 0.3); padding-left: 10px;">
                        Scanner results are based on the most recent completed daily candle.
                    </span>
                </div>
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
            font-weight:700;
            margin-bottom:22px;
        ">
            ✅ Top 5 setups found
        </div>
        """,
        unsafe_allow_html=True
    )

    short_setup = (
        best["Setup"]
        .replace("Pending ", "")
        .replace("Reversal", "REV")
    )

    components.html(
        f"""
        <div style="
            width:100%;
            box-sizing:border-box;
            padding:26px 34px;
            border-radius:22px;
            background:linear-gradient(135deg, rgba(22,163,74,0.18), rgba(15,23,42,0.96));
            border:1px solid rgba(34,197,94,0.35);
            box-shadow:0 18px 45px rgba(0,0,0,0.35);
            font-family:Arial, sans-serif;
        ">

            <div style="
                font-size:30px;
                font-weight:900;
                color:white;
                margin-bottom:26px;
            ">
                ⭐ Highest Probability Setup
            </div>

            <div style="
                display:grid;
                grid-template-columns: repeat(5, 1fr);
                gap:22px;
                text-align:center;
            ">

                <div>
                    <div style="color:#cbd5e1; font-size:14px; font-weight:700;">Ticker</div>
                    <div style="color:white; font-size:38px; font-weight:900;">{best["Ticker"]}</div>
                </div>

                <div>
                    <div style="color:#cbd5e1; font-size:14px; font-weight:700;">Setup</div>
                    <div style="color:#4ade80; font-size:38px; font-weight:900;">{short_setup}</div>
                </div>

                <div>
                    <div style="color:#cbd5e1; font-size:14px; font-weight:700;">Score</div>
                    <div style="color:white; font-size:38px; font-weight:900;">{int(best["Score"])}</div>
                </div>

                <div>
                    <div style="color:#cbd5e1; font-size:14px; font-weight:700;">Entry</div>
                    <div style="color:white; font-size:38px; font-weight:900;">{float(best["Entry"]):.2f}</div>
                </div>

                <div>
                    <div style="color:#cbd5e1; font-size:14px; font-weight:700;">Target</div>
                    <div style="color:#4ade80; font-size:38px; font-weight:900;">{float(best["Target"]):.2f}</div>
                </div>

            </div>
        </div>
        """,
        height=230
    )

    df_display = df_results.copy()
    df_display.index = df_display.index + 1

    st.dataframe(
        df_display.style
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
