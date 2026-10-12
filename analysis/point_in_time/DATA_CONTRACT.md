# Thesis source-data contract and blockers

## Required feature ledger

| Field | Description | Rule |
|---|---|---|
| company | Stable security identifier | Harmonize ticker changes and cross-listings |
| prediction_asof | UTC timestamp when prediction was hypothetically made | Forecast made only after last included observable close/release |
| feature | Predictor name | One value per company/time/feature |
| value | Numeric predictor value | Finite; absent feature can be omitted, to be imputed on training only |
| published_at | Actual initial public availability timestamp | Must not be later than prediction_asof |
| source_id | Traceable disclosure, price snapshot or vendor record | Never a fabricated placeholder on real data |

Examples of invalid proxies for publication date: fiscal quarter end, a statement's accounting-period label, current date when user exported a file, artificially imposed fixed lag with no justification.

## Required outcome ledger

| Field | Description | Rule |
|---|---|---|
| company | Same stable security identifier | Complete one-to-one feature join |
| prediction_asof | Prediction timestamp | Matches feature ledger cohort |
| target_end | Actual future evaluation endpoint | Strictly after prediction date |
| label_available_at | Earliest time this outcome could have been observed | Not before target_end |
| target_label | 1 for declared upward-direction definition, else 0 | Outcome definition and close convention must be documented |

The binary target construction, return cutoff, costs, exchanges, dividend/split adjustments and currency conventions are **not encoded** in the input schema and must be checked separately before any reported results are used.

## Parent thesis status (12 October 2026)

- Research focus: next-quarter pharmaceutical stock direction; the term profitability is a separate financial target and must not be substituted casually.
- Preliminary reported panel: 3,375 firm-quarter observations, 29 represented companies, 16 predictors; independently reconstructing from raw statements remains pending.
- The parent repository itself reports a STAR.NS corporate-action adjustment blocker.
- The October 9 handoff ZIP contains report, slides, Overleaf bundle and demonstration dashboard but no single validated point-in-time raw panel.
- The September master-data ZIP and work archives are source collections; simply possessing them does not establish a clean, publishable experiment.
- The run module produces **no empirical findings without feature.csv/label.csv ledgers**. CI uses clearly named SYNTHETIC_* identifiers.

## Next research milestones

1. Build a company-by-company availability table from the actual filings and S&P observations, including amendments and restatements.
2. Reconcile corporate-action adjusted total returns and ticker histories; record discrepancy decisions.
3. Export the actual point-in-time feature ledger, with proofs for release dates.
4. Run this framework and compare baseline-balanced accuracy, ROC-AUC, Brier scores and fold-by-fold stability.
5. Add company-held-out tests, bootstrap confidence intervals, and later realistic simulated investment costs, only after input provenance is settled.

Any change from 3,375/29/16 must be documented as an explicit new sample version.
