function idx = select_epochs(n_available, cond, sid, cfg)
% the same number of epochs for every child, in time order
f = fullfile(cfg.epoch_index_dir, ['epoch_index_' cond '.csv']);
if exist(f, 'file')
    T = readtable(f);
    idx = T{T.id == sid, 2:end};
    if isempty(idx), error('no epoch indices for child %d in %s', sid, f); end
    idx = sort(idx(:)');
    return
end
if n_available < cfg.n_epochs
    error('only %d clean epochs, need %d', n_available, cfg.n_epochs);
end
seed = cfg.epoch_seed + 10 * sid + find(strcmp(cfg.conds, cond)) - 1;
s = RandStream('mt19937ar', 'Seed', seed);
idx = sort(randperm(s, n_available, cfg.n_epochs));
end
