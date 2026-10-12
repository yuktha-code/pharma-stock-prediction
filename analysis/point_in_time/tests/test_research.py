"""Offline point-in-time leakage and walk-forward tests on synthetic fixtures.

No thesis data or empirical performance claims are created in these tests.
"""
import unittest
import numpy as np
import pandas as pd
from analysis.point_in_time.availability import (
    PointInTimeError, build_point_in_time_panel,
)
from analysis.point_in_time.walkforward import (
    SplitError, walk_forward_folds, evaluate_walk_forward, score_predictions,
)


def synthetic_ledgers(n_periods=16, n_companies=4):
    periods = pd.date_range("2018-01-01", periods=n_periods, freq="QS", tz="UTC")
    feats = []
    labels = []
    for k, timestamp in enumerate(periods):
        for i in range(n_companies):
            company = f"FIRM{i}"
            label = int((i + k * 3 + k // 4) % 3 != 0)
            labels.append({
                "company":company,"prediction_asof":timestamp,
                "target_end":timestamp + pd.DateOffset(months=3),
                "label_available_at":timestamp + pd.DateOffset(months=3,days=7),
                "target_label":label,
            })
            for feature, val in {
                "momentum": ((i*7+k)%11)/10.,
                "leverage": (i+k%3)/7.,
                "return_lag": (i-k)/17.
            }.items():
                feats.append({
                    "company":company,"prediction_asof":timestamp,
                    "feature":feature,"value":float(val),
                    "published_at":timestamp - pd.Timedelta(days=2),
                    "source_id":f"document:{i}:{k}:{feature}",
                })
    return pd.DataFrame(feats),pd.DataFrame(labels)


class AvailabilityTests(unittest.TestCase):
    def setUp(self):
        self.f,self.y=synthetic_ledgers()

    def test_successful_join(self):
        p=build_point_in_time_panel(self.f,self.y)
        self.assertEqual(len(p),len(self.y))
        self.assertEqual(p["company"].nunique(),4)
        self.assertIn("leverage",p.columns)
        self.assertNotIn("source_id",p.columns)

    def test_future_published_feature_is_rejected(self):
        f=self.f.copy()
        f.loc[0,"published_at"]=f.loc[0,"prediction_asof"] + pd.Timedelta(days=4)
        with self.assertRaisesRegex(PointInTimeError,"Look-ahead"):build_point_in_time_panel(f,self.y)

    def test_duplicate_feature_rejected(self):
        with self.assertRaisesRegex(PointInTimeError,"Duplicate"):build_point_in_time_panel(pd.concat([self.f,self.f.iloc[[0]]]),self.y)

    def test_duplicate_targets_rejected(self):
        with self.assertRaisesRegex(PointInTimeError,"Duplicate"):build_point_in_time_panel(self.f,pd.concat([self.y,self.y.iloc[[0]]]))

    def test_unmatched_company_quarter_rejected(self):
        with self.assertRaisesRegex(PointInTimeError,"Unmatched"):build_point_in_time_panel(self.f,self.y.iloc[1:])

    def test_label_not_available_before_target_end(self):
        y=self.y.copy()
        y.loc[0,"label_available_at"]=y.loc[0,"prediction_asof"]
        with self.assertRaisesRegex(PointInTimeError,"Outcome cannot"):build_point_in_time_panel(self.f,y)

    def test_blocked_corporate_action_company(self):
        f=self.f.copy();y=self.y.copy()
        f.loc[f.company=="FIRM0","company"]="STAR.NS"
        y.loc[y.company=="FIRM0","company"]="STAR.NS"
        with self.assertRaisesRegex(PointInTimeError,"unresolved"):build_point_in_time_panel(f,y)

    def test_nonfinite_input_rejected(self):
        f=self.f.copy();f.loc[0,"value"]=np.nan
        with self.assertRaisesRegex(PointInTimeError,"finite"):build_point_in_time_panel(f,self.y)

    def test_missing_source_id_rejected(self):
        f=self.f.copy();f.loc[0,"source_id"]=""
        with self.assertRaisesRegex(PointInTimeError,"source_id"):build_point_in_time_panel(f,self.y)

    def test_future_outcome_horizon_required(self):
        y=self.y.copy();y.loc[0,"target_end"]=y.loc[0,"prediction_asof"]
        with self.assertRaisesRegex(PointInTimeError,"strictly after"):build_point_in_time_panel(self.f,y)


class WalkForwardTests(unittest.TestCase):
    def setUp(self):
        f,y=synthetic_ledgers()
        self.panel=build_point_in_time_panel(f,y)

    def test_trains_only_on_past_available_labels(self):
        folds=walk_forward_folds(self.panel,min_history_periods=4)
        self.assertGreaterEqual(len(folds),7)
        for fold in folds:
            training=self.panel.iloc[fold.train_indices]
            test=self.panel.iloc[fold.test_indices]
            self.assertLess(training["prediction_asof"].max(),fold.test_start)
            self.assertLessEqual(training["label_available_at"].max(),fold.cutoff)
            self.assertGreaterEqual(test["prediction_asof"].min(),fold.test_start)
            self.assertTrue(set(fold.train_indices).isdisjoint(set(fold.test_indices)))

    def test_embargo_strips_late_labels(self):
        folds=walk_forward_folds(self.panel,min_history_periods=4,embargo_days=30)
        self.assertTrue(all(
            (self.panel.iloc[fold.train_indices]["label_available_at"]<=fold.cutoff).all()
            for fold in folds
        ))

    def test_gap_periods_excludes_most_recent_cohort(self):
        folds=walk_forward_folds(self.panel,min_history_periods=3,gap_periods=2)
        for fold in folds:
            past_dates=sorted(self.panel.loc[self.panel.prediction_asof<fold.test_start,"prediction_asof"].unique())
            gap_dates=set(past_dates[-2:])
            assert not set(self.panel.iloc[fold.train_indices]["prediction_asof"]).intersection(gap_dates)

    def test_fit_only_training_baselines(self):
        m,p=evaluate_walk_forward(self.panel,min_history_periods=4)
        self.assertFalse(m.empty)
        self.assertFalse(p.empty)
        self.assertTrue(set(m["model"])=={"majority","logistic_l2"})
        self.assertTrue(p["prob_up"].between(0,1).all())
        self.assertTrue(m["brier"].between(0,1).all())
        self.assertTrue(m["auc"].dropna().between(0,1).all())

    def test_probability_validation(self):
        with self.assertRaises(ValueError):score_predictions([0,1],[0.1,1.2])

    def test_single_class_auc_is_undefined(self):
        s=score_predictions([1,1,1],[0.5,0.6,0.9])
        self.assertIsNone(s["auc"])

    def test_invalid_split_parameters_rejected(self):
        with self.assertRaises(SplitError):walk_forward_folds(self.panel,min_history_periods=1)
        with self.assertRaises(SplitError):walk_forward_folds(self.panel,min_history_periods=4,step_periods=0)


if __name__ == "__main__":
    unittest.main()
