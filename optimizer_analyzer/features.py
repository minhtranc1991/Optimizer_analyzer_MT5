"""Derived columns: Gap, RelativeGap, Consistency, DDScore, Quality."""
import numpy as np
from sklearn.preprocessing import MinMaxScaler

REQUIRED = ["Forward Result", "Back Result"]


def parameter_columns(df):
    return [c for c in df.columns if c.startswith("set")]


def build_features(df):
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Report is missing required columns: {missing}")

    df = df.copy()
    fwd, back = df["Forward Result"], df["Back Result"]

    df["Gap"] = (fwd - back).abs()
    denom = np.maximum(fwd.abs(), back.abs()).replace(0, 1)
    df["RelativeGap"] = df["Gap"] / denom
    df["Consistency"] = np.minimum(fwd.abs(), back.abs()) / denom

    if "Equity DD %" in df.columns:
        dd = df["Equity DD %"].fillna(df["Equity DD %"].max())
        df["DDScore"] = 1 - MinMaxScaler().fit_transform(dd.to_frame()).ravel()
    else:
        df["DDScore"] = 1.0

    # Rewards high Sharpe/PF on consistent sets. Temporary formula.
    sharpe = df.get("Sharpe Ratio", 0).fillna(0)
    pf = df.get("Profit Factor", 1).fillna(1)
    df["Quality"] = sharpe * pf * df["Consistency"]
    return df
