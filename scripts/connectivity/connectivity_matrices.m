function M = connectivity_matrices(data, fs, bad, cfg, measure_fn)
% one child's matrices for every variant (all epochs, odd, even) and band; interpolated channels set to NaN
n = size(data, 3);
pos = struct('all', 1:n, 'h1', 1:2:n, 'h2', 2:2:n);
vn = fieldnames(pos);
bn = fieldnames(cfg.bands);
M = struct();
for v = 1:numel(vn)
    for b = 1:numel(bn)
        X = band_fft(data(:, :, pos.(vn{v})), fs, cfg.bands.(bn{b})); % Hann window
        W = measure_fn(X);
        W(bad, :) = NaN;
        W(:, bad) = NaN;
        M.([vn{v} '_' bn{b}]) = W;
    end
end
end
