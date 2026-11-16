# EEG connectivity and graph network analysis

Connectivity (wPLI, coherence) and graph measures including controllability on resting EEG, one row per child per condition and band.

- `scripts/run_connectivity.m` computes the connectivity matrices from the cleaned epochs (needs [FieldTrip](https://www.fieldtriptoolbox.org/) to read them).
- `scripts/graph_networks.m` computes the graph measures from those matrices (needs the [Brain Connectivity Toolbox](https://sites.google.com/site/bctnet/) in a `BCT/` folder at the repository root).
- Settings are in `scripts/config/`; helper functions are in `scripts/epochs/`, `scripts/connectivity/` and `scripts/graph/`.
- `scripts/preproc/` holds the Python (MNE) preprocessing that produces the cleaned epochs: filtering, bad-channel handling, ICA and epoching. It needs `mne`, `pyprep`, `mne-icalabel` and `picard`.
- Controllability follows Gu et al. 2015 and Chari et al. 2022.

No data are included.
