# ============================================================
# STABILITY FILTER
# ============================================================
from config import Config

class StabilityFilter:

    @staticmethod
    def filter(df):

        print("=" * 80)
        print(f"Selecting Top {int(Config.TOP_PERCENT*100)}%")

        top = df[
            df["FinalScore"] >=
            df["FinalScore"].quantile(
                1 - Config.TOP_PERCENT
            )
        ].copy()

        if not Config.USE_RELATIVE_GAP:

            print(f"Top Rows: {len(top):,}")

            return top

        threshold = top["RelativeGap"].quantile(
            Config.RELATIVE_GAP_PERCENTILE
        )

        print(top["RelativeGap"].describe(
            percentiles=[
                0.25,
                0.50,
                0.75,
                0.90
            ]
        ))

        stable = top[
            top["RelativeGap"] <= threshold
        ].copy()

        print(f"\nRelative Gap Threshold : {threshold:.4f}")
        print(f"Stable Rows           : {len(stable):,}")

        return stable