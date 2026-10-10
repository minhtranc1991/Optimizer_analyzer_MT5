"""Per-cluster medians and a ranking score."""
import pandas as pd

from .config import Config


def _norm(s):
    span = s.max() - s.min()
    return (s - s.min()) / span if span else s * 0 + 1.0


def summarise_clusters(df, parameters):
    rows = []
    for cluster, sub in df.groupby("Cluster"):
        row = {
            "Cluster": cluster,
            "Count": len(sub),
            "ForwardMedian": sub["Forward Result"].median(),
            "BackMedian": sub["Back Result"].median(),
            "GapMedian": sub["Gap"].median(),
            "RelativeGap": sub["RelativeGap"].median(),
            "Consistency": sub["Consistency"].median(),
            "NeighbourScore": sub["NeighbourScore"].mean(),
            "FinalScore": sub["FinalScore"].mean(),
        }
        row.update({p: sub[p].median() for p in parameters})
        rows.append(row)

    summary = pd.DataFrame(rows)
    summary["ClusterScore"] = (
        Config.CS_FORWARD * _norm(summary["ForwardMedian"])
        + Config.CS_CONSISTENCY * _norm(summary["Consistency"])
        + Config.CS_NEIGHBOUR * _norm(summary["NeighbourScore"])
        + Config.CS_SIZE * _norm(summary["Count"])
    )
    # Tiny clusters are noise: rank them last rather than let them win.
    summary["Eligible"] = summary["Count"] >= Config.MIN_CLUSTER_SIZE
    summary = summary.sort_values(
        ["Eligible", "ClusterScore"], ascending=False
    ).reset_index(drop=True)

    print()
    print("=" * 80)
    print("CLUSTER SUMMARY")
    print("=" * 80)
    print(summary.to_string(index=False))
    return summary
