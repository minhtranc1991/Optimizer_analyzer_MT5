# ============================================================
# CONFIG
# ============================================================
from dataclasses import dataclass

@dataclass
class Config:

    TOP_PERCENT = 0.50

    # Stable filter
    USE_RELATIVE_GAP = True
    RELATIVE_GAP_PERCENTILE = 0.50

    # Score weights
    W_FORWARD = 0.45
    W_BACK = 0.10
    W_PROFIT_FACTOR = 0.10
    W_SHARPE = 0.10
    W_CONSISTENCY = 0.15
    W_DRAWDOWN = 0.10

    RANDOM_STATE = 42

    MAX_CLUSTERS = 10

    SHAP_THRESHOLD = "median"