# ============================================================
# SHAP ANALYZER
# ============================================================
import pandas as pd
from config import Config
from feature_engineer import FeatureEngineer
from sklearn.ensemble import RandomForestRegressor

class SHAPAnalyzer:

    @staticmethod
    def importance(
            df,
            target="FinalScore"):

        params = FeatureEngineer.parameter_columns(df)

        X = df[params].fillna(0)

        y = df[target]

        model = RandomForestRegressor(
            n_estimators=500,
            random_state=Config.RANDOM_STATE,
            n_jobs=-1
        )

        model.fit(X, y)

        importance = pd.DataFrame({
            "Parameter": params,
            "Importance": model.feature_importances_
        })

        importance = importance.sort_values(
            "Importance",
            ascending=False
        )

        return importance.reset_index(
            drop=True
        )

    @staticmethod
    def report(df):

        print("=" * 80)
        print("PROFIT IMPORTANCE")
        print("=" * 80)

        profit = SHAPAnalyzer.importance(
            df,
            "Forward Result"
        )

        print(
            profit.to_string(
                index=False
            )
        )

        print()

        print("=" * 80)
        print("CONSISTENCY IMPORTANCE")
        print("=" * 80)

        consistency = SHAPAnalyzer.importance(
            df,
            "Consistency"
        )

        print(
            consistency.to_string(
                index=False
            )
        )

        return profit, consistency