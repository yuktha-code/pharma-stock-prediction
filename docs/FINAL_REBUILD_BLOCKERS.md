# Final rebuild blockers

## Current checkpoint: warmup-corrected validation, 9 September 2026

**Verdict: unresolved. BLOCKED BEFORE MODEL FITTING.** The requested single validator process completed with exit code 0. No estimator was run. The command was `powershell.exe -NoProfile -ExecutionPolicy Bypass -File thesis_output\reproduction_clean_2015_2026\validate_prices.ps1`; the bypass applied only to that process. No persistent execution-policy or registry change was made.

This update supersedes the historical no-warmup scope and diagnostic counts below. Earlier diagnostic files remain untouched. New evidence is under `thesis_output/reproduction_clean_2015_2026/validation_warmup_2015_2026/` (called **V** below). The existing validator was edited as authorised; this blocker report records the requested result. Raw data, original files, prior model results and existing report projects were not modified.

### Corrected lookback and validation scope

- The first candidate observation remains 2015-03-31. Its earliest required 365-calendar-day denominator cutoff is 2014-03-31. For each selected source, the validator retains the latest supplied row at or before that cutoff and subsequent daily history. Pre-2015 rows are historical feature inputs only; no pre-2015 model observation is constructed. The 200-day diagnostic concerns the moving-average window; it is not an additional return feature.
- `V/warmup_feature_checks.csv` contains 464 source-linked checks for the 91-, 182-, 200- and 365-day lookbacks of all 2015 company-quarter candidates. None has a missing denominator anchor. For example, Glenmark's 2015-03-31 lookbacks resolve to source lines 3122 (2014-12-30), 3065 (2014-09-30), 3053 (2014-09-12) and 2941 (2014-03-31), respectively, in its selected `Glenmark_Pharmaceuticals_GLENMARK_NS_daily.csv`. The 200-day window contains 131 daily rows. The old Glenmark 2003 anomalies cannot enter this bounded warmup.
- `V/canonical_sources.json` records 29 selected companies, separate warmup/study counts, zero source switches and only `Shanghai_Fosun_Pharma_600196_SS_daily.csv` for Fosun. The intended thirtieth company, Rovi, remains excluded for absent daily data. One-file selection does not itself prove listing identity or adjustment correctness.
- `V/candidate_target_panel.csv` contains 1,305 diagnostic candidates: 783 train, 203 validation, 261 test and 58 purged. The 1,247 retained candidates run from 2015-03-31 through 2026-03-31, with latest complete target quarter 2026-06-30. They are price-validation candidates, not a completed accounting-feature dataset or fitted model observations.
- `V/validation_gate.json` confirms zero pre-study observations and zero fitted models. Exposure checks explicitly exclude purged rows. `V/source_integrity_check.json` confirms all 29 selected sources had identical hashes before and after the run.

### Findings from the new files

`V/price_flags.csv` logs 222 diagnostic source rows: 214 unchanged zero-volume flat-OHLC rows, six severe moves, one changed zero-volume flat row and one invalid price. The additional 48 warmup flags are all unchanged zero-volume flat rows; no additional severe jump was detected in the included warmup. These are screening findings, not proof of data error or universal validity.

`V/flag_panel_dependencies.csv` contains 736 retained-observation relationships, including 94 involving warmup dates. In addition to direct row dependencies, it conservatively identifies target and return intervals containing a flagged event. An unchanged flat row inside such an interval does not by itself imply a contaminated return; these interval entries are explicitly review candidates. The larger relationship count reflects both warmup inclusion and the expanded interval tracing. `V/recorded_actions.csv` records the supplied split/dividend fields; absent action fields cannot exclude a demerger.

### Blocking evidence rechecked against original CSVs

The full source-directory definitions **S**, **A** and **B** and the source-value table remain in the historical evidence below. They were reread for this checkpoint. Source A line 5576 (2024-12-05) has adjusted price 1471.4779052734375; line 5577 (2024-12-06) has 676.3120727539062, a 54.0386% fall with zero supplied dividend/split fields. Source B lines 2560 and 2561 instead have 672.75 and 676.31. This disagreement exists in the original inputs; the validator did not introduce or repair it.

For the retained 2024-09-30 Strides test observation, A lines 5531 and 5593 imply next-quarter return -0.528663333235587 and target 0. B lines 2515 and 2577 imply +0.03094231254733655 and target 1. The newly generated A-based candidate is `V/candidate_target_panel.csv:445`; the severe-event record is `V/price_flags.csv:70`. B was inspected only for provenance and was never substituted.

The new dependency evidence is exact:

| V/flag_panel_dependencies.csv line | Retained test observation | Exposure to 2024-12-06 |
|---|---|---|
| 147 | 2024-09-30 | Next-quarter target interval crosses the unresolved basis event. |
| 148 | 2024-12-31 | 50/200-day means, 60/120-day volatility, 60-day volume row; 91/182/365-day return intervals. |
| 149 | 2025-03-31 | 200-day mean, 120-day volatility; 182/365-day return intervals. |
| 150 | 2025-06-30 | 365-day return interval. |
| 151 | 2025-09-30 | 365-day return interval. |

These are dependencies and unresolved basis exposures, not counterfactual recomputed feature values. The documented corporate action explains a structural event but does not establish either supplied series' adjustment basis. The retained target disagreement is sufficient to stop training. The other severe moves, unchanged-flat-row convention and Sanofi identity review described below remain un-cleared; adding warmup does not resolve them. Baxter's August 2026 invalid row remains outside retained target/feature exposure.

### Exact minimal next action

Obtain source-backed verification of a consistent Strides price basis across the December 2024 demerger, or an explicit, source-verified parent-security price-only definition excluding the distribution, as detailed below. Do not pick a series for its target sign, drop the affected observations, or invent an adjustment factor. Complete the remaining source-review items before any later clearance. Stop here: no fitting, retuning, feature repair, final report or ZIP production is authorised by this checkpoint result.

## Historical checkpoint evidence (preserved; superseded scope/counts)

**Status: BLOCKED BEFORE TRAINING.** No models were fitted and no final report or Overleaf ZIP was generated. The user explicitly required a stop if an unresolved anomaly affects the proposed 2015â€“2026 panel. That condition is met by Strides Pharma Science's conflicting corporate-action price bases.

## Scope and completed check

A new validator and its evidence are in `thesis_output/reproduction_clean_2015_2026/`. All paths below are relative to `C:\Users\yuktha\Downloads\research project(4)\`.

The scan reads one named source file for each of 29 represented companies in the supplied `thesis_output/reproduction/friend_package/research project/YUKTHA_CLEAN_2026-09-07/` tree. The intended universe remains 30; Rovi has no selected daily CSV. It does not read old model outputs as empirical evidence. Fosun uses only the `600196.SS` ticker-named CSV. There are zero source switches by construction and no duplicate selected dates were encountered. Single-file selection alone does not certify upstream listing identity or price adjustment integrity.

The study starts 2015-01-01 with no earlier price warm-up. The latest complete target quarter supported is **2026 Q2**, ending 2026-06-30; the last candidate observation is 2026-03-31. Diagnostic counts are 783 training, 203 validation and 261 test observations, plus 58 purged boundary observations: 1,305 before purge and 1,247 retained candidates. These are candidate price/target counts, not a completed accounting/model dataset.

The scan flags absolute daily moves of at least 30%, invalid prices, and zero-volume flat-OHLC records. It identifies 174 source rows: 166 unchanged zero-volume flat rows, six severe moves, one small changed zero-volume flat row and one invalid-price row. These flags are not 174 proven errors. Raw paths and line numbers appear in `price_flags.csv`; `recorded_actions.csv` preserves the supplied action evidence; `flag_panel_dependencies.csv` contains 448 candidate relationships. All 29 selected source hashes were unchanged after inspection.

## 1. Blocking Strides price-basis conflict

Define the exact local company directory **S** as:

`thesis_output/reproduction/friend_package/research project/YUKTHA_CLEAN_2026-09-07/01_INDIAN_COMPANIES/Strides_Pharma_Science/`

The provisional canonical source preserves the supplied adjusted supplement, without stitching:

**A:** `S/04_OTHER_SOURCE_MATERIAL/Strides_Pharma_Science_yahoo_adjusted_close_supplement.csv`

The conflicting comparison source, inspected but never substituted, is:

**B:** `S/02_MARKET_DATA/Daily/Strides_Pharma_Science_daily.csv`

| Date | A: CSV line / Adj_Close | B: CSV line / Close |
|---|---|---|
| 2024-09-30 | 5531 / 1386.2142333984375 | 2515 / 633.76 |
| 2024-12-05 | 5576 / 1471.4779052734375 | 2560 / 672.75 |
| 2024-12-06 | 5577 / 676.3120727539062 | 2561 / 676.31 |
| 2024-12-31 | 5593 / 653.3735961914062 | 2577 / 653.37 |

A drops **54.0386%** on 6 December. Its `Dividends` and `Stock Splits` fields both read zero on that date; that does not mean no other kind of corporate action occurred. The ticker-named input `S/02_MARKET_DATA/Daily/Strides_Pharma_Science_STAR_NS_daily.csv:5576â€“5577` contains the same large discontinuity, with adjusted values approximately 1471.477905 and 676.312012. Thus it is not introduced by the new validator. B explicitly identifies `STAR.NS`, but has a different pre-event price level and nearly the same post-event level. Its adjustment methodology is not established merely by the `Close` column name.

**The corporate action is supported; the applicable price basis remains unresolved.** Strides' issuer filing dated 11 December 2024 identifies the 6 December record date and allotment of one OneSource share for every two Strides shares. This is a primary-source explanation for a structural event, not validation of either supplied historical adjustment series. [Strides issuer filing, page 1](https://www.strides.com/Upload/PDF/strides-se-intimation-allotment-12dec2024.pdf).

No OneSource security was merged into Strides, and no prices were changed. Neither selecting the series with the smoother chart nor selecting the one with a preferable label is a defensible resolution.

### A retained test target changes direction

For the candidate Strides observation **2024-09-30**, outcome **2024-12-31**:

- A implies `653.3735961914062 / 1386.2142333984375 - 1 = -0.5286633332`, **non-up (0)**.
- B implies `653.37 / 633.76 - 1 = +0.0309423125`, **up (1)**.

The A-based diagnostic row is `thesis_output/reproduction_clean_2015_2026/candidate_target_panel.csv:445`. This is an actual disagreement in the requested target, not just a large intraday move. The alternative calculation was done for provenance comparison only; B was not used to replace the candidate data.

### Retained feature exposure

`flag_panel_dependencies.csv`, company `Strides_Pharma_Science`, event `2024-12-06`, records:

| Candidate observation | Split | Direct event-date exposure |
|---|---|---|
| 2024-09-30 | Test | Event lies inside the next-quarter target interval. |
| 2024-12-31 | Test | 50/200-day price means; 60/120-day volatility; the row's volume enters the 60-day volume window. |
| 2025-03-31 | Test | 200-day price mean and 120-day volatility. |

The event is not itself a quarter-end price endpoint. The target problem comes from endpoints on opposite sides of the unresolved basis change. A persistent adjustment difference also affects longer return lookbacks and other means spanning the two regimes; the table is an event-date dependency map, not a claim that only these cells could change under a justified source revision. No counterfactual feature matrix or model was fitted.

### Minimal missing data decision

**Establish and document the canonical Strides price basis across the 6 December 2024 demerger before fitting.** The minimum is either:

1. A source-backed, consistently corporate-action-adjusted `STAR.NS` series, with adjustment provenance explaining the pre/post-event values; or
2. An explicit methodological decision to predict the parent security's price-only direction excluding the distributed OneSource value, accompanied by verification that the chosen supplied series consistently represents that basis.

This must be a source/economic-definition decision, not permission to choose the desired target sign. A split/share-entitlement ratio by itself is not a valid price-adjustment factor. Do not silently swap to B, back-adjust A, remove Strides or omit the affected quarter. Those actions have not been authorised. An approved basis must be applied consistently to feature and target construction and the validation gate rerun before training.

## 2. Other review findings, distinguished from the blocker

- **Glenmark's 2003 spikes are outside this design.** No pre-2015 prices are used, so those specific records cannot enter these candidate targets or feature windows.
- **Fosun listing mixing is prevented in the new candidate construction.** `canonical_sources.json` selects only `Shanghai_Fosun_Pharma_600196_SS_daily.csv`. No `2196.HK` prices fill missing dates. This resolves the previously identified construction mechanism, not every possible source-quality issue.
- **Zhejiang Hisun, 2020-07-15, has a recorded dividend.** Its selected file `.../02_NON_INDIAN_COMPANIES/Zhejiang_Hisun_Pharma/02_MARKET_DATA/Daily/Zhejiang_Hisun_Pharma_600267_SS_daily.csv:4953` has volume 0, flat OHLC and dividend 0.05. The adjusted-price change is about +0.3201%. This is action-associated, not an unexplained severe integer-scale jump. It remains logged without removal.
- **Baxter's invalid record is outside the retained panel.** `.../02_NON_INDIAN_COMPANIES/Baxter_International/02_MARKET_DATA/Daily/Baxter_International_BAX_daily.csv:11301`, 2026-08-28, has missing OHLC/adjusted price. It is flagged and not treated as a zero price. Since the latest complete outcome is June 2026, it has no retained target/feature dependency. It is not a reason to remove a retained observation.
- **The five other severe flags require interpretation, not automatic deletion:** Biogen on 2020-11-04 (+43.97%), 2021-06-07 (+38.34%) and 2022-09-28 (+39.85%); Formycon on 2020-12-09 (+36.90%) and 2025-02-17 (-34.54%). Exact paths/lines and affected candidates are in the diagnostic CSVs. Large news-driven moves can be genuine; this check does not declare these data errors because they exceed a threshold. Detailed clearance remains pending because the Strides gate already prevents training.
- **Unchanged zero-volume flat rows remain present and visible.** They may represent non-trading/suspension/carry-forward conventions, not price-scale errors. No rows were silently dropped. Their treatment as daily observations still needs a documented convention before the complete dataset is cleared.
- **Sanofi identity metadata requires confirmation.** The provisionally selected `.../02_NON_INDIAN_COMPANIES/Sanofi/02_MARKET_DATA/Daily/Sanofi_daily.csv` is the inherited Paris-series choice, but its header/rows identify `Ticker=SNY`, `Country=France`. A country label alone does not establish exchange or currency. `canonical_sources.json` explicitly marks this description as requiring review; one-file selection is not being misrepresented as verified security identity. The supplied source mapping must establish which listing/currency it represents before final clearance.

The missing Rovi series remains an explicit sample limitation, not a fabricated thirtieth company. Neither the source-quality flags nor this blocked status establishes that the remaining market data are universally valid.

## 3. Work intentionally not performed

No financial feature rebuild, publication-date/YTD conversion, training-only transformations, eight-model fitting, held-out predictions, metrics, model selection, final figures, report source, compilation or ZIP generation has occurred in this new run. The candidate CSV is only a validation aid. Prior reproduction results have not been copied into a new report.

The next action is the Strides basis decision and source verification above, together with the remaining source-identity/flag clearance. The report stage must remain pending until that prerequisite passes.

