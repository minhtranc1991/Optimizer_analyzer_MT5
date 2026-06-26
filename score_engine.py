# ============================================================
# SCORE ENGINE
# ============================================================
import numpy as np
from config import Config
from sklearn.preprocessing import MinMaxScaler

class ScoreEngine:

    @staticmethod
    def build(df):

        df = df.copy()

        score_cols = []

        if "Forward Result" in df.columns:
            score_cols.append("Forward Result")

        if "Back Result" in df.columns:
            score_cols.append("Back Result")

        if "Profit Factor" in df.columns:
            score_cols.append("Profit Factor")

        if "Sharpe Ratio" in df.columns:
            score_cols.append("Sharpe Ratio")

        scaler = MinMaxScaler()

        scaled = scaler.fit_transform(

            df[score_cols].fillna(0)

        )

        score = np.zeros(len(df))

        col = 0

        if "Forward Result" in score_cols:

            score += Config.W_FORWARD * scaled[:, col]
            col += 1

        if "Back Result" in score_cols:

            score += Config.W_BACK * scaled[:, col]
            col += 1

        if "Profit Factor" in score_cols:

            score += Config.W_PROFIT_FACTOR * scaled[:, col]
            col += 1

        if "Sharpe Ratio" in score_cols:

            score += Config.W_SHARPE * scaled[:, col]
            col += 1

        score += Config.W_CONSISTENCY * df["Consistency"]

        score += Config.W_DRAWDOWN * df["DDScore"]

        df["FinalScore"] = score

        return df