"""Shared helpers: file discovery, stage file names, per-child QC records, argument parsing, parallel runner."""
import argparse, json, os, re, warnings
from pathlib import Path

import mne
from joblib import Parallel, delayed

import config as cfg

warnings.filterwarnings("ignore")
mne.set_log_level("ERROR")


def discover(cond):
    """{child id: EDF path} for one condition."""
    out = {}
    for f in sorted((cfg.RAW_DIR / cond).glob("*.edf")):
        m = re.match(r"\s*(\d+)", f.name)
        if m:
            out[int(m.group(1))] = f
    return out


def stage_path(cond, sid, suffix):
    d = cfg.DERIV / cond
    d.mkdir(parents=True, exist_ok=True)
    return d / f"sub-{sid:03d}_{cond}_{suffix}.fif"


def qc_path(cond, sid):
    d = cfg.DERIV / "qc" / cond
    d.mkdir(parents=True, exist_ok=True)
    return d / f"sub-{sid:03d}.json"


def load_qc(cond, sid):
    p = qc_path(cond, sid)
    return json.loads(p.read_text()) if p.exists() else {}


def update_qc(cond, sid, **kv):
    qc = load_qc(cond, sid)
    qc.update(id=sid, cond=cond)
    qc.update(kv)
    qc_path(cond, sid).write_text(json.dumps(qc, indent=1, default=str))
    return qc


def exclude(cond, sid, stage, reason):
    update_qc(cond, sid, excluded=True, excluded_stage=stage, excluded_reason=reason)
    return f"EXCLUDED at {stage}: {reason}"


def clear_exclusion(cond, sid, stage):
    """Called when a stage is re-run: drop an exclusion that this same stage recorded earlier."""
    qc = load_qc(cond, sid)
    if qc.get("excluded") and qc.get("excluded_stage") == stage:
        for k in ("excluded_stage", "excluded_reason"):
            qc.pop(k, None)
        qc["excluded"] = False
        qc_path(cond, sid).write_text(json.dumps(qc, indent=1, default=str))


def is_excluded(cond, sid):
    return load_qc(cond, sid).get("excluded", False)


def set_montage(raw):
    """Attach 10-20 electrode positions while keeping the old channel names (T3, T4, T5, T6)."""
    raw.rename_channels({k: v for k, v in cfg.OLD_TO_NEW.items() if k in raw.ch_names})
    raw.set_montage(cfg.MONTAGE, on_missing="raise")
    raw.rename_channels({v: k for k, v in cfg.OLD_TO_NEW.items() if v in raw.ch_names})


def parse_args(description):
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--ids", type=int, nargs="*", help="child IDs to process (default: all)")
    ap.add_argument("--conds", nargs="*", default=cfg.CONDITIONS, choices=cfg.CONDITIONS)
    ap.add_argument("--force", action="store_true", help="redo even if the output already exists")
    ap.add_argument("--n-jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    return ap.parse_args()


def run_stage(name, worker, ids, conds, force, n_jobs):
    """Run worker(cond, sid, force) -> status string for every child x condition, in parallel."""
    jobs = []
    for cond in conds:
        found = discover(cond)
        for sid in (ids or sorted(found)):
            if sid in found:
                jobs.append((cond, sid))
            else:
                print(f"[{name}] {cond} {sid:3d}: no EDF found")
    print(f"[{name}] starting {len(jobs)} jobs on {n_jobs} workers", flush=True)
    stream = Parallel(n_jobs=n_jobs, return_as="generator_unordered")(delayed(_call)(worker, c, s, force) for c, s in jobs)
    statuses = []
    for i, (c, s, r) in enumerate(stream, 1):       # printed as each child finishes
        statuses.append(str(r))
        print(f"[{name}] ({i}/{len(jobs)}) {c} {s:3d}: {r}", flush=True)
    n_ex = sum(r.startswith("EXCLUDED") for r in statuses)
    n_sk = sum(r.startswith("skipped") for r in statuses)
    print(f"[{name}] done: {len(jobs)} jobs, {n_sk} skipped, {n_ex} excluded", flush=True)


def _call(worker, cond, sid, force):
    try:
        return cond, sid, worker(cond, sid, force)
    except Exception as e:                           # one bad file must not stop the whole run
        return cond, sid, f"EXCLUDED: crashed with {type(e).__name__}: {e}"
