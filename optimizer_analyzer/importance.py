"""Parameter importance via RandomForest (impurity importance, not SHAP)."""
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from .config import Config
from .features import parameter_columns


def parameter_importance(df, target):
    params = parameter_columns(df)
    X = df[params].fillna(df[params].median())
    model = RandomForestRegressor(
        n_estimators=500, random_state=Config.RANDOM_STATE, n_jobs=-1
    ).fit(X, df[target])
    out = pd.DataFrame({"Parameter": params, "Importance": model.feature_importances_})
    return out.sort_values("Importance", ascending=False).reset_index(drop=True)


def importance_report(df):
    """Importance for profit and for consistency, on the full (unfiltered) set."""
    results = []
    for title, target in (("PROFIT", "Forward Result"), ("CONSISTENCY", "Consistency")):
        imp = parameter_importance(df, target)
        print("=" * 80)
        print(f"{title} IMPORTANCE")
        print("=" * 80)
        print(imp.to_string(index=False))
        print()
        results.append(imp)
    return tuple(results)
