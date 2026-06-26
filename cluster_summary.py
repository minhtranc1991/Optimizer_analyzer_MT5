# ============================================================
# CLUSTER SUMMARY
# ============================================================
import pandas as pd

class ClusterSummary:

    @staticmethod
    def build(
            df,
            parameters):

        rows = []

        for cluster in sorted(
                df["Cluster"].unique()):

            sub = df[df["Cluster"] == cluster]

            row = {
                "Cluster": cluster,
                "Count": len(sub),
                "ForwardMedian": sub["Forward Result"].median(),
                "BackMedian": sub["Back Result"].median(),
                "GapMedian": sub["Gap"].median(),
                "RelativeGap": sub["RelativeGap"].median(),
                "Consistency": sub["Consistency"].median(),
                "NeighbourScore": sub["NeighbourScore"].mean(),
                "FinalScore": sub["FinalScore"].mean()
            }

            for p in parameters:
                row[p] = sub[p].median()

            rows.append(row)

        summary = pd.DataFrame(rows)

        summary["ClusterScore"] = (
            0.40 * (summary["ForwardMedian"] / summary["ForwardMedian"].max())
            + 0.30 * summary["Consistency"]
            + 0.30 * (summary["NeighbourScore"] / summary["NeighbourScore"].max())
        )

        summary = summary.sort_values(
            "ClusterScore",
            ascending=False
        )

        print()

        print("=" * 80)
        print("CLUSTER SUMMARY")
        print("=" * 80)

        print(
            summary.to_string(
                index=False
            )
        )

        return summary