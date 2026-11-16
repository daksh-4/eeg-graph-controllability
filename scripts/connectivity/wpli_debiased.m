function W = wpli_debiased(X)
% debiased weighted phase lag index (Vinck et al. 2011), averaged over bins; X is channels x bins x epochs
[C, B, E] = size(X);
im = imag(reshape(X, [C 1 B E]) .* conj(reshape(X, [1 C B E])));
sum_im = sum(im, 4);
sum_abs = sum(abs(im), 4);
sum_sq = sum(im .^ 2, 4);
W = (sum_im .^ 2 - sum_sq) ./ (sum_abs .^ 2 - sum_sq);
W = mean(W, 3, 'omitnan');
W(1:C+1:end) = NaN;
end
