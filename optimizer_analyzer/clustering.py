"""KMeans on the selected parameters; k chosen by silhouette."""
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler

from .config import Config


def cluster_sets(df, parameters):
    df = df.copy()
    X = MinMaxScaler().fit_transform(df[parameters])

    best_k, best_score, best_labels = 1, float("nan"), [0] * len(df)
    n_distinct = len(df[parameters].drop_duplicates())
    for k in range(2, min(Config.MAX_CLUSTERS, len(df) // Config.MIN_AVG_CLUSTER, n_distinct - 1) + 1):
        labels = KMeans(
            n_clusters=k, random_state=Config.RANDOM_STATE, n_init=20
        ).fit_predict(X)
        score = silhouette_score(X, labels)
        if best_k == 1 or score > best_score:
            best_k, best_score, best_labels = k, score, labels

    print()
    print("=" * 80)
    print(f"Optimal clusters : {best_k}")
    print(f"Silhouette Score : {best_score:.4f}")

    df["Cluster"] = best_labels
    return df
