function [data, fs, labels] = load_child_epochs(cond, sid, cfg)
% cleaned epochs of one child: data is channels x samples x epochs
f = fullfile(cfg.deriv, cond, sprintf('sub-%03d_%s_04-clean_epo.fif', sid, cond));
hdr = ft_read_header(f);
data = double(ft_read_data(f));
fs = hdr.Fs;
labels = hdr.label(:)';
end
