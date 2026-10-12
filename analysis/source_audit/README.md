# Private Thesis Source-Archive Audit

**Purpose:** Recover which original stock/financial inputs might support the pharmaceutical company-quarter dataset, without inventing financial statement release dates or silently using later revisions.

The report is only an *inventory and schema audit*. It **does not** mean a real-data thesis ML experiment has been executed or that the preliminary 3,375-row / 29-firm / 16-predictor panel is verified.

## What it actually does

1. Opens the September organized master-data ZIP (and, if requested, work archives) read-only, **without extracting files to disk**.
2. Inventories the number and type of files, including nested ZIPs up to the configured depth.
3. Examines up to 256 KiB from individual CSV/TSV/JSON files, and up to 16 MiB from each XLSX/XLSM workbook; records **column names and sheet names**, not financial values.
4. Ranks candidate company-quarter, labelled-panel and point-in-time-schema files by observed header names.
5. Highlights absence of an explicit public release date, target availability date or security identifier.
6. Writes a **private JSON metadata report**. No underlying licensed market data are uploaded or committed.

**The phrase "candidate_point_in_time_panel_schema_only" does not mean the observed dates are correct.** Fiscal period-end != date when the market could first know the financial numbers.

## Windows PowerShell (already have master ZIP in Downloads)

From your desired working directory:

~~~powershell
git clone https://github.com/yuktha-code/pharma-stock-prediction.git
Set-Location pharma-stock-prediction
py -3 -m pip install "openpyxl>=3.1,<4"

$source = "$env:USERPROFILE\Downloads\YUKTHA_FINAL_MASTER_DATA_2026-09-02_ORGANIZED.zip"
$out = "$env:USERPROFILE\Downloads\thesis_master_private_audit.json"
py -3 -m analysis.source_audit.scan --archive $source --out $out --max-depth 1

# This displays the top 15 candidate file locations only (no financial rows).
$report = Get-Content $out -Raw | ConvertFrom-Json
$report.priority_candidates | Select-Object -First 15 path, classification, score
~~~

If your ZIP is in a different directory, replace \`$source\` with the exact path. Run the auditor separately for \`THESIS_WORK_ARCHIVE_A.zip\`, \`B.zip\`, \`C.zip\`, and the October handoff ZIP if you have them.

The scanner defaults to 25,000 ZIP entries, one nested archive level, 32 MiB max per nested ZIP, and 16 MiB max per workbook. Large files, Parquet sources or deeply nested archives may be skipped and **must be reported as uninspected**; do not interpret their absence from candidates as proof the data are unavailable.

## Testing

~~~powershell
py -3 -m unittest discover -s analysis/source_audit/tests -p "test_*.py" -v
~~~

Tests use synthetic ZIP and workbook fixtures. GitHub CI **does not have your master dataset** and cannot validate source provenance.

## After running the report

The most useful items to share privately are: the report's \`by_extension\`, \`classifications\`, \`warnings\`, and the first 20 \`priority_candidates\` headers/paths. **Review filenames for confidential identifiers before sharing.** Do not upload raw licensed S&P/Bloomberg data to GitHub or public conversations.

Then:
- inspect high-ranking original panels and vendor exports;
- reconcile all company IDs, reporting availability, and share/split adjustments;
- build the separate feature and label ledgers expected by [point-in-time analysis](../point_in_time/README.md);
- run genuine chronological baselines with source-manifest evidence;
- mark the empirical results only after they are independently reproducible.

## Limitations of schema-only inspection

An archive may contain accounting balances for many companies but still lack **public filing release timestamps**, total-return-adjusted stock prices or non-surviving firms. Such an archive is valuable for reconstruction, but it does not by itself justify an actual market-predictive result.

The code does not guess release dates, manufacture stock returns, download private data, or claim model accuracy. It also does not assume a name/date column means it is an eligible firm-quarter training panel.
