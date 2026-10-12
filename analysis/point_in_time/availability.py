"""Strict point-in-time alignment for financial ML research.

Input source facts are externally supplied; this module does NOT prove that
filing dates, stock adjustments, or vendor revisions are correct.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

FEATURE_COLUMNS = {"company", "prediction_asof", "feature", "value", "published_at", "source_id"}
TARGET_COLUMNS = {"company", "prediction_asof", "target_end", "label_available_at", "target_label"}
KEY = ["company", "prediction_asof"]
RESERVED_FEATURES = {"target_label", "target_end", "label_available_at", "prediction_asof", "company"}


class PointInTimeError(ValueError):
    pass


def _require(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise PointInTimeError(f"{name} missing required columns: {missing}")


def _dates(df: pd.DataFrame, names: tuple[str, ...], kind: str) -> pd.DataFrame:
    result = df.copy()
    for name in names:
        try:
            result[name] = pd.to_datetime(result[name], errors="raise", utc=True)
        except (ValueError, TypeError) as exc:
            raise PointInTimeError(f"{kind}: invalid timestamp in {name}") from exc
        if result[name].isna().any():
            raise PointInTimeError(f"{kind}: null timestamps in {name}")
    return result


def build_point_in_time_panel(
    features: pd.DataFrame,
    labels: pd.DataFrame,
    *,
    blocked_companies: tuple[str, ...] = ("STAR.NS",),
) -> pd.DataFrame:
    """Join feature-ledger entries only if each was published by prediction time.

    Explicit feature ledger:
      company,prediction_asof,feature,value,published_at,source_id

    Explicit outcome ledger:
      company,prediction_asof,target_end,label_available_at,target_label

    'source_id' should identify the actual filing/price-source snapshot. Supply
    raw public-release dates, not fiscal-period labels masquerading as dates.
    """
    _require(features, FEATURE_COLUMNS, "features")
    _require(labels, TARGET_COLUMNS, "labels")
    if features.empty or labels.empty:
        raise PointInTimeError("Feature and outcome ledgers must not be empty")
    f = _dates(features, ("prediction_asof", "published_at"), "features")
    y = _dates(labels, ("prediction_asof", "target_end", "label_available_at"), "labels")
    for df, kind in [(f, "features"), (y, "labels")]:
        if df["company"].isna().any() or df["company"].astype(str).str.strip().eq("").any():
            raise PointInTimeError(f"{kind}: empty company keys")
        if df["company"].isin(blocked_companies).any():
            bad = sorted(df.loc[df["company"].isin(blocked_companies), "company"].unique())
            raise PointInTimeError(
                f"Corporate-action/source validation unresolved for {bad}; "
                "remove those rows, or explicitly override only after reconciliation."
            )
    if f["feature"].isna().any() or f["feature"].astype(str).str.strip().eq("").any():
        raise PointInTimeError("Empty feature names")
    if f["feature"].isin(RESERVED_FEATURES).any():
        raise PointInTimeError("Feature name collides with outcome or identifier column")
    if f["source_id"].isna().any() or f["source_id"].astype(str).str.strip().eq("").any():
        raise PointInTimeError("Every feature must have a nonempty provenance source_id")
    if (f["published_at"] > f["prediction_asof"]).any():
        bad = f.loc[f["published_at"] > f["prediction_asof"], KEY + ["feature"]].head(5)
        raise PointInTimeError(f"Look-ahead feature publication detected: {bad.to_dict('records')}")
    if f.duplicated(KEY + ["feature"]).any():
        raise PointInTimeError("Duplicate company/as-of/feature keys; choose an explicit source snapshot")
    if y.duplicated(KEY).any():
        raise PointInTimeError("Duplicate company/as-of outcome rows")
    if (y["target_end"] <= y["prediction_asof"]).any():
        raise PointInTimeError("Outcome must end strictly after its prediction timestamp")
    if (y["label_available_at"] < y["target_end"]).any():
        raise PointInTimeError("Outcome cannot be known before the target horizon ends")
    if y["target_label"].isna().any():
        raise PointInTimeError("Missing outcome labels; do not fabricate labels")
    yy = pd.to_numeric(y["target_label"], errors="coerce")
    if yy.isna().any() or not yy.isin([0, 1]).all():
        raise PointInTimeError("Outcome labels must be binary 0/1")
    y["target_label"] = yy.astype(int)
    xx = pd.to_numeric(f["value"], errors="coerce")
    if (~np.isfinite(xx.to_numpy(dtype=float))).any():
        raise PointInTimeError("Feature values must be finite; missing data need an explicit missingness convention")
    f["value"] = xx
    # Reject silently unmatched labels or features: no implicit sample deletion.
    fk = f[KEY].drop_duplicates()
    check1 = y[KEY].merge(fk, on=KEY, how="left", indicator=True)
    check2 = fk.merge(y[KEY], on=KEY, how="left", indicator=True)
    if check1["_merge"].ne("both").any() or check2["_merge"].ne("both").any():
        raise PointInTimeError("Unmatched feature/outcome company-as-of keys")
    wide = f.pivot(index=KEY, columns="feature", values="value").reset_index()
    wide.columns.name = None
    out = y.merge(wide, on=KEY, how="inner", validate="one_to_one")
    if len(out) != len(y):
        raise PointInTimeError("Outcome/feature join changed the number of observations")
    return out.sort_values(KEY[::-1]).reset_index(drop=True)


def load_ledgers(feature_csv: str, target_csv: str, *, blocked_companies=("STAR.NS",)) -> pd.DataFrame:
    return build_point_in_time_panel(
        pd.read_csv(feature_csv), pd.read_csv(target_csv),
        blocked_companies=tuple(blocked_companies)
    )
