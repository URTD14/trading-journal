# app.py

import streamlit as st
import pandas as pd
from datetime import date

from config import EFFECTIVE_CAPITAL, MAX_DAILY_LOSS_RS
from utils import calculate_pnl, load_trades, equity_curve

st.set_page_config(page_title="Trading Journal", layout="wide")

st.title("📈 Personal Trading Journal")

st.sidebar.header("Account Configuration")
st.sidebar.write(f"Capital: ₹4,700")
st.sidebar.write(f"Leverage: 5x")
st.sidebar.write(f"Effective Capital: ₹{EFFECTIVE_CAPITAL}")

# Load trades
df = load_trades()

# ======================
# TRADE ENTRY SECTION
# ======================

st.subheader("Log Today’s Trade")

with st.form("trade_form"):
    trade_date = st.date_input("Date", date.today())
    stock = st.text_input("Stock Name")
    side = st.selectbox("Side", ["BUY", "SELL"])
    entry = st.number_input("Entry Price", min_value=0.0, step=0.05)
    exit = st.number_input("Exit Price", min_value=0.0, step=0.05)

    qty = st.number_input(
        "Quantity",
        min_value=1,
        help="Use quantity that fits ₹4,700 × 5x"
    )

    notes = st.text_area("Notes / Emotion / Mistake")

    submitted = st.form_submit_button("Save Trade")

if submitted:
    gross, net = calculate_pnl(entry, exit, qty, side)

    # Daily loss protection
    today_loss = df[df["date"] == str(trade_date)]["net_pnl"].sum()
    if today_loss + net < -MAX_DAILY_LOSS_RS:
        st.error("Daily loss limit breached. Trade not allowed.")
    else:
        new_trade = {
            "date": trade_date,
            "stock": stock.upper(),
            "side": side,
            "entry": entry,
            "exit": exit,
            "qty": qty,
            "gross_pnl": gross,
            "net_pnl": net,
            "notes": notes
        }

        df = pd.concat([df, pd.DataFrame([new_trade])], ignore_index=True)
        df.to_csv("trades.csv", index=False)
        st.success("Trade logged successfully")

# ======================
# DASHBOARD
# ======================

st.subheader("Performance Dashboard")

if len(df) > 0:
    eq = equity_curve(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", len(df))
    col2.metric("Net PnL (₹)", round(df["net_pnl"].sum(), 2))
    col3.metric("Win Rate (%)", round((df["net_pnl"] > 0).mean() * 100, 2))
    col4.metric("Current Capital (₹)", round(eq["equity"].iloc[-1], 2))

    st.line_chart(eq.set_index("date")["equity"])

    st.subheader("Trade Log")
    st.dataframe(df, use_container_width=True)

else:
    st.info("No trades logged yet.")
