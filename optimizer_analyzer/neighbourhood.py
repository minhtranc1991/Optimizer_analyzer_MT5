"""Score each stable set by how good its neighbours are on the FULL grid."""
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

from .config import Config

STATS = {
    "NeighbourScore": ("FinalScore", np.mean),
    "NeighbourForward": ("Forward Result", np.median),
    "NeighbourGap": ("Gap", np.median),
    "NeighbourConsistency": ("Consistency", np.median),
}


def analyse_neighbourhood(full, stable, parameters):
    scaler = MinMaxScaler().fit(full[parameters])
    radius = Config.NEIGHBOUR_RADIUS * np.sqrt(len(parameters))
    nn = NearestNeighbors(radius=radius).fit(scaler.transform(full[parameters]))
    neighbours = nn.radius_neighbors(
        scaler.transform(stable[parameters]), return_distance=False
    )
    self_pos = full.index.get_indexer(stable.index)

    out = stable.copy()
    cols = {name: [] for name in STATS}
    counts = []
    for pos, ids in zip(self_pos, neighbours):
        ids = ids[ids != pos]  # exclude the point itself
        counts.append(len(ids))
        sub = full.iloc[ids]
        for name, (col, fn) in STATS.items():
            # isolated point (no neighbours) scores 0: no evidence of a plateau
            cols[name].append(fn(sub[col]) if len(ids) else 0.0)

    out["NeighbourCount"] = counts
    for name, values in cols.items():
        out[name] = values
    return out
