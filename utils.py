# utils.py

import pandas as pd
from config import TOTAL_CHARGES, CAPITAL

def calculate_pnl(entry, exit, qty, side):
    if side == "BUY":
        gross = (exit - entry) * qty
    else:
        gross = (entry - exit) * qty

    net = gross - TOTAL_CHARGES
    return gross, net


def load_trades(path="trades.csv"):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame(columns=[
            "date", "stock", "side",
            "entry", "exit", "qty",
            "gross_pnl", "net_pnl",
            "notes"
        ])


def equity_curve(df):
    df = df.copy()
    df["cum_pnl"] = df["net_pnl"].cumsum()
    df["equity"] = CAPITAL + df["cum_pnl"]
    return df
