# Point-in-Time Financial ML and Walk-Forward Validation

**Status: methodological extension under review. Not yet an empirical thesis result.**

This module adds an independently testable data-availability ledger and a chronological baseline engine to the pharmaceutical equity-direction thesis. It is built to prevent publication-timing leakage and stale-label leakage; it does **not** solve issues in unavailable raw data or invent model performance.

## Research question

Can company financial and market features, known **as of the actual forecasting date**, predict next-quarter pharmaceutical-equity direction out of sample? Is any signal better than a majority-class baseline, and does it survive different historical quarters and market conditions?

The parent thesis currently reports a **preliminary** panel of 3,375 company-quarter observations, 29 firms and 16 predictors. This software has **not** been fitted to that panel here because the dated feature-and-label ledger needed for a valid point-in-time evaluation was not contained in the October 9 presentation/report handoff. Results must not be inferred from CI synthetic fixtures.

## The two input ledgers (no fictional release timestamps)

1. `features.csv`: `company,prediction_asof,feature,value,published_at,source_id`
2. `labels.csv`: `company,prediction_asof,target_end,label_available_at,target_label`

Every `source_id` should reference an inspectable S&P data export, dated company disclosure, price-vendor snapshot or actual exchange record. `published_at` means **first publicly available date** for that feature value, not the quarter-end date or the date it was exported to disk. Restated fundamentals may not be silently backfilled into earlier prediction dates. For technical indicators, the source time must respect the market-close cutoff and only use observable prior bars.

The source market/financial data, filing timestamps, point-in-time adjusted prices, company identifiers and delisted-company coverage require separate validation. Merely populating these fields does not establish correctness.

## Implemented integrity gates

- One row per `company,prediction_asof,feature`, one binary outcome per `company,prediction_asof`; rejected duplicates and unmatched joins.
- Feature release `published_at <= prediction_asof` and finite feature values, with nonempty source identifiers.
- Future outcome `target_end > prediction_asof`; outcome publication `label_available_at >= target_end`.
- Training rows only enter a fold when their **labels were known by that fold's fit cutoff**.
- Expanding or rolling training cohorts; optional per-quarter gap and day-based embargo.
- Train-only median imputation and feature scaling; no fitting preprocessing on test data.
- Majority/prior-probability baseline and logistic L2 baseline; per-fold accuracy, balanced accuracy, Brier score, ROC-AUC only when both test labels are present.
- Fail-closed default for `STAR.NS` while its adjustment/source issue remains unresolved. An explicit CLI override is available only after independent verification.

## Execute tests and an obviously synthetic demonstration

```bash
python -m pip install -r analysis/point_in_time/requirements.txt
python -m unittest discover -s analysis/point_in_time/tests -p "test_*.py" -v

python -m analysis.point_in_time.synthetic_demo --out /tmp/thesis_demo
python -m analysis.point_in_time.run \
  --features /tmp/thesis_demo/synthetic_features.csv \
  --labels /tmp/thesis_demo/synthetic_labels.csv \
  --out /tmp/thesis_demo/run --min-history 4
```

All `SYNTHETIC_*` company identifiers are simulated by a seeded generator. **These outputs are not thesis observations, evidence of alpha or historical investment results.** GitHub Actions runs only the above synthetic/leakage tests.

## Running against real dated data

```bash
python -m analysis.point_in_time.run \
  --features PATH_TO_VERIFIED_FEATURE_LEDGER.csv \
  --labels PATH_TO_VERIFIED_OUTCOME_LEDGER.csv \
  --out PRIVATE_RESEARCH_OUTPUTS \
  --min-history 6 --test-periods 1 --gap-periods 1 --embargo-days 0
```

The runner records SHA-256 hashes of input CSVs, fold metrics, test predictions and a run manifest. **Keep actual licensed S&P extracts and company-level source documents private** unless release rights are confirmed. Do not commit the full data, private IDs or non-public vendor outputs.

## Outstanding steps before thesis claims

1. Recover and standardize actual stock-price adjustments (including STAR.NS), delistings and corporate identifiers.
2. Recover financial filing/publication timestamps; document exactly when each covariate could first have been known.
3. Validate the 3,375-row original panel, 29 companies, 16 predictors and next-quarter binary label against source files; harmonize task wording (stock-price direction versus profitability).
4. Run chronological and company-held-out evaluations on those verified data, with no release-timing leakage.
5. Add risk-adjusted economic evaluation **only after** confirming a valid predictive task. A predicted direction is not a profit claim.

See [DATA_CONTRACT.md](DATA_CONTRACT.md) for field definitions and a checklist for raw-source reconciliation.
