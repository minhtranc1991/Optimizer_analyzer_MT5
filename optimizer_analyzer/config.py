"""Tunable settings. Plain class attributes, read as Config.NAME."""


class Config:
    RANDOM_STATE = 42

    # Pre-filter (applied before scoring so outliers don't distort scaling)
    MIN_TRADES = 100          # None to disable
    MAX_EQUITY_DD = None      # percent, None to disable

    # Stability filter
    TOP_PERCENT = 0.50
    USE_RELATIVE_GAP = True
    RELATIVE_GAP_PERCENTILE = 0.50
    # Sets strong on both periods bypass the gap filter ("elite" list)
    ELITE_MIN_FORWARD = 60
    ELITE_MIN_BACK = 60

    # Score weights (sum = 1)
    W_FORWARD = 0.45
    W_BACK = 0.10
    W_PROFIT_FACTOR = 0.10
    W_SHARPE = 0.10
    W_CONSISTENCY = 0.05
    W_QUALITY = 0.10          # Sharpe * PF * Consistency
    W_DRAWDOWN = 0.10
    OUTLIER_CLIP = (0.01, 0.99)   # quantiles clipped before MinMax scaling

    # Parameter selection: median | cumulative | relative | top_n | all
    SELECT_MODE = "cumulative"
    SELECT_CUMULATIVE = 0.80  # cumulative: keep params until this share of importance
    SELECT_RELATIVE = 0.50    # relative: keep score >= this * best score
    SELECT_TOP_N = 3          # top_n
    SELECT_MIN = 2            # never keep fewer than this

    # Neighbourhood: radius in MinMax space per sqrt(n_params)
    NEIGHBOUR_RADIUS = 0.15

    # Clustering
    MAX_CLUSTERS = 10
    MIN_AVG_CLUSTER = 8       # k <= rows / this, avoids fragmenting small samples
    MIN_CLUSTER_SIZE = 3      # clusters smaller than this can't be recommended

    # Cluster score weights (sum = 1)
    CS_FORWARD = 0.30
    CS_CONSISTENCY = 0.25
    CS_NEIGHBOUR = 0.25
    CS_SIZE = 0.20
