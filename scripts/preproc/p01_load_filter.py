"""Stage 01: read the EDF, keep the 19 standard EEG channels, attach the 10-20 montage, band-pass filter.
Output: sub-XXX_<cond>_01-filt_raw.fif"""
import mne
import numpy as np

import config as cfg
import common as C


def worker(cond, sid, force=False):
    out = C.stage_path(cond, sid, "01-filt_raw")
    if out.exists() and not force:
        return "skipped (exists)"
    C.qc_path(cond, sid).write_text("{}")      # re-running stage 01 starts a fresh QC record for this child
    edf = C.discover(cond)[sid]
    raw = mne.io.read_raw_edf(edf, preload=True)
    orig_channels = list(raw.ch_names)

    raw.rename_channels({n: n.replace("EEG ", "").strip() for n in raw.ch_names})
    missing = [c for c in cfg.CHANNELS if c not in raw.ch_names]
    if missing:
        return C.exclude(cond, sid, "01", f"missing channels {missing}")
    raw.pick(cfg.CHANNELS)
    raw.reorder_channels(cfg.CHANNELS)
    C.set_montage(raw)
    raw.notch_filter(freqs=cfg.NOTCH_FREQS, notch_widths=cfg.NOTCH_WIDTH, method="fir", fir_design="firwin", phase="zero", verbose="ERROR")
    raw.filter(l_freq=cfg.L_FREQ, h_freq=cfg.H_FREQ, h_trans_bandwidth=cfg.H_TRANS, fir_design="firwin", phase="zero", verbose="ERROR")
    raw.save(out, overwrite=True, verbose="ERROR")

    data = raw.get_data()
    C.update_qc(cond, sid, excluded=False,
                edf=edf.name, n_channels_in_file=len(orig_channels), sfreq=raw.info["sfreq"],
                duration_s=round(raw.times[-1], 1),
                median_channel_sd_uV=round(float(np.median(data.std(axis=1)) * 1e6), 2))
    return f"ok ({raw.times[-1]:.0f} s, {len(orig_channels)} channels in file)"


def main(ids=None, conds=cfg.CONDITIONS, force=False, n_jobs=1):
    C.run_stage("01 load/filter", worker, ids, conds, force, n_jobs)


if __name__ == "__main__":
    a = C.parse_args(__doc__)
    main(a.ids, a.conds, a.force, a.n_jobs)
