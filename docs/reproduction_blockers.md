# Reproduction blocker

## Current decision: 9 September 2026

**BLOCKED BEFORE TRAINING: the missing item is source-backed confirmation of the correct continuous STAR.NS price basis across the December 2024 OneSource demerger.** The earlier missing-feature-dictionary decision below is historical and was superseded by the subsequently supplied executable pipeline. The current user explicitly authorises an honest preliminary report while the empirical rebuild is blocked.

The new report is `thesis_output/OVERLEAF_SUBMISSION_PROJECT_FINAL/Thesis_Final.tex`. It labels the existing numerical results as preliminary and superseded for the intended 2015--2026 study. No models were refitted, retuned or definitively selected. No `reproduction_verified` empirical pipeline was created because its gate remains uncleared.

### Exact source evidence

Paths are relative to `C:\Users\yuktha\Downloads\research project(4)`. Define **S** as `thesis_output/reproduction/friend_package/research project/YUKTHA_CLEAN_2026-09-07/01_INDIAN_COMPANIES/Strides_Pharma_Science/`.

| Series | Exact source relative to S | Coverage and schema |
|---|---|---|
| A | `04_OTHER_SOURCE_MATERIAL/Strides_Pharma_Science_yahoo_adjusted_close_supplement.csv` | 2002-06-26 to 2026-09-01; adjusted OHLC and Adj_Close, volume, dividend/split fields; no ticker column. Yahoo origin is stated by filename/documentary selection. |
| B | `02_MARKET_DATA/Daily/Strides_Pharma_Science_daily.csv` | 2014-08-01 to 2026-08-19; OHLCV, Company, Country, Ticker=STAR.NS; no adjustment/action fields or demonstrated distribution-adjustment methodology. |
| C | `02_MARKET_DATA/Daily/Strides_Pharma_Science_STAR_NS_daily.csv` | 2002-06-26 to 2026-09-01; Close, Adj Close, OHLCV and action fields. Ticker is in filename; the event discontinuity persists in both Close and Adj Close. |
| Merged | `04_OTHER_SOURCE_MATERIAL/Strides_Pharma_Science__stock__daily.csv` | Complementary Close and adjusted_close blocks, with source-dependent symbol/action fields; preserves conflicting bases rather than supplying independent authority. |

Both weekly and both monthly files under `S/02_MARKET_DATA/` were also read. They are derived representations, not independent adjustment authority. Aggregate labels may extend beyond the last underlying supplied trading date and cannot certify complete target quarters. All eight filenames, columns, date coverage, ticker values and exact event rows are in `thesis_output/OVERLEAF_SUBMISSION_PROJECT_FINAL/evidence/strides_series_profiles.json`.

`S/SOURCE_INDEX.csv:12-19` links market files to original source paths but supplies no vendor adjustment specification. `.../00_MASTER_AUDIT_AND_METADATA/THESIS_COMPLETE_WORK_AND_NEXT_STEPS.md:164-165` states that the adjusted Yahoo supplement was retained. `pipeline/lib/companies.py:STOCK_SERIES_OVERRIDE` and `pipeline/_02_clean_stock.py:select_canonical_block` implement that choice. These records do not explain how distributed OneSource value entered the prices.

| Date | A: physical CSV line / Adj_Close | B: physical CSV line / Close |
|---|---|---|
| 2024-09-30 | 5531 / 1386.2142333984375 | 2515 / 633.76 |
| 2024-12-05 | 5576 / 1471.4779052734375 | 2560 / 672.75 |
| 2024-12-06 | 5577 / 676.3120727539062 | 2561 / 676.31 |
| 2024-12-31 | 5593 / 653.3735961914062 | 2577 / 653.37 |

A implies -0.528663333235587 (target 0) for the 2024-09-30 observation ending 2024-12-31; B implies +0.03094231254733655 (target 1). A has zero dividend/split fields on the event date, which does not exclude a demerger. C lines 5576-5577 show Close 1485.050048828125 to 682.5499877929688 and Adj Close 1471.4779052734375 to 676.31201171875. A and C also have different latest prices on 2026-09-01; their names do not certify equivalent continuous histories.

The issuer's [11 December 2024 notice, page 1](https://www.strides.com/Upload/PDF/strides-se-intimation-allotment-12dec2024.pdf) confirms STAR, the 6 December record date and one OneSource share for two Strides shares. It supplies no historical adjustment factor or continuous series. The share entitlement ratio is not itself a price-adjustment factor.

### Retained exposure and interpretation

Define **V** as `thesis_output/reproduction_clean_2015_2026/validation_warmup_2015_2026/`. `V/candidate_target_panel.csv:445` contains the retained A-based 2024-09-30 Strides test observation; `V/price_flags.csv:70` logs the event. `V/flag_panel_dependencies.csv:147-151` traces it to:

- 2024-09-30: the next-quarter target crosses the event and changes direction between A and B.
- 2024-12-31: 50/200-day means, 60/120-day volatility, volume-window row, and 91/182/365-day return intervals.
- 2025-03-31: 200-day mean, 120-day volatility, and 182/365-day return intervals.
- 2025-06-30 and 2025-09-30: 365-day return intervals.

These are retained test observations. Changed truths alter confusion counts and may alter all metrics, including AUC. Changed features may alter predictions/scores. A continuous-source revision affecting training or validation history may also change preprocessing, fitted models and validation ranking. A correction confined to test data does not itself change validation selection. No counterfactual model metrics were generated.

The checkpoint uses pre-2015 history only as feature warmup and has 1,247 retained price candidates (783/203/261), with no fitted models. The saved preliminary metrics are unchanged and belong to a long training history beginning in 1962, including old Glenmark anomalies and mixed Fosun listings. Future Fosun construction is restricted to `Shanghai_Fosun_Pharma_600196_SS_daily.csv` / `600196.SS`.

### Minimal next decision

Obtain a source/vendor-confirmed continuous STAR.NS series with the explicit return convention and distribution-adjustment methodology. Prefer a shareholder-return-consistent basis for the financial-return interpretation. Parent-company price-only treatment would require an explicit economic-definition decision and source verification. Do not choose the favourable label, infer a factor from the entitlement, silently substitute B or remove Strides.

Sanofi identity/currency, other severe-price interpretation, unchanged zero-volume flat-row treatment, statement/YTD comparability and actual publication-date handling also require clearance. Further price evidence remains in `FINAL_REBUILD_BLOCKERS.md`. The new report may be compiled and reviewed as preliminary, but model training must remain stopped.

## Historical decision (preserved; superseded by later supplied code)

## Decision

The available files are insufficient to reproduce the documented company-quarter, combined market-and-fundamentals research project experiment. Stop before model fitting and creation of `Thesis_Final.docx` or `Thesis_Final.pdf`. Existing `Thesis_Draft` files and original sources are preserved.

This does **not** establish that the raw data cannot support any new classification study. It establishes that the intended predictor matrix is underdetermined: a newly chosen feature design would be a new experiment, not a reconstruction of the documented one.

## Single concrete missing analytical input

**The complete feature-construction specification for the documented 22 predictors: exact formulas and their mappings to the raw source fields.**

One self-contained feature dictionary is sufficient to supply this input; it need not be another final-model package. The original executable feature-building script/notebook with its dependencies would also supply it if it fully defines the same transformations.

For each predictor, the specification must identify its name, formula, input source/field, units, lookback window and shift, and missing/undefined-value treatment. Where relevant, it must resolve quarterly versus annual fallback, fiscal/YTD-to-quarter conversion, publication/availability timing, and staleness. These are parts of the same feature definition, not separate requests for trained outputs.

## Evidence supporting the decision

The supplied file

`research project/YUKTHA_FINAL_MASTER_DATA_2026-09-02_ORGANIZED/00_MASTER_AUDIT_AND_METADATA/THESIS_COMPLETE_WORK_AND_NEXT_STEPS.md`

states in Section 15 (lines 240â€“246):

- There are 11 market and 11 fundamental predictors.
- Their exact formulas and source-field mappings reside in the project's feature dictionary and feature-building scripts.
- Definitive formulas must come from those artifacts rather than generic examples.

Only feature families are described: momentum, moving averages, volatility, volume, profitability, leverage, liquidity, growth and valuation. Those families do not specify a unique numerical design matrix. For example, a momentum family does not identify its horizon; a growth family does not determine quarter-on-quarter versus year-on-year construction or treatment of cumulative reporting.

Section 4's six weekly preliminary features belong to an explicitly different experiment. They cannot fill the missing definitions for the final quarterly combined-feature study.

Section 11 reports historical panel dimensions, and Sections 12â€“13 and 17 describe the target, broad availability rules, split and eight-model process. These provide useful reconstruction constraints but cannot recover the missing predictor values. The reported 1,410 rows and historical model metrics are not substitutes for the feature specification.

The completed content inspection in `thesis_output/content_inspection.jsonl`, `inspection_summary.json`, and `content_search_hits.json` did not locate the referenced executable analysis or definitive dictionary. The saved `new_evidence_delta_check.json` confirms that all 7,991 source files matched the earlier inspection with no additions or changed contents at that checkpoint. The user has since confirmed that no additional final-model package exists.

For this assessment, the historical work summary was reread and a targeted search of `00_MASTER_AUDIT_AND_METADATA` for feature definitions, dictionary references, representative predictor names and the 22-feature description found narrative references rather than the required definitions. No broad source inventory was repeated.

## Why training cannot resolve this input

Eight classifiers can be implemented and trained without original fitted objects or saved predictions. Their genuine new predictions, confusion matrices and ROC curves could then be calculated. Missing historical trained objects or hyperparameters are therefore not the single gating input identified here.

However, training requires a defined predictor matrix. Selecting convenient features from the raw columns would introduce analytical choices not established by the supplied study. Attempting to recover those choices by matching historical held-out scores would also use test outcomes to guide the design. Neither procedure is a defensible reproduction.

Once the complete feature specification is available, it can be implemented against the preserved raw inputs, with explicit source reconciliation, a frozen chronological evaluation design and recorded model settings. Further data sufficiency and leakage checks would then be necessary; their success is not assumed here. Alternatively, explicit authorization to design a new feature specification would change the task to a new raw-data experiment, whose results must be labelled accordingly rather than presented as recovered historical results.

## Work status and presentation requirements retained

No models were fitted, no metrics were generated, and no new empirical verification or final-document QA is claimed. No `Thesis_Final` files were created. The draft backups were not edited, including their existing reference content.

For any subsequent final report, the latest instructions remain controlling: use RC Report as the primary presentation reference and the PEMFC paper as the secondary reference, study both before authoring, retain DejaVu typography, centre actual model results and interpretation, remove all CFA references/discussion from the new final report, and use Gu, Kelly and Xiu only as a brief relevant literature citation if needed. These design requirements cannot resolve the missing analytical definition.

