# ============================================================
# FEATURE SELECTION
# ============================================================
from config import Config

class FeatureSelector:

    @staticmethod
    def select(
            profit_importance,
            consistency_importance):

        merge = profit_importance.merge(
            consistency_importance,
            on="Parameter",
            suffixes=(
                "_Profit",
                "_Consistency"
            )
        )

        merge["Score"] = (
            merge["Importance_Profit"]
            +
            merge["Importance_Consistency"]
        ) / 2

        if Config.SHAP_THRESHOLD == "median":

            threshold = merge["Score"].median()

        else:

            threshold = Config.SHAP_THRESHOLD

        selected = merge[
            merge["Score"] >= threshold
        ].copy()

        selected = selected.sort_values(
            "Score",
            ascending=False
        )

        print()

        print("=" * 80)
        print("SELECTED PARAMETERS")
        print("=" * 80)

        print(
            selected.to_string(
                index=False
            )
        )

        return selected["Parameter"].tolist()