function rho = rank_corr(x, y)
rx = zeros(numel(x),1);  ry = zeros(numel(y),1);
[~, ix] = sort(x(:));  rx(ix) = 1:numel(x);
[~, iy] = sort(y(:));  ry(iy) = 1:numel(y);
cc = corrcoef(rx, ry);
rho = cc(1, 2);
end
