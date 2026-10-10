"""Final recommendation: ranges of the best eligible cluster."""
from .ranges import parameter_ranges


def build_recommendation(summary, stable, full, parameters):
    best = summary.iloc[0]
    sub = stable[stable["Cluster"] == int(best["Cluster"])]
    ranges = parameter_ranges(sub, full, parameters)

    print()
    print("=" * 80)
    print("FINAL RECOMMENDATION")
    print("=" * 80)
    print(f"\nBest Cluster   : {int(best['Cluster'])} (n={len(sub)})")
    print(f"Cluster Score  : {best['ClusterScore']:.3f}")
    print(f"Forward Median : {best['ForwardMedian']:.2f}")
    print(f"Consistency    : {best['Consistency']:.3f}")
    if not best["Eligible"]:
        print("WARNING: no cluster reached MIN_CLUSTER_SIZE; result is low-confidence")
    print("\nSuggested Optimize Range")
    print("-" * 60)
    for r in ranges.itertuples():
        print(
            f"{r.Parameter:<28}{r.Low:.4f} -> {r.High:.4f}"
            f" | center={r.Center:.4f} | step={r.Step:g}"
        )
    print("\nConfidence")
    print("-" * 60)
    print(f"Neighbour Score : {sub['NeighbourScore'].mean():.3f}")
    print(f"Consistency     : {sub['Consistency'].median():.3f}")
    print(f"Relative Gap    : {sub['RelativeGap'].median():.3f}")
    print(f"Forward Median  : {sub['Forward Result'].median():.2f}")
    return ranges
