# ============================================================
# NEIGHBOURHOOD ANALYZER
# ============================================================
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

class NeighbourhoodAnalyzer:

    @staticmethod
    def analyse(
            df,
            parameters,
            radius=0.25):

        scaler = MinMaxScaler()

        X = scaler.fit_transform(
            df[parameters]
        )

        nn = NearestNeighbors(
            radius=radius
        )

        nn.fit(X)

        neighbors = nn.radius_neighbors(
            X,
            return_distance=False
        )

        neighbour_score = []
        neighbour_forward = []
        neighbour_gap = []
        neighbour_consistency = []

        for ids in neighbors:
            sub = df.iloc[ids]
            neighbour_score.append(
                sub["FinalScore"].mean()
            )
            neighbour_forward.append(
                sub["Forward Result"].median()
            )
            neighbour_gap.append(
                sub["Gap"].median()
            )
            neighbour_consistency.append(
                sub["Consistency"].median()
            )

        df = df.copy()

        df["NeighbourCount"] = [
            len(i)
            for i in neighbors
        ]
        df["NeighbourScore"] = neighbour_score
        df["NeighbourForward"] = neighbour_forward
        df["NeighbourGap"] = neighbour_gap
        df["NeighbourConsistency"] = neighbour_consistency

        return df