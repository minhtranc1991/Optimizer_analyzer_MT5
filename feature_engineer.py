# ============================================================
# FEATURE ENGINEER
# ============================================================
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class FeatureEngineer:

    @staticmethod
    def parameter_columns(df):

        return [
            c
            for c in df.columns
            if c.startswith("set")
        ]

    @staticmethod
    def metric_columns(df):

        metrics = []

        candidates = [
            "Forward Result",
            "Back Result",
            "Profit Factor",
            "Sharpe Ratio",
            "Equity DD %"
        ]

        for c in candidates:

            if c in df.columns:
                metrics.append(c)

        return metrics

    @staticmethod
    def build(df):

        df = df.copy()

        # -----------------------
        # Gap
        # -----------------------

        df["Gap"] = np.abs(df["Forward Result"] - df["Back Result"])

        # -----------------------
        # Relative Gap
        # -----------------------

        denom = np.maximum(
            np.abs(df["Forward Result"]),
            np.abs(df["Back Result"])
        )

        denom = np.where(
            denom == 0,
            1,
            denom
        )

        df["RelativeGap"] = (
            df["Gap"]
            /
            denom
        )

        # -----------------------
        # Consistency
        # -----------------------

        df["Consistency"] = (
            np.minimum(
                np.abs(df["Forward Result"]),
                np.abs(df["Back Result"])
            ) / denom
        )

        # -----------------------
        # Drawdown score
        # -----------------------

        if "Equity DD %" in df.columns:

            dd = df["Equity DD %"].fillna(
                df["Equity DD %"].max()
            )

            scaler = MinMaxScaler()

            df["DDScore"] = 1 - scaler.fit_transform(
                dd.values.reshape(-1, 1)
            ).flatten()

        else:
            df["DDScore"] = 1

        return df