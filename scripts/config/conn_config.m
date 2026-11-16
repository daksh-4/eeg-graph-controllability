function cfg = conn_config()
% settings for computing connectivity matrices from the cleaned epochs

cfg.deriv = fullfile(getenv('HOME'), 'caesar_derivatives', 'pass_b');
cfg.conds = {'rsEC', 'rsEO'};
cfg.bands = struct('theta', [4 8], 'alpha', [8 12], 'beta', [12 30]);   % [lo, hi) in Hz

cfg.n_epochs = 80;
cfg.epoch_seed = 97;
cfg.epoch_index_dir = fullfile(cfg.deriv, 'epoch_index');               % optional: epoch_index_<cond>.csv, one row per child (id, then the epoch numbers)

cfg.out_dir = fullfile(cfg.deriv, 'matlab_native');
end
