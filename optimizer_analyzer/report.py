"""Console output helpers."""
from pathlib import Path

from .features import parameter_columns


def print_top_stable(df, n=20):
    print()
    print("=" * 80)
    print("TOP STABLE PARAMETER SETS (by Quality)")
    print("=" * 80)
    cols = ["Forward Result", "Back Result", "Gap", "RelativeGap",
            "Consistency", "Quality", "FinalScore"] + parameter_columns(df)
    top = df.sort_values(["Quality", "FinalScore"], ascending=False).head(n)
    print(top[[c for c in cols if c in df.columns]].to_string(index=False))


def print_elite(elite, parameters):
    print()
    print("=" * 80)
    print("ELITE SETS (Forward & Back above threshold)")
    print("=" * 80)
    if elite.empty:
        print("none")
        return
    cols = ["Forward Result", "Back Result", "RelativeGap", "FinalScore"] + parameters
    print(elite[cols].sort_values("FinalScore", ascending=False).to_string(index=False))


def print_run_summary(result, xml_file, html_path, run_dir):
    """Short console summary; the full detail lives in report.txt / report.html."""
    full, stable, elite = result["full"], result["stable"], result["elite"]
    best = result["summary"].iloc[0]
    line = "=" * 72

    print(line)
    print(Path(xml_file).name)
    print(line)
    print(f"Sets    : {result['n_raw']:,} raw -> {len(full):,} pre-filter -> "
          f"{len(stable):,} stable ({len(elite):,} elite)")
    print(f"Params  : {len(result['parameters'])} selected -> {', '.join(result['parameters'])}")
    print(f"Cluster : #{int(best['Cluster'])} of {len(result['summary'])} "
          f"(n={int(best['Count'])}, score {best['ClusterScore']:.3f}) | "
          f"Fwd {best['ForwardMedian']:.1f}  Back {best['BackMedian']:.1f}  "
          f"Consistency {best['Consistency']:.2f}")
    print()
    print("Recommended ranges")
    for r in result["ranges"].itertuples():
        print(f"  {r.Parameter:<24}{r.Low:>10g} -> {r.High:<10g} center {r.Center:g}")

    if len(stable) and len(elite) / len(stable) > 0.8:
        print(f"  ! Elite is {len(elite) / len(stable):.0%} of stable: raise ELITE_MIN_FORWARD/BACK")
    if not best["Eligible"]:
        print("  ! no cluster reached MIN_CLUSTER_SIZE: low confidence")

    print()
    print(f"Report : {html_path}")
    print(f"Files  : {run_dir}  (report.txt = full console report, or run with -v)")
