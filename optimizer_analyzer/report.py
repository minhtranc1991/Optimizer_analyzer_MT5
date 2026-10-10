"""Console output helpers."""
from .features import parameter_columns


def print_top_stable(df, n=20):
    print()
    print("=" * 80)
    print("TOP STABLE PARAMETER SETS (by Quality)")
    print("=" * 80)
    cols = ["Forward Result", "Back Result", "Gap", "RelativeGap",
            "Consistency", "Quality", "FinalScore"] + parameter_columns(df)
    top = df.sort_values(["Quality", "FinalScore"], ascending=False).head(n)
    print(top[[c for c in cols if c in df.columns]].to_string(index=False))


def print_elite(elite, parameters):
    print()
    print("=" * 80)
    print("ELITE SETS (Forward & Back above threshold)")
    print("=" * 80)
    if elite.empty:
        print("none")
        return
    cols = ["Forward Result", "Back Result", "RelativeGap", "FinalScore"] + parameters
    print(elite[cols].sort_values("FinalScore", ascending=False).to_string(index=False))
