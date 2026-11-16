function X = band_fft(data, fs, band)
% Hann-windowed FFT of each epoch, keeping the bins in [lo, hi): channels x bins x epochs
n = size(data, 2);
w = 0.5 - 0.5 * cos(2 * pi * (0:n-1) / (n - 1));
x = fft(data .* w, [], 2);
k = 0:floor(n/2);
sel = (k * fs / n >= band(1)) & (k * fs / n < band(2));
X = x(:, k(sel) + 1, :);
end
