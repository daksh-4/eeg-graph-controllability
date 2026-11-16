function cfg = graph_config()
% settings for the MATLAB graph analysis

cfg.measure = 'wpli';                              % wpli or coherence
cfg.conds   = {'rsEC', 'rsEO'};
cfg.bands   = {'theta', 'alpha', 'beta'};
cfg.variant = 'all';                               % all, h1 or h2 (odd / even epochs)

cfg.data_dir = fullfile(getenv('HOME'), 'caesar_derivatives', 'pass_b', 'matlab_native');

% regions 
cfg.frontal   = {'Fp1', 'Fp2', 'F3', 'F4', 'F7', 'F8', 'Fz'};
cfg.posterior = {'P3', 'P4', 'Pz', 'O1', 'O2'};

cfg.n_louvain = 10;                                % keep the best of 10 runs
cfg.densities = [0.2 0.4];
cfg.ctrl_scale = 100;                              % constant multiplier on the weights before controllability

if strcmp(cfg.measure, 'wpli')
    cfg.out_file = 'graph_networks_outputs_all.csv';
else
    cfg.out_file = ['graph_networks_outputs_all_' cfg.measure '.csv'];
end
end
