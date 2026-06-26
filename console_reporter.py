# ============================================================
# CONSOLE REPORTER
# ============================================================
from feature_engineer import FeatureEngineer

class ConsoleReporter:

    @staticmethod
    def top_stable(df, n=20):

        print()
        print("=" * 80)
        print("TOP STABLE PARAMETER SETS")
        print("=" * 80)

        cols = [
            "Forward Result",
            "Back Result",
            "Gap",
            "RelativeGap",
            "Consistency",
            "FinalScore"
        ]

        cols += FeatureEngineer.parameter_columns(df)

        cols = [c for c in cols if c in df.columns]

        out = df.sort_values(
            [
                "Consistency",
                "FinalScore"
            ],
            ascending=False
        ).head(n)

        print(
            out[cols].to_string(
                index=False
            )
        )