import pandas as pd

from xml_loader import XMLLoader
from score_engine import ScoreEngine
from shap_analyzer import SHAPAnalyzer
from range_detector import RangeGenerator
from cluster_summary import ClusterSummary
from feature_engineer import FeatureEngineer
from stability_filter import StabilityFilter
from feature_selector import FeatureSelector
from cluster_analyzer import ClusterAnalyzer
from console_reporter import ConsoleReporter
from recommendation_engine import RecommendationEngine
from neighbourhood_analyzer import NeighbourhoodAnalyzer

# ============================================================
# MAIN
# ============================================================

def main(xml_file):

    pd.set_option(
        "display.max_columns",
        None
    )
    pd.set_option(
        "display.width",
        None
    )

    # --------------------------
    # Load
    # --------------------------
    df = XMLLoader.load(xml_file)

    # --------------------------
    # Features
    # --------------------------
    df = FeatureEngineer.build(df)

    # --------------------------
    # Score
    # --------------------------
    df = ScoreEngine.build(df)

    # --------------------------
    # Stable
    # --------------------------
    stable = StabilityFilter.filter(df)

    # --------------------------
    # SHAP
    # --------------------------
    profit_shap, consistency_shap = (
        SHAPAnalyzer.report(
            stable
        )
    )

    # --------------------------
    # Feature Selection
    # --------------------------
    parameters = FeatureSelector.select(
        profit_shap,
        consistency_shap
    )

    # --------------------------
    # Neighbourhood
    # --------------------------
    stable = NeighbourhoodAnalyzer.analyse(
        stable,
        parameters
    )

    # --------------------------
    # KMeans
    # --------------------------
    stable = ClusterAnalyzer.fit(
        stable,
        parameters
    )

    # --------------------------
    # Top Stable
    # --------------------------
    ConsoleReporter.top_stable(
        stable
    )

    # --------------------------
    # Cluster Summary
    # --------------------------
    summary = ClusterSummary.build(
        stable,
        parameters
    )

    # --------------------------
    # Range
    # --------------------------
    RangeGenerator.generate(
        stable,
        parameters
    )

    # --------------------------
    # Final
    # --------------------------
    RecommendationEngine.build(
        summary,
        stable,
        parameters
    )


if __name__ == "__main__":

    main("ReportOptimizer-2020-2024.xml")