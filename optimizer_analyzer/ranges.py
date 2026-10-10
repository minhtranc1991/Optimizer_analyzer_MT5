"""Optimisation range per parameter: IQR of a cluster, never narrower than one grid step."""
import pandas as pd


def grid_step(full, parameter):
    """Smallest spacing between distinct tested values (the optimiser's step)."""
    values = sorted(full[parameter].dropna().unique())
    return float(pd.Series(values).diff().min()) if len(values) > 1 else 0.0


def parameter_ranges(sub, full, parameters):
    """DataFrame: Parameter, Low, High, Center (median), Std, Step."""
    rows = []
    for p in parameters:
        s = sub[p]
        step = grid_step(full, p)
        low, high = s.quantile(0.25), s.quantile(0.75)
        if high - low < step:  # widen collapsed range around the median
            half = step / 2
            low, high = min(low, s.median() - half), max(high, s.median() + half)
        # never recommend values outside what was actually tested
        low, high = max(low, full[p].min()), min(high, full[p].max())
        rows.append({
            "Parameter": p, "Low": low, "High": high,
            "Center": s.median(), "Std": s.std(), "Step": step,
        })
    return pd.DataFrame(rows)


def print_ranges(stable, full, parameters):
    print()
    print("=" * 80)
    print("OPTIMIZATION RANGES")
    print("=" * 80)
    for cluster, sub in stable.groupby("Cluster"):
        print(f"\nCluster {cluster} (n={len(sub)})")
        for r in parameter_ranges(sub, full, parameters).itertuples():
            print(
                f"{r.Parameter:<28}{r.Low:.4f} -> {r.High:.4f}"
                f" | center={r.Center:.4f} | std={r.Std:.3f}"
            )
