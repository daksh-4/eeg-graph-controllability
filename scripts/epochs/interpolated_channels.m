function bad = interpolated_channels(cond, sid, cfg)
% names of the channels that were interpolated for this child
q = jsondecode(fileread(fullfile(cfg.deriv, 'qc', cond, sprintf('sub-%03d.json', sid))));
bad = {};
if isfield(q, 'bad_channels') && ~isempty(q.bad_channels)
    bad = cellstr(q.bad_channels);
end
bad = bad(:)';
end
