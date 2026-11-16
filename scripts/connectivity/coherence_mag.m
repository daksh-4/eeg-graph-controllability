function Cm = coherence_mag(X)
% magnitude coherence, averaged over bins; X is channels x bins x epochs
[C, B, E] = size(X);
S = sum(reshape(X, [C 1 B E]) .* conj(reshape(X, [1 C B E])), 4) / E;
Sm = reshape(S, C * C, B);
p = real(Sm(1:C+1:end, :));
Cm = abs(S) ./ sqrt(reshape(p, [C 1 B]) .* reshape(p, [1 C B]));
Cm = mean(Cm, 3, 'omitnan');
Cm(1:C+1:end) = NaN;
end
