"""FinalScore = weighted sum of min-max scaled metrics."""
import numpy as np

from .config import Config

# column -> weight attribute on Config
METRIC_WEIGHTS = {
    "Forward Result": "W_FORWARD",
    "Back Result": "W_BACK",
    "Profit Factor": "W_PROFIT_FACTOR",
    "Sharpe Ratio": "W_SHARPE",
    "Consistency": "W_CONSISTENCY",
    "Quality": "W_QUALITY",
    "DDScore": "W_DRAWDOWN",
}


def _scale(s):
    s = s.fillna(s.median())
    lo, hi = s.quantile(Config.OUTLIER_CLIP[0]), s.quantile(Config.OUTLIER_CLIP[1])
    s = s.clip(lo, hi)
    span = hi - lo
    return (s - lo) / span if span else s * 0


def build_score(df):
    df = df.copy()
    present = {c: getattr(Config, w) for c, w in METRIC_WEIGHTS.items() if c in df.columns}
    total = sum(present.values())  # renormalise if a metric column is absent
    df["FinalScore"] = sum(w / total * _scale(df[c]) for c, w in present.items())
    return df
