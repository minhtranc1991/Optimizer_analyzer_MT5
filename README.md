# Optimizer Analyzer MT5

Analyses MetaTrader 5 optimization reports (XML export) and recommends **robust
parameter ranges** for the next optimization pass, instead of a single "best" set.

For one XML file it produces an interactive HTML report (charts + plain-language
comments), a full text report and CSVs.

---

## Quick start

```bash
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt

python main.py                   # newest XML in data/
python main.py data/a.xml data/b.xml
```

Open the generated `output/<name>_report.html` in a browser (works offline).

### Showcase

Run on [`data/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01.xml`](data/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01.xml)
(1,390 optimization passes):

| Output | File |
|---|---|
| Interactive report | [output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01_report.html](output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01_report.html) |
| Full console report | [output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01/report.txt](output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01/report.txt) |
| Recommended ranges | [ranges.csv](output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01/ranges.csv) |
| Stable sets + cluster | [stable.csv](output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01/stable.csv) |
| Cluster summary | [clusters.csv](output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01/clusters.csv) |

What the pipeline concluded:

- 1,390 passes -> 1,028 after the trade-count pre-filter -> 870 stable sets.
- 5 of 11 parameters selected for optimization (the other 6 are fixed at the
  best cluster's median): `setSlowMAPeriod`, `setEntryScoreBuy`,
  `setEntryScoreSell`, `setLimitATR`, `setMaxPositions`.
- 2 clusters; best cluster 1 (382 sets, Forward median 93.9, Back median 84.5,
  consistency 0.85).

Recommended ranges for the next run:

| Parameter | From | To | Center | Step |
|---|---|---|---|---|
| setSlowMAPeriod | 108 | 276 | 198 | 12 |
| setEntryScoreBuy | 47 | 55 | 51 | 1 |
| setEntryScoreSell | 51 | 57 | 54 | 1 |
| setLimitATR | 0.5 | 1.5 | 1.0 | 0.5 |
| setMaxPositions | 1 | 1.5 | 1 | 1 |

The HTML report is organised as:

1. **Summary**: funnel from raw passes to recommendation, warnings.
2. **Parameter choice**: importance table; each parameter is *optimize* or
   *fix at X*, with the reason.
3. **Charts** (each with "how to read" and data-driven comments):
   Forward vs Back, importance, 2-parameter score map, score vs each parameter,
   Forward per cluster, parallel coordinates.
4. **Clusters**: verdict per cluster (recommended / most profitable / most
   stable / too small / weak surroundings).
5. **Recommended ranges**: per-parameter comment, edge-of-tested-domain warnings.
6. **Top parameter sets**: per-set verdict (elite, overfit-to-Back, isolated
   point, few trades, high drawdown).

---

## Workflow

```
XML report
   |  loader            parse SpreadsheetML (handles skipped cells)
   v
features                Gap, RelativeGap, Consistency, DDScore, Quality
   |  filtering         pre-filter: MIN_TRADES / MAX_EQUITY_DD
   v
importance              RandomForest on the full set (Forward, Consistency)
   |  selection         SELECT_MODE: cumulative | median | relative | top_n | all
   v
scoring                 FinalScore = weighted, outlier-clipped, min-max metrics
   |  filtering         top N% by score -> low RelativeGap  (+ elite list)
   v
neighbourhood           how good are the surroundings on the FULL grid
   |  clustering        KMeans, k by silhouette (k <= rows / MIN_AVG_CLUSTER)
   v
cluster_summary         rank clusters
   |  ranges / recommend IQR range, >= 1 grid step, clipped to tested domain
   v
report.txt  report.html  ranges.csv  stable.csv  clusters.csv
```

### Key metrics

| Metric | Definition |
|---|---|
| Gap / RelativeGap | `abs(Fwd - Back)`, and that divided by `max(abs(Fwd), abs(Back))` |
| Consistency | `min(abs(Fwd), abs(Back)) / max(...)`, 1 = identical results |
| Quality | `Sharpe * ProfitFactor * Consistency` (temporary formula) |
| FinalScore | weighted sum of Forward, Back, PF, Sharpe, Consistency, Quality, drawdown score |
| Elite | `Forward > ELITE_MIN_FORWARD` and `Back > ELITE_MIN_BACK`; bypasses the gap filter |
| NeighbourScore | mean FinalScore of tested sets within a radius; isolated points score 0 |

All thresholds and weights live in [optimizer_analyzer/config.py](optimizer_analyzer/config.py).
Parameters with hard limits (e.g. `setMaxPositions >= 1`) go in `PARAM_BOUNDS`
so the report does not suggest testing beyond them.

---

## Project layout

```
main.py                 entry point
optimizer_analyzer/     package (see Workflow)
  loader  features  importance  selection  scoring  filtering
  neighbourhood  clustering  cluster_summary  ranges  recommend
  report  commentary  plots  pipeline  config
data/                   MT5 optimization XML exports
output/                 <name>_report.html + one folder per run
scripts/                check_mt5_connection.py (needs MetaTrader5)
tests/                  smoke tests
```

### Output layout

```
output/<name>_report.html        open this
output/<name>/report.txt         everything the console printed
output/<name>/ranges.csv         recommended ranges
output/<name>/stable.csv         stable sets with cluster + neighbourhood metrics
output/<name>/clusters.csv       cluster summary
```

## Data file naming

`<EA>_<SYMBOL>_<TF>_<start YYYY-MM-DD>_<fwd>_<end>_r<NN>.xml`, for example
`AMFS_v2_XAU_M5_2026-08-03_fwd1-4_10-03_r01.xml`.

- `end` is `MM-DD` of the start year, or full `YYYY-MM-DD` when the period crosses a year.
- Files exported with only a year/month range use the first/last day of that range.
- `unk` = unknown; `rNN` orders runs with the same EA and period.

## Reading the results: known limits

- **Forward and Back may cover different lengths**, so absolute `Gap` and
  `Consistency` are only comparable if the periods are similar. Check the
  Forward-vs-Back correlation in the report before trusting the ranking.
- **Elite thresholds are file-dependent.** If Elite is most of Stable the
  report warns; raise `ELITE_MIN_FORWARD/BACK`.
- **Range touching the edge of the tested domain** means the true optimum may
  lie outside it; the report flags this unless it is a `PARAM_BOUNDS` limit.
- Importance is RandomForest impurity importance, not SHAP.

## Tests

```bash
python -m pytest tests
```
