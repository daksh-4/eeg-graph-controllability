function T = graph_measures(S, band, cfg)
% graph measures for one condition and band, one row per child
n = numel(S.ids);
strength = NaN(n,1);  ge = NaN(n,1);  clust = NaN(n,1);
neff_frontal = NaN(n,1);  neff_posterior = NaN(n,1);  modularity = NaN(n,1);
avg_ctrl = NaN(n,1);  modal_ctrl = NaN(n,1);  ac_mc_rho = NaN(n,1);
eff_d20 = NaN(n,1);  clust_d20 = NaN(n,1);  eff_d40 = NaN(n,1);  clust_d40 = NaN(n,1);
d1 = cfg.densities(1);  d2 = cfg.densities(2);

for i = 1:n
    [W, ch] = load_child_matrix(S, i, band, cfg.variant);
    nn = size(W,1);

    % strength, global efficiency, clustering
    strength(i) = mean(W(triu(true(nn),1)));
    ge(i) = efficiency_wei(W);
    clust(i) = mean(clustering_coef_wu(W));

    % nodal efficiency in frontal and posterior electrodes
    nodal = nodal_efficiency(W);
    neff_frontal(i) = mean(nodal(ismember(ch, cfg.frontal)));
    neff_posterior(i) = mean(nodal(ismember(ch, cfg.posterior)));

    % modularity
    Q = zeros(cfg.n_louvain,1);
    for q = 1:cfg.n_louvain
        [~, Q(q)] = community_louvain(W);
    end
    modularity(i) = max(Q);

    % controllability
    [avg, modal] = node_controllability(W, cfg.ctrl_scale);
    avg_ctrl(i) = mean(avg);
    modal_ctrl(i) = mean(modal);
    ac_mc_rho(i) = rank_corr(avg, modal);

    % binary measures at fixed density
    B1 = double(threshold_proportional(W, d1) > 0);
    B2 = double(threshold_proportional(W, d2) > 0);
    eff_d20(i) = efficiency_bin(B1);  clust_d20(i) = mean(clustering_coef_bu(B1));
    eff_d40(i) = efficiency_bin(B2);  clust_d40(i) = mean(clustering_coef_bu(B2));
end

T = table(S.ids(:), strength, ge, clust, neff_frontal, neff_posterior, modularity, avg_ctrl, modal_ctrl, ac_mc_rho, ...
          eff_d20, eff_d40, clust_d20, clust_d40, 'VariableNames', ...
          {'id','mean_strength','geff_w','clust_w','neff_frontal','neff_posterior','modularity_w','mean_avg_ctrl','mean_modal_ctrl', ...
           'ac_mc_rho','eff_bin_d20','eff_bin_d40','clust_bin_d20','clust_bin_d40'});
end
