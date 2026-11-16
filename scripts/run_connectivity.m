% wPLI and coherence matrices from the cleaned epochs, saved in the layout graph_networks.m reads

addpath(genpath(fileparts(mfilename('fullpath'))));
ft_defaults

cfg = conn_config();

% options for graph connectivity measures
measures = {'wpli', 'coherence'};
fns = {@wpli_debiased, @coherence_mag};

% options for splitting epochs into halves
variants = {'all', 'h1', 'h2'};
bands = fieldnames(cfg.bands);
if ~exist(cfg.out_dir, 'dir'), mkdir(cfg.out_dir); end

for c = 1:numel(cfg.conds)
    cond = cfg.conds{c};
    files = dir(fullfile(cfg.deriv, cond, ['sub-*_' cond '_04-clean_epo.fif']));
    ids = sort(cellfun(@(s) sscanf(s, 'sub-%d'), {files.name})');
    n = numel(ids);
    R = cell(n, numel(measures));
    for k = 1:n
        [data, fs, labels] = load_child_epochs(cond, ids(k), cfg);
        if k == 1, channels = labels; else, assert(isequal(labels, channels)); end
        bad = find(ismember(labels, interpolated_channels(cond, ids(k), cfg)));
        idx = select_epochs(size(data, 3), cond, ids(k), cfg);
        for m = 1:numel(measures)
            R{k, m} = connectivity_matrices(data(:, :, idx), fs, bad, cfg, fns{m});
        end
    end
    for m = 1:numel(measures)
        S = struct();
        for v = 1:numel(variants)
            for b = 1:numel(bands)
                f = [variants{v} '_' bands{b}];
                tmp = cellfun(@(r) r.(f), R(:, m), 'UniformOutput', false);
                S.(['W_' f]) = cat(3, tmp{:});
            end
        end
        S.ids = ids;
        S.channels = channels;
        S.keep = cell2mat(cellfun(@(r) ~all(isnan(r.all_alpha), 2)', R(:, m), 'UniformOutput', false));
        save(fullfile(cfg.out_dir, [measures{m} '_' cond '.mat']), '-struct', 'S');
    end
end
