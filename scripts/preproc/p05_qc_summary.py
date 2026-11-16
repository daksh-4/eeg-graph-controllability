"""Stage 05: collect the per-child QC records into one table and make the checkpoint figures.
Outputs (in outputs/preproc_qc/): qc_summary.csv, qc_overview.png, example_psd_<cond>.png"""
import json
import warnings
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd

import config as cfg
import common as C

warnings.filterwarnings("ignore")


def collect():
    rows = []
    for p in sorted((cfg.DERIV / "qc").glob("*/sub-*.json")):
        q = json.loads(p.read_text())
        if q:
            rows.append(q)
    df = pd.DataFrame(rows)
    keep = ["id", "cond", "excluded", "excluded_stage", "excluded_reason", "n_channels_in_file", "duration_s", "median_channel_sd_uV",
            "n_bad_channels", "bad_channels", "n_ica_removed", "ica_removed_labels", "n_epochs_total", "n_epochs_clean", "clean_seconds"]
    return df[[c for c in keep if c in df.columns]].sort_values(["cond", "id"]).reset_index(drop=True)


def overview_figure(df, path):
    fig, ax = plt.subplots(2, 3, figsize=(14, 8))
    for cond, col in zip(cfg.CONDITIONS, ["tab:blue", "tab:orange"]):
        d = df[df.cond == cond]
        if "n_epochs_clean" in d:
            ax[0, 0].hist(d["n_epochs_clean"].dropna(), bins=15, alpha=0.6, color=col, label=cond)
        if "n_bad_channels" in d:
            ax[0, 1].hist(d["n_bad_channels"].dropna(), bins=np.arange(-0.5, 6.5, 1), alpha=0.6, color=col, label=cond)
        if "n_ica_removed" in d:
            ax[0, 2].hist(d["n_ica_removed"].dropna(), bins=np.arange(-0.5, 10.5, 1), alpha=0.6, color=col, label=cond)
    ax[0, 0].axvline(cfg.MIN_CLEAN_EPOCHS, color="k", ls="--"); ax[0, 0].set(title="clean 2 s epochs per child", xlabel="epochs")
    ax[0, 1].set(title="bad channels interpolated", xlabel="channels"); ax[0, 2].set(title="ICA components removed", xlabel="components")
    for a in ax[0]:
        a.legend()
    if "ica_removed_labels" in df:
        c = Counter(l for ls in df["ica_removed_labels"].dropna() for l in ls)
        ax[1, 0].bar(list(c) or ["none"], list(c.values()) or [0]); ax[1, 0].set(title="removed ICA component types (all children)")
        ax[1, 0].tick_params(axis="x", rotation=30)
    ex = df[df.excluded == True]  # noqa: E712
    c2 = Counter(ex["excluded_stage"]) if len(ex) else Counter()
    ax[1, 1].bar([f"stage {k}" for k in c2] or ["none"], list(c2.values()) or [0]); ax[1, 1].set(title="exclusions by stage")
    if "median_channel_sd_uV" in df:
        ax[1, 2].scatter(df["duration_s"], df["median_channel_sd_uV"], s=10, c=df["cond"].map({"rsEC": "tab:blue", "rsEO": "tab:orange"}))
        ax[1, 2].set(title="raw duration vs typical channel SD", xlabel="seconds", ylabel="uV")
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def psd_examples(cond, df, path, n=6, seed=1):
    ids = df[(df.cond == cond) & (df.excluded == False)]["id"].tolist()  # noqa: E712
    rng = np.random.default_rng(seed)
    ids = sorted(rng.choice(ids, size=min(n, len(ids)), replace=False)) if ids else []
    fig, axes = plt.subplots(2, 3, figsize=(14, 7), sharex=True, sharey=True)
    for a, sid in zip(axes.ravel(), ids):
        for suffix, lab in [("01-filt_raw", "after filter"), ("03-ica_raw", "after bad-channel fix + ICA")]:
            p = C.stage_path(cond, int(sid), suffix)
            if p.exists():
                raw = mne.io.read_raw_fif(p, preload=True, verbose="ERROR")
                psd = raw.compute_psd(fmin=1, fmax=45, verbose="ERROR")
                a.semilogy(psd.freqs, psd.get_data().mean(axis=0) * 1e12, label=lab)
        a.set(title=f"child {sid}", xlabel="Hz", ylabel="power (uV^2/Hz)"); a.legend(fontsize=7)
    fig.suptitle(f"{cond}: average spectrum before/after cleaning"); fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def main():
    cfg.QC_DIR.mkdir(parents=True, exist_ok=True)
    df = collect()
    df.to_csv(cfg.QC_DIR / "qc_summary.csv", index=False)
    overview_figure(df, cfg.QC_DIR / "qc_overview.png")
    for cond in cfg.CONDITIONS:
        psd_examples(cond, df, cfg.QC_DIR / f"example_psd_{cond}.png")
    print(f"[05 QC] {len(df)} child-condition records")
    print(df.groupby("cond").agg(n=("id", "size"), excluded=("excluded", "sum"),
                                 clean_epochs_median=("n_epochs_clean", "median"), clean_epochs_min=("n_epochs_clean", "min"),
                                 bad_channels_mean=("n_bad_channels", "mean"), ica_removed_mean=("n_ica_removed", "mean")).round(2).to_string())
    ex = df[df.excluded == True]  # noqa: E712
    if len(ex):
        print("\nExclusions:"); print(ex[["cond", "id", "excluded_stage", "excluded_reason"]].to_string(index=False))


if __name__ == "__main__":
    main()
