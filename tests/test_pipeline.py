"""Smoke test on synthetic data: python -m pytest tests  (or python tests/test_pipeline.py)"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from optimizer_analyzer.pipeline import run  # noqa: E402
from optimizer_analyzer.features import build_features  # noqa: E402


def synthetic(n=120, seed=0):
    r = np.random.default_rng(seed)
    df = pd.DataFrame({
        "Forward Result": r.normal(40, 15, n), "Back Result": r.normal(45, 15, n),
        "Profit Factor": r.normal(1, .2, n), "Sharpe Ratio": r.normal(0, 3, n),
        "Equity DD %": r.uniform(5, 40, n), "Trades": r.integers(50, 400, n),
        "setA": r.integers(1, 20, n) / 10, "setB": r.integers(30, 70, n),
        "setC": r.integers(0, 3, n),
    })
    df.loc[0, ["Forward Result", "Back Result"]] = 80  # elite row
    return df


def test_quality_ranks_high_sharpe_pf_first():
    df = build_features(pd.DataFrame({
        "Forward Result": [50., 50.], "Back Result": [50., 50.],
        "Sharpe Ratio": [1., 10.], "Profit Factor": [1., 1.5]}))
    assert df["Quality"].iloc[1] > df["Quality"].iloc[0]


def test_pipeline_runs_and_writes_ranges(tmp_path, monkeypatch):
    import optimizer_analyzer.pipeline as cli
    monkeypatch.setattr(cli, "load_report", lambda _: synthetic())
    ranges = run("fake.xml", tmp_path)["ranges"]
    assert (ranges["Low"] <= ranges["High"]).all()
    assert (tmp_path / "fake_ranges.csv").exists()
    assert (tmp_path / "fake_report.html").exists() and (tmp_path / "fake_report.txt").exists()


if __name__ == "__main__":
    import tempfile
    test_quality_ranks_high_sharpe_pf_first()
    test_pipeline_runs_and_writes_ranges(Path(tempfile.mkdtemp()), type("M", (), {"setattr": lambda s, o, n, v: setattr(o, n, v)})())
    print("ok")
