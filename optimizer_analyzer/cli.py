"""Pipeline entry: python -m optimizer_analyzer <report.xml>"""
import argparse
from pathlib import Path

import pandas as pd

from .cluster_summary import summarise_clusters
from .clustering import cluster_sets
from .features import build_features
from .filtering import prefilter, stability_filter
from .importance import importance_report
from .loader import load_report
from .neighbourhood import analyse_neighbourhood
from .ranges import print_ranges
from .recommend import build_recommendation
from .report import print_elite, print_top_stable
from .scoring import build_score
from .selection import select_parameters


def run(xml_file, output_dir="output"):
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    print(f"Loading {xml_file}")
    df = prefilter(build_features(load_report(xml_file)))

    # Importance first, on the full set: independent of the stability filter.
    parameters = select_parameters(*importance_report(df))

    df = build_score(df)
    stable, elite = stability_filter(df)
    print_elite(elite, parameters)

    stable = analyse_neighbourhood(df, stable, parameters)
    stable = cluster_sets(stable, parameters)

    print_top_stable(stable)
    summary = summarise_clusters(stable, parameters)
    print_ranges(stable, df, parameters)
    ranges = build_recommendation(summary, stable, df, parameters)

    out = Path(output_dir)
    out.mkdir(exist_ok=True)
    stem = Path(xml_file).stem
    ranges.to_csv(out / f"{stem}_ranges.csv", index=False)
    stable.to_csv(out / f"{stem}_stable.csv", index=False)
    return ranges


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml_file", help="MT5 optimization report (XML)")
    parser.add_argument("-o", "--output-dir", default="output")
    args = parser.parse_args()
    run(args.xml_file, args.output_dir)
