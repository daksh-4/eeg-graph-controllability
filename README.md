# EEG graph network analysis (MATLAB)

Graph measures and controllability on resting EEG connectivity matrices (wPLI or coherence), one row per child per condition and band.

- `graph_networks.m` runs everything. Settings are in `scripts/matlab/graph_config.m`.
- Needs the [Brain Connectivity Toolbox](https://sites.google.com/site/bctnet/); put it in a `BCT/` folder next to `graph_networks.m`.
- Input: one `.mat` file per measure and condition (`wpli_rsEC.mat`, ...) containing `W_<variant>_<band>` (19 x 19 x N), `ids`, `channels` and `keep`.
- Output: `graph_networks_outputs_all.csv`.
- Controllability follows Gu et al. 2015 and Chari et al. 2022.
