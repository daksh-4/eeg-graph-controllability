% function [avg, modal] = node_controllability(W)
% % Gu et al. 2015 / Chari et al. 2022: A = W / (1 + largest eigenvalue)
% A = W / (1 + max(eig(W)));
% [V, L] = eig((A + A') / 2);
% lam = diag(L)';
% avg = sum(V.^2 ./ (1 - lam.^2), 2);
% modal = sum((1 - lam.^2) .* V.^2, 2);
% end

function [avg, modal] = node_controllability(W, scale)
% Gu et al. 2015 / Chari et al. 2022: A = W / (1 + largest eigenvalue)
% the same constant multiplies every child's weights, so the +1 is small as it is for streamline counts
W = scale * W;
A = W / (1 + max(eig(W)));
[V, L] = eig((A + A') / 2);
lam = diag(L)';
avg = sum(V.^2 ./ (1 - lam.^2), 2);
modal = sum((1 - lam.^2) .* V.^2, 2);
end
