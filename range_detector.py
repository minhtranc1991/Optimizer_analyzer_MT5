# ============================================================
# RANGE GENERATOR
# ============================================================
from plateau_detector import PlateauDetector

class RangeGenerator:

    @staticmethod
    def generate(
            df,
            parameters):

        print()

        print("=" * 80)
        print("OPTIMIZATION RANGES")
        print("=" * 80)

        for cluster in sorted(df["Cluster"].unique()):

            print()
            print(f"Cluster {cluster}")

            sub = df[
                df["Cluster"] == cluster
            ]

            plateau = PlateauDetector.analyse(

                sub,
                parameters
            )

            for p in parameters:
                info = plateau[p]

                print(
                    f"{p:<30}"
                    f"{info['q25']:.4f}"
                    " -> "
                    f"{info['q75']:.4f}"
                    f" | center={info['center']}"
                    f" | std={info['std']:.3f}"
                )