"""Stage 02: detect bad channels (PREP-style), interpolate them, re-reference to the common average.
Detection uses pyprep's flatline/NaN, deviation and correlation criteria. The high-frequency-noise criterion is
skipped because the data are low-passed at 45 Hz (and were notched at 45-55 Hz at acquisition), so it cannot be assessed.
RANSAC is skipped because 19 channels give too few neighbours for it to be reliable.
Output: sub-XXX_<cond>_02-clean_raw.fif"""
import mne
from pyprep import NoisyChannels

import config as cfg
import common as C


def worker(cond, sid, force=False):
    out = C.stage_path(cond, sid, "02-clean_raw")
    if out.exists() and not force:
        return "skipped (exists)"
    src = C.stage_path(cond, sid, "01-filt_raw")
    if not src.exists():
        return "skipped (no stage-01 file)"
    C.clear_exclusion(cond, sid, "02")
    raw = mne.io.read_raw_fif(src, preload=True, verbose="ERROR")

    nd = NoisyChannels(raw.copy(), do_detrend=True, random_state=cfg.BAD_CHANNEL_SEED)
    nd.find_bad_by_nan_flat()
    nd.find_bad_by_deviation()
    nd.find_bad_by_correlation()
    bads = sorted(set(nd.bad_by_nan + nd.bad_by_flat + nd.bad_by_deviation + nd.bad_by_correlation))
    detail = dict(nan=nd.bad_by_nan, flat=nd.bad_by_flat, deviation=nd.bad_by_deviation, correlation=nd.bad_by_correlation)
    C.update_qc(cond, sid, bad_channels=bads, bad_channel_detail=detail, n_bad_channels=len(bads))

    if len(bads) > cfg.MAX_BAD_CHANNELS:
        return C.exclude(cond, sid, "02", f"{len(bads)} bad channels {bads}")
    if bads:
        raw.info["bads"] = bads
        raw.interpolate_bads(reset_bads=True, verbose="ERROR")
    raw.set_eeg_reference(cfg.REFERENCE, projection=False, verbose="ERROR")
    raw.save(out, overwrite=True, verbose="ERROR")
    return f"ok (bad channels: {bads or 'none'})"


def main(ids=None, conds=cfg.CONDITIONS, force=False, n_jobs=1):
    C.run_stage("02 bad channels", worker, ids, conds, force, n_jobs)


if __name__ == "__main__":
    a = C.parse_args(__doc__)
    main(a.ids, a.conds, a.force, a.n_jobs)
