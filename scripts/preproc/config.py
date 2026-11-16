"""Every preprocessing setting lives here (see analysis_plan_pass_b.md). Change settings here, nowhere else."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data/iranian/raw"
# Intermediate files are large, so they are kept outside the OneDrive-synced project folder.
DERIV = Path(os.environ.get("CAESAR_DERIV", Path.home() / "caesar_derivatives" / "pass_b"))
QC_DIR = ROOT / "outputs/preproc_qc"

CONDITIONS = ["rsEC", "rsEO"]  # resting eyes closed / eyes open

# 19 standard 10-20 channels, in the naming used by the EDF files (old nomenclature).
CHANNELS = ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "T3", "C3", "Cz", "C4", "T4", "T5", "P3", "Pz", "P4", "T6", "O1", "O2"]
# Only needed to look up electrode positions in MNE's montage (which uses the newer names).
OLD_TO_NEW = {"T3": "T7", "T4": "T8", "T5": "P7", "T6": "P8"}
MONTAGE = "standard_1020"

# 01 load and filter
L_FREQ, H_FREQ = 1.0, 45.0       # band-pass (Hz)
# The EDFs still contain strong 50 Hz mains noise (and its 100 Hz harmonic), despite the paper's stated notch: before this fix the
# residual above 45 Hz carried a median 55-67% of the variance. So: notch 50 Hz first, then a steeper low-pass (stopband from 47 Hz;
# the MNE default would leave a transition band out to ~56 Hz and pass the mains peak).
NOTCH_FREQS = [50.0]
NOTCH_WIDTH = 2.0                # notch width in Hz (stopband 49-51 Hz)
H_TRANS = 2.0                    # low-pass transition bandwidth in Hz (passband to 45 Hz, stopband from 47 Hz)

# 02 bad channels and re-reference
MAX_BAD_CHANNELS = 2             # more than this -> child excluded from that condition
BAD_CHANNEL_SEED = 97
REFERENCE = "average"

# 03 ICA
ICA_N_COMPONENTS = 15            # capped at the data rank
ICA_METHOD = "picard"
ICA_SEED = 97
ICA_MAX_ITER = 500
ICLABEL_THRESHOLD = 0.8
# "line noise" is deliberately not removed: the data were notched at acquisition and are low-passed at 45 Hz, so
# ICLabel's "line noise" components here were large slow components carrying 20-70% of the variance, not mains hum.
ICLABEL_REMOVE = {"eye blink", "muscle artifact", "heart beat", "channel noise"}

# 04 epoching
EPOCH_SECONDS = 2.0
# Amplitude rejection is relative to each child's own typical level, not an absolute cutoff: the stored EDF amplitudes
# differ 20-fold between children and do not track the authors' NeuroGuide values (all headers carry identical calibration),
# yet the spectral shape of the high-amplitude recordings agrees with the authors' analysis. An absolute cutoff would have
# excluded ~25 valid recordings. Epochs whose peak-to-peak amplitude (max over channels) exceeds this multiple of the
# child's median epoch value are rejected.
REJECT_PTP_RATIO = 2.5
FLAT_THRESHOLD = 1e-6            # volts
MIN_CLEAN_EPOCHS = 30            # 60 s of clean data
