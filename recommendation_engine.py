# ============================================================
# FINAL RECOMMENDATION
# ============================================================

class RecommendationEngine:

    @staticmethod
    def build(
            summary,
            stable,
            parameters):

        print()
        print("=" * 80)
        print("FINAL RECOMMENDATION")
        print("=" * 80)

        best = summary.iloc[0]

        cluster = int(best["Cluster"])

        sub = stable[
            stable["Cluster"] == cluster
        ]

        print()
        print(f"Best Cluster : {cluster}")
        print(f"Cluster Score : {best['ClusterScore']:.3f}")
        print(f"Forward Median : {best['ForwardMedian']:.2f}")
        print(f"Consistency : {best['Consistency']:.3f}")
        print()
        print("Suggested Optimize Range")
        print("-" * 60)

        for p in parameters:

            q25 = sub[p].quantile(0.25)
            q75 = sub[p].quantile(0.75)

            median = sub[p].median()

            mode = sub[p].mode()

            if len(mode):
                center = mode.iloc[0]

            else:
                center = median

            print(
                f"{p:<28}"
                f"{q25:.4f}"
                " -> "
                f"{q75:.4f}"
                f" | center={center}"
            )

        print()

        print("Confidence")

        print("-" * 60)

        print(
            f"Neighbour Score : "
            f"{sub['NeighbourScore'].mean():.3f}"
        )

        print(
            f"Consistency : "
            f"{sub['Consistency'].median():.3f}"
        )

        print(
            f"Relative Gap : "
            f"{sub['RelativeGap'].median():.3f}"
        )

        print(
            f"Forward Median : "
            f"{sub['Forward Result'].median():.2f}"
        )