# ============================================================
# PLATEAU DETECTOR
# ============================================================

class PlateauDetector:

    @staticmethod
    def analyse(df, parameters):

        plateau = {}

        for p in parameters:
            s = df[p]
            mode = s.mode()

            if len(mode):
                center = mode.iloc[0]

            else:
                center = s.median()

            plateau[p] = {
                "center": center,
                "median": s.median(),
                "mean": s.mean(),
                "std": s.std(),
                "q10": s.quantile(0.10),
                "q25": s.quantile(0.25),
                "q75": s.quantile(0.75),
                "q90": s.quantile(0.90),
                "min": s.min(),
                "max": s.max()
            }

        return plateau