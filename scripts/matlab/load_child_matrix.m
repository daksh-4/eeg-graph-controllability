function [W, ch] = load_child_matrix(S, k, band, variant)
% one child's matrix: drop interpolated channels, negatives and diagonal set to 0
if nargin < 4, variant = 'all'; end
W = S.(['W_' variant '_' band])(:,:,k);
keep = logical(S.keep(k,:));
W = W(keep, keep);
W(W < 0) = 0;  W(1:size(W,1)+1:end) = 0;
ch = cellstr(S.channels);
ch = ch(keep);
end
