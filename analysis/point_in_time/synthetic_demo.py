"""Create DETERMINISTIC SYNTHETIC test fixtures (never use as thesis results)."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd


def generate(out:Path,companies=5,periods=16,seed=20261012):
    if companies<2 or periods<10:
        raise ValueError("Need >=2 firms and >=10 periods")
    rng=np.random.default_rng(seed)
    dates=pd.date_range("2017-01-01",periods=periods,freq="QS",tz="UTC")
    features=[];targets=[]
    for q,asof in enumerate(dates):
        for idx in range(companies):
            firm=f"SYNTHETIC_{idx:02d}"
            momentum=float(rng.normal(0,0.2))
            leverage=float(np.clip(rng.normal(0.4,0.15),0,1))
            raw_signal=0.7*momentum-0.4*leverage+float(rng.normal(0,0.3))
            target=int(raw_signal>0)
            targets.append({
                "company":firm,"prediction_asof":asof.isoformat(),
                "target_end":(asof+pd.DateOffset(months=3)).isoformat(),
                "label_available_at":(asof+pd.DateOffset(months=3,days=7)).isoformat(),
                "target_label":target,
            })
            for feature,value in [("momentum",momentum),("leverage",leverage)]:
                features.append({
                    "company":firm,"prediction_asof":asof.isoformat(),
                    "feature":feature,"value":value,
                    "published_at":(asof-pd.Timedelta(days=2)).isoformat(),
                    "source_id":f"SYNTHETIC:{seed}:{q}:{idx}:{feature}"
                })
    out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(features).to_csv(out/"synthetic_features.csv",index=False)
    pd.DataFrame(targets).to_csv(out/"synthetic_labels.csv",index=False)
    (out/"NOT_REAL_DATA.txt").write_text(
        "All rows are simulated; not observed financial statements or market prices. "
        "Do not report sample statistics as thesis findings.\n",encoding="utf-8")
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    generate(args.out)
    print("Synthetic-only fixture written to",args.out)


if __name__=="__main__": main()
