# ============================================================
# CLUSTER ANALYZER
# ============================================================
from config import Config
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler

class ClusterAnalyzer:

    @staticmethod
    def fit(
            df,
            parameters):

        scaler = MinMaxScaler()

        X = scaler.fit_transform(

            df[parameters]

        )

        best_score = -1

        best_model = None

        best_k = 2

        max_cluster = min(

            Config.MAX_CLUSTERS,

            len(df) - 1

        )

        for k in range(

                2,

                max_cluster + 1):

            model = KMeans(

                n_clusters=k,

                random_state=Config.RANDOM_STATE,

                n_init=20

            )

            label = model.fit_predict(X)

            score = silhouette_score(

                X,

                label

            )

            if score > best_score:

                best_score = score

                best_model = model

                best_k = k

        print()

        print("=" * 80)
        print(f"Optimal clusters : {best_k}")
        print(f"Silhouette Score : {best_score:.4f}")

        df = df.copy()

        df["Cluster"] = best_model.predict(X)

        return df