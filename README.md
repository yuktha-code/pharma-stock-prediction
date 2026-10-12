# Pharmaceutical Stock Direction Prediction

A company-quarter machine-learning study of next-quarter stock-price direction in Indian and non-Indian pharmaceutical companies.

## Contents

- `paper/` - Overleaf source, figures, tables and current paper PDF
- `analysis/` - selected reconstruction and verification scripts

## Status

This repository contains the current preliminary research outputs. The reported model results are not final verified empirical findings because a corporate-action adjustment issue in the `STAR.NS` series requires source standardisation before the complete final rerun.

## New research-methodology extension (not an empirical result)

A [point-in-time financial ML and walk-forward baseline framework](analysis/point_in_time/README.md) has been implemented and CI-tested to validate feature publication timestamps, training-label availability, rolling/expanding chronological folds, and train-only transformations. It has deterministic **synthetic-only** CI checks. It has **not** been run on a fully verified version of the original firm-quarter dataset and does **not** supersede the preliminary findings or fix the outstanding `STAR.NS` corporate-action issue. See [data requirements](analysis/point_in_time/DATA_CONTRACT.md).
