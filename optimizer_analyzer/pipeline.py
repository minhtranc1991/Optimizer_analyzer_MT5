"""Full analysis flow. Everything printed is also saved to output/<stem>_report.txt."""
import contextlib
import io
import sys
from pathlib import Path

import pandas as pd

from .cluster_summary import summarise_clusters
from .clustering import cluster_sets
from .features import build_features
from .filtering import prefilter, stability_filter
from .importance import importance_report
from .loader import load_report
from .neighbourhood import analyse_neighbourhood
from .plots import write_html_report
from .ranges import print_ranges
from .recommend import build_recommendation
from .report import print_elite, print_top_stable
from .scoring import build_score
from .selection import select_parameters


class _Tee(io.TextIOBase):
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)
        return len(s)


def _analyse(xml_file):
    print(f"Loading {xml_file}")
    raw = build_features(load_report(xml_file))
    df = prefilter(raw)

    # Importance first, on the full set: independent of the stability filter.
    profit_imp, cons_imp = importance_report(df)
    parameters = select_parameters(profit_imp, cons_imp)

    df = build_score(df)
    stable, elite = stability_filter(df)
    print_elite(elite, parameters)

    stable = analyse_neighbourhood(df, stable, parameters)
    stable = cluster_sets(stable, parameters)

    print_top_stable(stable)
    summary = summarise_clusters(stable, parameters)
    print_ranges(stable, df, parameters)
    ranges = build_recommendation(summary, stable, df, parameters)
    return {
        "full": df, "stable": stable, "elite": elite, "parameters": parameters,
        "profit_importance": profit_imp, "consistency_importance": cons_imp,
        "summary": summary, "ranges": ranges, "n_raw": len(raw),
    }


def run(xml_file, output_dir="output"):
    """Run the whole flow, then save text report, CSVs and the HTML charts."""
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    out = Path(output_dir)
    out.mkdir(exist_ok=True)
    stem = Path(xml_file).stem

    buf = io.StringIO()
    result = None
    try:
        with contextlib.redirect_stdout(_Tee(sys.stdout, buf)):
            result = _analyse(xml_file)
    finally:  # keep the partial report even if a step crashed
        (out / f"{stem}_report.txt").write_text(buf.getvalue(), encoding="utf-8")

    result["ranges"].to_csv(out / f"{stem}_ranges.csv", index=False)
    result["stable"].to_csv(out / f"{stem}_stable.csv", index=False)
    result["summary"].to_csv(out / f"{stem}_clusters.csv", index=False)
    write_html_report(result, out / f"{stem}_report.html", title=stem)

    print(f"\nSaved to {out.resolve()}: {stem}_report.txt/.html, _ranges/_stable/_clusters.csv")
    return result
