function nodal = nodal_efficiency(W)
% mean inverse shortest-path distance from each node to all others (length = 1 / weight)
nn = size(W,1);
D = distance_wei(weight_conversion(W, 'lengths'));
inv_d = 1 ./ D;  inv_d(1:nn+1:end) = 0;
nodal = sum(inv_d, 2) / (nn - 1);
end
