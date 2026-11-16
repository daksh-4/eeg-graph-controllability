"""Stage 04: cut into non-overlapping 2 s epochs, reject epochs far above the child's own typical amplitude (or flat),
and exclude children with fewer than the minimum number of clean epochs.
Output: sub-XXX_<cond>_04-clean_epo.fif"""
from collections import Counter

import mne
import numpy as np

import config as cfg
import common as C


def worker(cond, sid, force=False):
    out = C.stage_path(cond, sid, "04-clean_epo")
    if out.exists() and not force:
        return "skipped (exists)"
    src = C.stage_path(cond, sid, "03-ica_raw")
    if not src.exists():
        return "skipped (no stage-03 file)"
    C.clear_exclusion(cond, sid, "04")
    raw = mne.io.read_raw_fif(src, preload=True, verbose="ERROR")

    epochs = mne.make_fixed_length_epochs(raw, duration=cfg.EPOCH_SECONDS, overlap=0.0, preload=True, verbose="ERROR")
    n_total = len(epochs)
    ptp = np.ptp(epochs.get_data(), axis=2).max(axis=1)           # per epoch: largest peak-to-peak over channels
    median_ptp = float(np.median(ptp))
    epochs.drop(np.where(ptp > cfg.REJECT_PTP_RATIO * median_ptp)[0], reason="AMPLITUDE_VS_CHILD_MEDIAN", verbose="ERROR")
    epochs.drop_bad(flat=dict(eeg=cfg.FLAT_THRESHOLD), verbose="ERROR")
    n_kept = len(epochs)
    why = Counter(ch for log in epochs.drop_log for ch in log)
    C.update_qc(cond, sid, n_epochs_total=n_total, n_epochs_clean=n_kept, clean_seconds=n_kept * cfg.EPOCH_SECONDS,
                child_median_ptp_uV=round(median_ptp * 1e6, 1), epochs_dropped_by=dict(why))

    if n_kept < cfg.MIN_CLEAN_EPOCHS:
        return C.exclude(cond, sid, "04", f"only {n_kept}/{n_total} clean epochs (minimum {cfg.MIN_CLEAN_EPOCHS})")
    epochs.save(out, overwrite=True, verbose="ERROR")
    return f"ok ({n_kept}/{n_total} epochs kept)"


def main(ids=None, conds=cfg.CONDITIONS, force=False, n_jobs=1):
    C.run_stage("04 epoch", worker, ids, conds, force, n_jobs)


if __name__ == "__main__":
    a = C.parse_args(__doc__)
    main(a.ids, a.conds, a.force, a.n_jobs)
