"""Pre-filter and stability filter."""
import pandas as pd

from .config import Config


def prefilter(df):
    """Drop sets with too few trades or too much drawdown."""
    keep = pd.Series(True, index=df.index)
    if Config.MIN_TRADES is not None and "Trades" in df.columns:
        keep &= df["Trades"] >= Config.MIN_TRADES
    if Config.MAX_EQUITY_DD is not None and "Equity DD %" in df.columns:
        keep &= df["Equity DD %"] <= Config.MAX_EQUITY_DD
    print(f"Pre-filter: {int(keep.sum()):,}/{len(df):,} rows kept")
    return df[keep].copy()


def elite_sets(df):
    """Sets strong on both Forward and Back, regardless of gap."""
    return df[
        (df["Forward Result"] > Config.ELITE_MIN_FORWARD)
        & (df["Back Result"] > Config.ELITE_MIN_BACK)
    ].copy()


def stability_filter(df):
    """Return (stable, elite). stable = top by score & low gap, plus elite."""
    print("=" * 80)
    print(f"Selecting Top {int(Config.TOP_PERCENT * 100)}%")

    cutoff = df["FinalScore"].quantile(1 - Config.TOP_PERCENT)
    top = df[df["FinalScore"] >= cutoff]

    stable = top
    if Config.USE_RELATIVE_GAP:
        threshold = top["RelativeGap"].quantile(Config.RELATIVE_GAP_PERCENTILE)
        stable = top[top["RelativeGap"] <= threshold]
        print(f"Relative Gap Threshold : {threshold:.4f}")

    elite = elite_sets(df)
    stable = pd.concat([stable, elite]).loc[lambda d: ~d.index.duplicated()].copy()

    print(f"Elite (Fwd>{Config.ELITE_MIN_FORWARD} & Back>{Config.ELITE_MIN_BACK}) : {len(elite):,}")
    print(f"Stable Rows            : {len(stable):,}")
    return stable, elite
