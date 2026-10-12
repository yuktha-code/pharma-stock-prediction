"""Leakage-aware walk-forward splits and out-of-sample model benchmarks.

The evaluation is a *research framework*. It makes no claim of empirical
trading performance until a documented genuine panel is provided and run.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, roc_auc_score

REQUIRED = {"company", "prediction_asof", "target_end", "label_available_at", "target_label"}
NON_FEATURE = REQUIRED | {"fold", "source_id", "published_at"}


class SplitError(ValueError):
    pass


@dataclass(frozen=True)
class WalkForwardFold:
    fold_number: int
    train_indices: np.ndarray
    test_indices: np.ndarray
    cutoff: pd.Timestamp
    test_start: pd.Timestamp


def walk_forward_folds(
    panel: pd.DataFrame, *,
    min_history_periods: int = 6,
    test_periods: int = 1,
    step_periods: int = 1,
    gap_periods: int = 0,
    embargo_days: int = 0,
    max_history_periods: int | None = None,
) -> list[WalkForwardFold]:
    """Group by quarter-as-of and restrict training labels to those publicly known.

    In fold k, fit at test_start - embargo_days. An observation may enter
    training only if BOTH its prediction period belongs to the permitted
    past window AND label_available_at <= that fit time.

    gap_periods excludes entire as-of cohorts before the test cohort.
    max_history_periods implements rolling instead of expanding windows.
    """
    if any(not isinstance(x, int) or x < 0 for x in
           (min_history_periods, test_periods, step_periods, gap_periods, embargo_days)):
        raise SplitError("Split counts and embargo must be nonnegative integers")
    if min_history_periods < 2 or test_periods < 1 or step_periods < 1:
        raise SplitError("Need >=2 history cohorts and positive test/step periods")
    if max_history_periods is not None and (not isinstance(max_history_periods, int)
                                            or max_history_periods < min_history_periods):
        raise SplitError("Rolling history cannot be shorter than required history")
    missing = REQUIRED - set(panel.columns)
    if missing:
        raise SplitError(f"Panel missing {sorted(missing)}")
    p = panel.copy()
    for x in ("prediction_asof", "target_end", "label_available_at"):
        p[x] = pd.to_datetime(p[x], utc=True, errors="raise")
        if p[x].isna().any():
            raise SplitError(f"Null timestamp in {x}")
    if (p["target_end"] <= p["prediction_asof"]).any():
        raise SplitError("Invalid outcome horizon")
    if (p["label_available_at"] < p["target_end"]).any():
        raise SplitError("Impossible early label availability")
    periods = sorted(p["prediction_asof"].unique())
    folds = []
    start = min_history_periods + gap_periods
    for k in range(start, len(periods) - test_periods + 1, step_periods):
        permitted_end = k - gap_periods
        history_periods = periods[:permitted_end]
        if max_history_periods is not None:
            history_periods = history_periods[-max_history_periods:]
        test_times = periods[k:k+test_periods]
        test_start = pd.Timestamp(test_times[0])
        fit_cutoff = test_start - pd.Timedelta(days=embargo_days)
        train_mask = p["prediction_asof"].isin(history_periods) & (p["label_available_at"] <= fit_cutoff)
        test_mask = p["prediction_asof"].isin(test_times)
        train_ids = np.flatnonzero(train_mask.to_numpy())
        test_ids = np.flatnonzero(test_mask.to_numpy())
        if len(test_ids) and len(train_ids) and p.loc[train_ids, "prediction_asof"].nunique() >= min_history_periods:
            folds.append(WalkForwardFold(len(folds)+1,train_ids,test_ids,fit_cutoff,test_start))
    return folds


def score_predictions(y_true, positive_prob: np.ndarray) -> dict[str,float | None]:
    y = np.asarray(y_true, dtype=int)
    prob = np.asarray(positive_prob, dtype=float)
    if not len(y) or y.shape != prob.shape or not np.all(np.isfinite(prob)) or np.any((prob < 0) | (prob > 1)):
        raise ValueError("Invalid probability array")
    pred = (prob >= 0.5).astype(int)
    out = {
        "accuracy": float(accuracy_score(y,pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y,pred)),
        "brier": float(brier_score_loss(y,prob)),
        "auc": None,
    }
    if len(np.unique(y)) == 2:
        out["auc"] = float(roc_auc_score(y,prob))
    return out


def evaluate_walk_forward(
    panel: pd.DataFrame, *,
    folds: list[WalkForwardFold] | None = None,
    min_history_periods: int = 6,
    gap_periods: int = 0,
    embargo_days: int = 0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Train-only imputation/scaling; majority-class and logistic baselines.

    Returns metrics + point-in-time test predictions. No trained model uses
    test labels, later observations or future preprocessing statistics.
    """
    missing = REQUIRED - set(panel.columns)
    if missing:
        raise SplitError(f"Missing required columns: {sorted(missing)}")
    cols = sorted(set(panel.select_dtypes(include=["number"]).columns) - NON_FEATURE)
    if "target_label" in cols:
        cols.remove("target_label")
    if not cols:
        raise SplitError("No numeric predictors available")
    p=panel.reset_index(drop=True)
    if folds is None:
        folds=walk_forward_folds(
            p, min_history_periods=min_history_periods,
            gap_periods=gap_periods, embargo_days=embargo_days
        )
    metrics=[];predictions=[]
    for fold in folds:
        train=p.iloc[fold.train_indices]
        test=p.iloc[fold.test_indices]
        if len(train) < 3 or not len(test):
            continue
        if (train["label_available_at"] > fold.cutoff).any():
            raise SplitError("Fold contains labels unavailable at fit time")
        if (train["prediction_asof"] >= fold.test_start).any():
            raise SplitError("Fold leaked future predictions")
        xtr=train[cols];xte=test[cols]
        # If an entire predictor is absent in training, it cannot be
        # estimated from the test set: remove it for this fold.
        active=[c for c in cols if xtr[c].notna().any()]
        if not active:
            raise SplitError("No observed training features in fold")
        ytr=train["target_label"].astype(int).to_numpy()
        yte=test["target_label"].astype(int).to_numpy()
        models={"majority": DummyClassifier(strategy="prior")}
        if len(np.unique(ytr)) >= 2:
            models["logistic_l2"] = Pipeline([
                ("imputer",SimpleImputer(strategy="median")),
                ("scaler",StandardScaler()),
                ("clf",LogisticRegression(max_iter=1000,random_state=0))
            ])
        for name,estimator in models.items():
            estimator.fit(xtr[active],ytr)
            model_classes=estimator.classes_ if name=="majority" else estimator.named_steps["clf"].classes_
            raw_probs=estimator.predict_proba(xte[active])
            pos=np.where(model_classes == 1)[0]
            prob=raw_probs[:,pos[0]] if len(pos) else np.zeros(len(test))
            scores=score_predictions(yte,prob)
            metrics.append({
                "fold":fold.fold_number,"model":name,
                "fit_cutoff":fold.cutoff.isoformat(),"test_start":fold.test_start.isoformat(),
                "train_n":len(train),"test_n":len(test),**scores
            })
            for company,asof,true,pp in zip(test["company"],test["prediction_asof"],yte,prob):
                predictions.append({
                    "fold":fold.fold_number,"model":name,"company":company,
                    "prediction_asof":pd.Timestamp(asof).isoformat(),
                    "label":int(true),"prob_up":float(pp)
                })
    return pd.DataFrame(metrics),pd.DataFrame(predictions)
