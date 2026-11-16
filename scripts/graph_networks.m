% graph network analysis, all conditions and bands

here = fileparts(mfilename('fullpath'));
addpath(genpath(here));
addpath(genpath(fullfile(here, '..', 'BCT')));

cfg = graph_config();

allT = table();
for c = 1:numel(cfg.conds)
    S = load(fullfile(cfg.data_dir, [cfg.measure '_' cfg.conds{c} '.mat']));
    for b = 1:numel(cfg.bands)
        T = graph_measures(S, cfg.bands{b}, cfg);
        T.cond = repmat(cfg.conds(c), height(T), 1);
        T.band = repmat(cfg.bands(b), height(T), 1);
        T = movevars(T, {'cond', 'band'}, 'After', 'id');
        allT = [allT; T];                           %#ok<AGROW>
    end
end

disp(groupsummary(allT, {'cond', 'band'}))
writetable(allT, cfg.out_file);
