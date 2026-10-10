"""Choose which parameters to optimise, from importance scores."""
from .config import Config

MODES = ("median", "cumulative", "relative", "top_n", "all")


def select_parameters(profit_importance, consistency_importance):
    merged = profit_importance.merge(
        consistency_importance, on="Parameter", suffixes=("_Profit", "_Consistency")
    )
    merged["Score"] = (merged["Importance_Profit"] + merged["Importance_Consistency"]) / 2
    merged = merged.sort_values("Score", ascending=False).reset_index(drop=True)

    mode = Config.SELECT_MODE
    if mode not in MODES:
        raise ValueError(f"SELECT_MODE must be one of {MODES}, got {mode!r}")

    score = merged["Score"]
    if mode == "median":
        keep = score >= score.median()
    elif mode == "cumulative":
        # keep until the running share reaches the target (the crossing param is kept)
        keep = (score.cumsum() - score) / score.sum() < Config.SELECT_CUMULATIVE
    elif mode == "relative":
        keep = score >= Config.SELECT_RELATIVE * score.max()
    elif mode == "top_n":
        keep = score.index < Config.SELECT_TOP_N
    else:
        keep = score == score

    keep = keep | (score.index < Config.SELECT_MIN)
    selected = merged[keep]

    print("=" * 80)
    print(f"SELECTED PARAMETERS (mode={mode})")
    print("=" * 80)
    print(selected.to_string(index=False))
    return selected["Parameter"].tolist()
