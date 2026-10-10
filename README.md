# Optimizer Analyzer MT5

Python utility for analyzing MetaTrader 5 (MT5) optimization reports exported as XML and recommending robust parameter ranges.

---

## Features

- Load MT5 optimization reports from XML.
- Engineer features such as:
  - Gap
  - RelativeGap
  - Consistency
  - DDScore
- Calculate a weighted `FinalScore`.
- Filter robust parameter sets.
- Rank parameter importance using RandomForest (SHAP-like).
- Select important parameters automatically.
- Analyze local parameter neighbourhoods.
- Cluster similar parameter sets with KMeans.
- Recommend stable parameter ranges.

---

## Layout

```
optimizer_analyzer/   package (loader, features, importance, selection, scoring,
                      filtering, neighbourhood, clustering, cluster_summary,
                      ranges, recommend, report, cli, config)
data/                 MT5 optimization XML exports
output/               generated CSVs (git-ignored)
scripts/              check_mt5_connection.py (needs MetaTrader5)
tests/                smoke tests
```

Pipeline order: load -> features -> pre-filter -> importance -> parameter
selection -> score -> stability filter (+ elite list) -> neighbourhood ->
clustering -> ranges -> recommendation.

## Install

```bash
python -m venv venv && venv\Scriptsctivate
pip install -r requirements.txt
```

## Usage

```bash
python -m optimizer_analyzer data/ML_XAUUSD_M5_2026m06-07_fwd1-4_2026-07-18_r01.xml
```

Writes `output/<name>_ranges.csv` and `output/<name>_stable.csv`.
All tunables live in `optimizer_analyzer/config.py`
(`SELECT_MODE`: median | cumulative | relative | top_n | all).

## Tests

```bash
python -m pytest tests
```

## Data file naming

`<EA>_<SYMBOL>_<TF>_<period>_<fwd>_<run-date>_r<NN>.xml`, for example
`ML_XAUUSD_M5_2026m06-07_fwd1-4_2026-07-18_r01.xml`.
`period` is `2022-2026` (years) or `2026m03-06` (months); `unk` = unknown.
Run date comes from the XML `Created` field; `rNN` orders runs of the same day.
