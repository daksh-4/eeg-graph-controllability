"""Run the preprocessing stages in order. Each stage can also be run on its own (see p01..p05).
Examples:
    python scripts/preproc/run_preproc.py --ids 1 2 3            # a few children, all stages
    python scripts/preproc/run_preproc.py --stages 3 4 5          # only some stages
    python scripts/preproc/run_preproc.py --force --stages 3 4    # redo stages 3 and 4"""
import argparse
import os

import config as cfg
import p01_load_filter, p02_bad_channels, p03_ica, p04_epoch, p05_qc_summary

STAGES = {1: p01_load_filter, 2: p02_bad_channels, 3: p03_ica, 4: p04_epoch}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids", type=int, nargs="*")
    ap.add_argument("--conds", nargs="*", default=cfg.CONDITIONS, choices=cfg.CONDITIONS)
    ap.add_argument("--stages", type=int, nargs="*", default=[1, 2, 3, 4, 5])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--n-jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    a = ap.parse_args()
    for s in sorted(a.stages):
        if s == 5:
            p05_qc_summary.main()
        else:
            STAGES[s].main(a.ids, a.conds, a.force, a.n_jobs)
