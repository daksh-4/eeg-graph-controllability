"""Stage 03: ICA (Picard) on the continuous data, ICLabel to classify components, remove artifact components.
Removes components labelled eye blink, muscle artifact, heart beat, line noise or channel noise with probability > threshold.
Outputs: sub-XXX_<cond>_03-ica_raw.fif (cleaned data) and sub-XXX_<cond>_03_ica.fif (the ICA solution)"""
import mne
from mne.preprocessing import ICA
from mne_icalabel import label_components

import config as cfg
import common as C


def worker(cond, sid, force=False):
    out = C.stage_path(cond, sid, "03-ica_raw")
    if out.exists() and not force:
        return "skipped (exists)"
    src = C.stage_path(cond, sid, "02-clean_raw")
    if not src.exists():
        return "skipped (no stage-02 file)"
    raw = mne.io.read_raw_fif(src, preload=True, verbose="ERROR")

    rank = mne.compute_rank(raw, rank="info")["eeg"]
    n_comp = min(cfg.ICA_N_COMPONENTS, rank)
    ica = ICA(n_components=n_comp, method=cfg.ICA_METHOD, max_iter=cfg.ICA_MAX_ITER,
              fit_params=dict(ortho=False, extended=True), random_state=cfg.ICA_SEED)
    ica.fit(raw, verbose="ERROR")

    res = label_components(raw, ica, method="iclabel")
    labels, probs = res["labels"], res["y_pred_proba"]
    drop = [i for i, (lab, p) in enumerate(zip(labels, probs)) if lab in cfg.ICLABEL_REMOVE and p > cfg.ICLABEL_THRESHOLD]
    ica.exclude = drop
    clean = ica.apply(raw.copy(), verbose="ERROR")

    ica.save(C.stage_path(cond, sid, "03_ica"), overwrite=True, verbose="ERROR")
    clean.save(out, overwrite=True, verbose="ERROR")
    C.update_qc(cond, sid, ica_n_components=int(n_comp), ica_rank=int(rank),
                ica_labels=[str(x) for x in labels], ica_label_prob=[round(float(p), 3) for p in probs],
                ica_removed=[int(i) for i in drop], ica_removed_labels=[str(labels[i]) for i in drop],
                n_ica_removed=len(drop))
    return f"ok ({len(drop)}/{n_comp} components removed: {[labels[i] for i in drop] or 'none'})"


def main(ids=None, conds=cfg.CONDITIONS, force=False, n_jobs=1):
    C.run_stage("03 ICA", worker, ids, conds, force, n_jobs)


if __name__ == "__main__":
    a = C.parse_args(__doc__)
    main(a.ids, a.conds, a.force, a.n_jobs)
