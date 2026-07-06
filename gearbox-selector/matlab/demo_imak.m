% demo_imak.m — İ-MAK Redüktör Seçici MATLAB kullanımı / usage examples
% Çalıştır / run:  demo_imak

% 1) Interaktif menü / interactive menu (uncomment):
% imak_reduktor();

% 2) Programatik, varsayılan girdiler / programmatic, default inputs:
r = imak_reduktor('hoist');
fprintf('Vinç kaldırma  -> Mt=%.0f Nm, n=%.1f rpm, motor=%g kW, Mn=%.0f Nm\n', ...
        r.MT, r.n, r.motor_kW, r.Mn);

% 3) Kendi değerlerinizle / with your own values (English output):
v = struct('m',3000, 'D',400, 'v',12);       % load 3 t, drum 400 mm, 12 m/min
r = imak_reduktor('hoist', v, 'en');
fprintf('Custom hoist   -> Mt=%.0f Nm, n=%.1f rpm, motor=%g kW\n', r.MT, r.n, r.motor_kW);

% 4) Ekrana tam rapor / full printed report:
imak_reduktor('kiln');

% 5) Toplu tarama / batch sweep over several applications:
ids = {'belt_inc','screw','ballmill','pump','fan'};
for i = 1:numel(ids)
    r = imak_reduktor(ids{i});
    fprintf('%-10s  Mn=%8.0f Nm  motor=%6g kW\n', ids{i}, r.Mn, r.motor_kW);
end
