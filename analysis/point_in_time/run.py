"""Run walk-forward baselines only on source-verified user-provided ledgers."""
import argparse
import hashlib
import json
from pathlib import Path

from .availability import load_ledgers, PointInTimeError
from .walkforward import evaluate_walk_forward, walk_forward_folds


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--features",type=Path,required=True,help="Feature ledger with actual public-availability timestamps")
    ap.add_argument("--labels",type=Path,required=True,help="Outcome ledger with verifiable label-availability timestamps")
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--min-history",type=int,default=6)
    ap.add_argument("--test-periods",type=int,default=1)
    ap.add_argument("--gap-periods",type=int,default=0)
    ap.add_argument("--embargo-days",type=int,default=0)
    ap.add_argument("--max-history",type=int,default=None)
    ap.add_argument("--allow-star-after-verification",action="store_true",
                    help="Only use after separately verifying STAR.NS corporate-action adjustments and data provenance")
    args=ap.parse_args(argv)
    if not args.features.is_file() or not args.labels.is_file():
        ap.error("Input CSV file missing. You must supply original panel data, not fabricated placeholders")
    blocklist=() if args.allow_star_after_verification else ("STAR.NS",)
    panel=load_ledgers(str(args.features),str(args.labels),blocked_companies=blocklist)
    folds=walk_forward_folds(panel,min_history_periods=args.min_history,
                            test_periods=args.test_periods,gap_periods=args.gap_periods,
                            embargo_days=args.embargo_days,max_history_periods=args.max_history)
    if not folds:
        raise RuntimeError("No eligible walk-forward folds: inspect label dates, history and embargo")
    metrics,predictions=evaluate_walk_forward(panel,folds=folds)
    if metrics.empty or predictions.empty:
        raise RuntimeError("Insufficient class variation or data to fit baselines")
    args.out.mkdir(parents=True,exist_ok=True)
    metrics.to_csv(args.out/"fold_metrics.csv",index=False)
    predictions.to_csv(args.out/"predictions.csv",index=False)
    run_metadata={
        "status":"empirical_run_requires_data_source_independent_verification",
        "features_path":str(args.features),
        "features_sha256":sha256(args.features),
        "labels_path":str(args.labels),
        "labels_sha256":sha256(args.labels),
        "unique_companies":int(panel["company"].nunique()),
        "observations":len(panel),
        "asof_periods":int(panel["prediction_asof"].nunique()),
        "feature_columns":sorted(set(panel.columns)-{
            "company","prediction_asof","target_end","label_available_at","target_label"
        }),
        "fold_count":len(folds),
        "min_history":args.min_history,
        "test_periods":args.test_periods,
        "gap_periods":args.gap_periods,
        "embargo_days":args.embargo_days,
        "max_history":args.max_history,
        "star_unblocked_by_user":bool(args.allow_star_after_verification),
        "not_a_profitability_or_live_trading_claim":True,
    }
    (args.out/"run_manifest.json").write_text(json.dumps(run_metadata,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"observations":len(panel),"folds":len(folds),
                      "metrics_rows":len(metrics),"prediction_rows":len(predictions),
                      "output":str(args.out)},indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
