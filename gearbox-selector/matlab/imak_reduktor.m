function out = imak_reduktor(appId, v, lang)
%IMAK_REDUKTOR  İ-MAK Redüktör Seçici / I-MAK Gearbox Selector (MATLAB).
%   Same 26 applications and formulas as the web / C++ versions.
%   Sources: İ-MAK ArGe Teknik Eğitim Sunumu + standard drive engineering.
%
%   USAGE
%     imak_reduktor()                    % interactive menu (choose app, enter values)
%     r = imak_reduktor('kiln')          % programmatic, default inputs
%     r = imak_reduktor('kiln', v)       % v = struct of input overrides
%     r = imak_reduktor('kiln', v, 'en') % English
%
%   v may contain any variable id of the application, plus optional
%   n1 (motor rpm, default 1450), eta (gearbox efficiency), sf (service factor).
%
%   Returns struct r with fields:
%     id, name, formula, series
%     MT      - output moment [Nm]
%     n       - output speed [rpm]
%     Pout    - gearbox output power [kW]
%     Pmotor  - required motor power [kW]
%     motor_kW- next standard IEC motor size [kW]
%     ratio   - i = n1/n
%     sf      - service factor used
%     Mn      - required nominal moment = MT*sf [Nm]
%     steps   - struct array of worked calculation steps
%
%   EXAMPLE
%     r = imak_reduktor('hoist');                 % 2943 Nm, 10.6 rpm, 4 kW
%     r = imak_reduktor('belt_inc', struct('m',10000,'a',25));
%     imak_reduktor()                              % interactive

    if nargin < 3 || isempty(lang), lang = 'tr'; end
    apps = getApps();

    if nargin == 0
        interactive(apps, lang);
        out = [];
        return;
    end

    k = find(strcmp({apps.id}, appId), 1);
    if isempty(k)
        error('imak_reduktor:unknownApp', 'Unknown application id: %s\nValid ids: %s', ...
              appId, strjoin({apps.id}, ', '));
    end
    a = apps(k);

    vv = struct();
    for i = 1:numel(a.vars), vv.(a.vars(i).id) = a.vars(i).def; end
    if nargin >= 2 && ~isempty(v) && isstruct(v)
        f = fieldnames(v);
        for i = 1:numel(f), vv.(f{i}) = v.(f{i}); end
    end
    n1  = getdef(vv, 'n1', 1450);
    eta = getdef(vv, 'eta', a.eta);
    sf  = getdef(vv, 'sf',  a.sf);

    r = computeResult(a, vv, n1, eta, sf, lang);
    if nargout == 0
        printResult(a, r, lang);
    else
        out = r;
    end
end

% ======================================================================
function r = computeResult(a, v, n1, eta, sf, lang)
    s = a.fn(v);
    MT = s.MT; n = s.n; Pout = s.Pout;
    if ~isfinite(MT) && isfinite(Pout) && n > 0, MT = 9550*Pout/n; end
    if ~isfinite(Pout) && isfinite(MT) && n > 0, Pout = MT*n/9550; end
    if eta <= 0, eta = 1; end
    Pmotor = Pout/eta;
    motor  = iecUp(Pmotor);
    ratio  = NaN; if n1 > 0 && n > 0, ratio = n1/n; end
    if sf < 1, sf = 1; end
    Mn = MT*sf;

    r = struct();
    r.id      = a.id;
    r.name    = pick(a.nameTR, a.nameEN, lang);
    r.formula = pick(a.fTR, a.fEN, lang);
    r.series  = pick(a.serTR, a.serEN, lang);
    r.MT = MT;  r.n = n;  r.Pout = Pout;
    r.Pmotor = Pmotor;  r.motor_kW = motor;
    r.ratio = ratio;  r.sf = sf;  r.Mn = Mn;
    r.steps = s.steps;
end

% ======================================================================
function s = iecUp(p)
    IEC = [0.12 0.18 0.25 0.37 0.55 0.75 1.1 1.5 2.2 3 4 5.5 7.5 11 15 18.5 ...
           22 30 37 45 55 75 90 110 132 160 200 250 315 355];
    idx = find(IEC >= p - 1e-9, 1);
    if isempty(idx), s = IEC(end); else, s = IEC(idx); end
end

function val = getdef(v, name, def)
    if isfield(v, name), val = v.(name); else, val = def; end
end

function s = pick(tr, en, lang)
    if strcmp(lang, 'en'), s = en; else, s = tr; end
end

function s = st(tr, en, val, u)
    s = struct('tr', tr, 'en', en, 'val', val, 'u', u);
end

function s = fmtn(x)
    if ~isfinite(x), s = '-'; return; end
    a = abs(x);
    if a < 10,  s = sprintf('%.2f', x);
    elseif a < 100, s = sprintf('%.1f', x);
    else, s = sprintf('%.0f', x); end
    if any(s == '.'), while s(end)=='0', s(end)=[]; end; if s(end)=='.', s(end)=[]; end; end
end

% ======================================================================
function v = mkVar(id, tr, en, u, def)
    v = struct('id', id, 'tr', tr, 'en', en, 'u', u, 'def', def);
end

function a = mkApp(id, gTR, gEN, nTR, nEN, sTR, sEN, fTR, fEN, sf, eta, vars, fn)
    a = struct('id', id, 'grpTR', gTR, 'grpEN', gEN, 'nameTR', nTR, 'nameEN', nEN, ...
               'serTR', sTR, 'serEN', sEN, 'fTR', fTR, 'fEN', fEN, ...
               'sf', sf, 'eta', eta, 'vars', {vars}, 'fn', fn);
end

% ======================================================================
function apps = getApps()
    apps = struct('id', {}, 'grpTR', {}, 'grpEN', {}, 'nameTR', {}, 'nameEN', {}, ...
                  'serTR', {}, 'serEN', {}, 'fTR', {}, 'fEN', {}, 'sf', {}, 'eta', {}, ...
                  'vars', {}, 'fn', {});

    % ---------- Konveyör & Taşıma ----------
    apps(end+1) = mkApp('belt_h','Konveyör & Taşıma','Conveying & Handling', ...
        'Bantlı konveyör — yatay','Belt conveyor — horizontal','İRK Serisi (helis-konik)','İRK series (helical-bevel)', ...
        'Mᴛ=k·m·g·r ; n=9,55·v/r','Mᴛ=k·m·g·r ; n=9.55·v/r',1.25,0.96, ...
        [mkVar('m','Yük kütlesi m','Load mass m','kg',10000), mkVar('D','Tambur çapı Ø','Drum Ø','mm',250), ...
         mkVar('v','Bant hızı v','Belt speed v','m/s',1.0), mkVar('k','Sürtünme katsayısı k','Friction coeff. k','',0.125)], @calc_belt_h);

    apps(end+1) = mkApp('belt_inc','Konveyör & Taşıma','Conveying & Handling', ...
        'Bantlı konveyör — eğimli','Belt conveyor — inclined','İRK Serisi (helis-konik)','İRK series (helical-bevel)', ...
        'Mᴛ=k·(cosα+sinα)·m·g·r ; n=9,55·v/r','Mᴛ=k·(cosα+sinα)·m·g·r ; n=9.55·v/r',1.25,0.96, ...
        [mkVar('m','Yük kütlesi m','Load mass m','kg',10000), mkVar('D','Tambur çapı Ø','Drum Ø','mm',250), ...
         mkVar('v','Bant hızı v','Belt speed v','m/s',1.0), mkVar('a','Eğim α','Incline α','deg',25), ...
         mkVar('k','Sürtünme katsayısı k','Friction coeff. k','',0.125)], @calc_belt_inc);

    apps(end+1) = mkApp('screw','Konveyör & Taşıma','Conveying & Handling', ...
        'Helezon (vidalı) konveyör','Screw (auger) conveyor','Helis redüktörlü motor','Helical geared motor', ...
        'n=(Q/60)/G ; Qtop=G·(L/h) ; v=h·n/1000 ; Pm=Qtop·v/(60·75·1,36·η)','n=(Q/60)/G ; Qtot=G·(L/h) ; v=h·n/1000 ; Pm=Qtot·v/(60·75·1.36·η)',1.25,0.96, ...
        [mkVar('Q','Kapasite Q','Capacity Q','kg/h',8000), mkVar('Gk','Hatve yükü G','Load per pitch G','kg',100), ...
         mkVar('L','Uzunluk L','Length L','mm',3000), mkVar('h','Hatve h','Pitch h','mm',300), ...
         mkVar('ho','Yükleme verimi','Loading eff.','',0.30)], @calc_screw);

    apps(end+1) = mkApp('elevator','Konveyör & Taşıma','Conveying & Handling', ...
        'Kovalı elevatör','Bucket elevator','Helis-konik + geri dönüşsüz','Helical-bevel + backstop', ...
        'Po=k·Q·H/367 ; n=60·v/(π·D)','Po=k·Q·H/367 ; n=60·v/(π·D)',1.4,0.96, ...
        [mkVar('Q','Kapasite Q','Capacity Q','t/h',50), mkVar('H','Kaldırma yüksekliği H','Lift height H','m',20), ...
         mkVar('v','Hız v','Speed v','m/s',1.5), mkVar('D','Kafa tamburu Ø','Head pulley Ø','mm',500), ...
         mkVar('k','Dolum faktörü k','Fill factor k','',1.25)], @calc_elevator);

    apps(end+1) = mkApp('chain','Konveyör & Taşıma','Conveying & Handling', ...
        'Zincirli / sıyırıcı konveyör','Chain / drag conveyor','İRK Serisi (helis-konik)','İRK series (helical-bevel)', ...
        'Mᴛ=f·m·g·r ; n=v/(π·D)','Mᴛ=f·m·g·r ; n=v/(π·D)',1.5,0.95, ...
        [mkVar('m','Hareketli kütle m','Moving mass m','kg',8000), mkVar('D','Zincir dişlisi Ø','Sprocket Ø','mm',250), ...
         mkVar('v','Zincir hızı v','Chain speed v','m/min',20), mkVar('f','Sürtünme katsayısı f','Friction coeff. f','',0.30)], @calc_chain);

    apps(end+1) = mkApp('feeder','Konveyör & Taşıma','Conveying & Handling', ...
        'Titreşimli besleyici','Vibrating feeder','Mil üstü redüktörlü motor','Shaft-mounted geared motor', ...
        'ω=2π·n/60 ; Po=k·m·A²·ω³/1000','ω=2π·n/60 ; Po=k·m·A²·ω³/1000',1.75,0.95, ...
        [mkVar('m','Titreşen kütle m','Vibrating mass m','kg',300), mkVar('A','Genlik A','Amplitude A','mm',4), ...
         mkVar('n','Ekssantrik devri','Exciter speed','rpm',750), mkVar('k','Güç faktörü k','Power factor k','',0.40)], @calc_vib);

    % ---------- Kaldırma & Vinç ----------
    apps(end+1) = mkApp('hoist','Kaldırma & Vinç','Lifting & Crane', ...
        'Vinç kaldırma (tambur + palanga)','Crane hoist (drum + falls)','İRC Serisi (kaldırma)','İRC series (hoist)', ...
        'Mᴛ=m·g·r/z ; n=9,55·v·z/r','Mᴛ=m·g·r/z ; n=9.55·v·z/r',1.5,0.97, ...
        [mkVar('m','Kaldırılacak yük m','Load m','kg',2000), mkVar('D','Tambur çapı Ø','Drum Ø','mm',300), ...
         mkVar('v','Kaldırma hızı v','Lift speed v','m/min',10), mkVar('z','Palanga kat sayısı z','Rope falls z','',1)], @calc_hoist);

    apps(end+1) = mkApp('pulley','Kaldırma & Vinç','Lifting & Crane', ...
        'Palangalı kaldırma','Pulley / block-and-tackle hoist','İRC Serisi (kaldırma)','İRC series (hoist)', ...
        'Mᴛ=m·g·r/z ; n=9,55·v·z/r','Mᴛ=m·g·r/z ; n=9.55·v·z/r',1.5,0.95, ...
        [mkVar('m','Kaldırılacak yük m','Load m','kg',5000), mkVar('D','Tambur çapı Ø','Drum Ø','mm',400), ...
         mkVar('v','Kaldırma hızı v','Lift speed v','m/min',8), mkVar('z','Palanga kat sayısı z','Rope falls z','',2), ...
         mkVar('re','Palanga verimi','Reeving eff.','',0.95)], @calc_pulley);

    apps(end+1) = mkApp('travel','Kaldırma & Vinç','Lifting & Crane', ...
        'Yürütme (köprü/araba)','Travel (bridge / trolley)','Yürütme redüktörlü motor','Travel geared motor', ...
        'Mᴛ=[Q·f+μ·Q·(d/2)]·g ; v=π·D·n/60000','Mᴛ=[Q·f+μ·Q·(d/2)]·g ; v=π·D·n/60000',1.25,0.95, ...
        [mkVar('Q','Yük Q','Load Q','kg',5000), mkVar('D','Tekerlek çapı Ø','Wheel Ø','mm',500), ...
         mkVar('d','Rulman çapı Ø','Bearing Ø','mm',100), mkVar('v','Yürütme hızı v','Travel speed v','m/s',1.5), ...
         mkVar('f','Yuvarlanma katsayısı f','Rolling coeff. f','',0.002), mkVar('mu','Rulman sürtünmesi μ','Bearing friction μ','',0.008)], @calc_travel);

    apps(end+1) = mkApp('slew','Kaldırma & Vinç','Lifting & Crane', ...
        'Döner (slewing) tahrik','Slewing drive','Helis-konik redüktörlü motor','Helical-bevel geared motor', ...
        'J=m·r² ; α=(2π·n/60)/t ; Mᴛ=J·α+Tf','J=m·r² ; α=(2π·n/60)/t ; Mᴛ=J·α+Tf',1.5,0.94, ...
        [mkVar('m','Dönen kütle m','Slewing mass m','kg',5000), mkVar('r','Kütle yarıçapı r','Mass radius r','m',3), ...
         mkVar('n','Dönme devri','Slew speed','rpm',1.5), mkVar('t','Hızlanma süresi t','Accel time t','s',5), ...
         mkVar('Tf','Sürtünme momenti Tf','Friction torque Tf','Nm',500)], @calc_slew);

    apps(end+1) = mkApp('lift','Kaldırma & Vinç','Lifting & Crane', ...
        'Asansör (halatlı)','Passenger lift (traction)','Sertifikalı asansör tahriki','Certified lift drive', ...
        'F=Q·(1−b)·g ; Po=F·v/1000 ; n=60·rf·v/(π·D)','F=Q·(1−b)·g ; Po=F·v/1000 ; n=60·rf·v/(π·D)',1.75,0.95, ...
        [mkVar('Q','Kabin yükü Q','Car load Q','kg',1000), mkVar('v','Hız v','Speed v','m/s',1.0), ...
         mkVar('b','Denge oranı b','Balance b','',0.5), mkVar('D','Kasnak çapı Ø','Sheave Ø','mm',600), ...
         mkVar('rf','Askı oranı (1/2)','Roping factor (1/2)','',1)], @calc_lift);

    % ---------- Karıştırma & Proses ----------
    apps(end+1) = mkApp('mixer_b','Karıştırma & Proses','Mixing & Process', ...
        'Karıştırıcı — kanat yöntemi','Agitator — blade method','Helis redüktörlü motor (karıştırıcı)','Helical geared motor (agitator)', ...
        'Mk=(Ød/2)·b·ki·ρ·10 ; Mᴛ=ΣMk','Mk=(Ød/2)·b·ki·ρ·10 ; Mᴛ=ΣMk',1.5,0.95, ...
        [mkVar('Dd','Pervane çapı Ød','Impeller Ø','mm',1500), mkVar('b','Pervane genişliği b','Blade width b','mm',100), ...
         mkVar('k1','1. kanat sıvı yük. k1','Blade-1 liquid h. k1','mm',3500), mkVar('k2','2. kanat k2','Blade-2 k2','mm',2500), ...
         mkVar('k3','3. kanat k3','Blade-3 k3','mm',1500), mkVar('n','Mil devri n','Shaft speed n','rpm',20), ...
         mkVar('ro','Yoğunluk ρ','Density ρ','gr/cm3',1.1)], @calc_mixer_b);

    apps(end+1) = mkApp('mixer_np','Karıştırma & Proses','Mixing & Process', ...
        'Karıştırıcı — güç sayısı (Np)','Agitator — power number (Np)','Helis redüktörlü motor','Helical geared motor', ...
        'N=n/60 ; Po=Np·ρ·N³·D⁵/1000','N=n/60 ; Po=Np·ρ·N³·D⁵/1000',1.5,0.96, ...
        [mkVar('Np','Güç sayısı Np','Power number Np','',1.5), mkVar('ro','Yoğunluk ρ','Density ρ','kg/m3',1000), ...
         mkVar('D','Pervane çapı Ø','Impeller Ø','mm',500), mkVar('n','Mil devri n','Shaft speed n','rpm',60)], @calc_mixer_np);

    apps(end+1) = mkApp('kiln','Karıştırma & Proses','Mixing & Process', ...
        'Döner fırın / kurutma tamburu','Rotary kiln / drying drum','Helis-konik redüktörlü motor','Helical-bevel geared motor', ...
        'Mᴛ=(1+k)·m·g·(D/2)·e','Mᴛ=(1+k)·m·g·(D/2)·e',1.5,0.95, ...
        [mkVar('D','İç çap Ø','Internal Ø','mm',3000), mkVar('m','Dönen yük m','Rotating load m','kg',20000), ...
         mkVar('e','Eksantriklik e','Eccentricity e','',0.35), mkVar('n','Dönme devri n','Rotation speed n','rpm',2), ...
         mkVar('k','Sürtünme payı k','Friction allow. k','%',20)], @calc_kiln);

    apps(end+1) = mkApp('extruder','Karıştırma & Proses','Mixing & Process', ...
        'Ekstruder (vida)','Extruder (screw)','Helis redüktörlü motor (yüksek eksenel)','Helical geared motor (high axial)', ...
        'Po=SME·Q ; Mᴛ=9550·Po/n','Po=SME·Q ; Mᴛ=9550·Po/n',1.5,0.96, ...
        [mkVar('Q','Debi Q','Throughput Q','kg/h',200), mkVar('SME','Özgül mek. enerji','Specific mech. energy','kWh/kg',0.20), ...
         mkVar('n','Vida devri n','Screw speed n','rpm',100)], @calc_extruder);

    % ---------- Değirmen & Öğütme ----------
    apps(end+1) = mkApp('roller','Değirmen & Öğütme','Milling & Grinding','Valsli değirmen (un)','Roller mill (flour)', ...
        'Helis redüktörlü motor','Helical geared motor','Po=E·Q ; Mᴛ=9550·Po/n','Po=E·Q ; Mᴛ=9550·Po/n',1.5,0.96, ...
        specVars(10,10,300), @calc_specE);
    apps(end+1) = mkApp('hammer','Değirmen & Öğütme','Milling & Grinding','Çekiçli değirmen','Hammer mill', ...
        'Helis redüktörlü motor (darbe)','Helical geared motor (shock)','Po=E·Q ; Mᴛ=9550·Po/n','Po=E·Q ; Mᴛ=9550·Po/n',1.75,0.96, ...
        specVars(5,15,1500), @calc_specE);

    apps(end+1) = mkApp('ballmill','Değirmen & Öğütme','Milling & Grinding','Bilyalı değirmen (Bond)','Ball mill (Bond)', ...
        'Değirmen tipi redüktör','Mill-duty geared drive','E=10·Wi·(1/√P80−1/√F80) ; Po=E·Q','E=10·Wi·(1/√P80−1/√F80) ; Po=E·Q',1.75,0.95, ...
        [mkVar('Q','Kapasite Q','Capacity Q','t/h',20), mkVar('Wi','İş indeksi Wi','Work index Wi','kWh/t',13), ...
         mkVar('F','Besleme F80','Feed F80','um',10000), mkVar('Pp','Ürün P80','Product P80','um',100), ...
         mkVar('n','Değirmen devri n','Mill speed n','rpm',18)], @calc_ball);

    apps(end+1) = mkApp('sifter','Değirmen & Öğütme','Milling & Grinding','Elek / plansifter','Sifter / plansifter', ...
        'Helis redüktörlü motor','Helical geared motor','ω=2π·n/60 ; Po=k·m·r²·ω³/1000','ω=2π·n/60 ; Po=k·m·r²·ω³/1000',1.5,0.96, ...
        [mkVar('m','Salınan kütle m','Gyrating mass m','kg',300), mkVar('r','Salınım yarıçapı r','Gyration throw r','mm',40), ...
         mkVar('n','Devir n','Speed n','rpm',220), mkVar('k','Sönüm faktörü k','Damping factor k','',0.35)], @calc_sifter);

    apps(end+1) = mkApp('pellet','Değirmen & Öğütme','Milling & Grinding','Pelet değirmeni','Pellet mill', ...
        'Helis-konik redüktör (ağır)','Helical-bevel (heavy)','Po=E·Q ; Mᴛ=9550·Po/n','Po=E·Q ; Mᴛ=9550·Po/n',1.75,0.95, ...
        specVars(8,45,250), @calc_specE);

    % ---------- Kırma & Titreşim ----------
    apps(end+1) = mkApp('crusher','Kırma & Titreşim','Crushing & Vibrating','Kırıcı (taş / cevher)','Crusher (stone / ore)', ...
        'Helis-konik redüktör (ağır)','Helical-bevel (heavy duty)','Po=E·Q ; Mᴛ=9550·Po/n','Po=E·Q ; Mᴛ=9550·Po/n',1.75,0.95, ...
        specVars(50,2,200), @calc_specE);

    apps(end+1) = mkApp('vibscreen','Kırma & Titreşim','Crushing & Vibrating','Titreşimli elek','Vibrating screen', ...
        'Mil üstü redüktörlü motor','Shaft-mounted geared motor','ω=2π·n/60 ; Po=k·m·A²·ω³/1000','ω=2π·n/60 ; Po=k·m·A²·ω³/1000',1.75,0.95, ...
        [mkVar('m','Titreşen kütle m','Vibrating mass m','kg',800), mkVar('A','Genlik A','Amplitude A','mm',5), ...
         mkVar('n','Ekssantrik devri','Exciter speed','rpm',900), mkVar('k','Güç faktörü k','Power factor k','',0.5)], @calc_vib);

    apps(end+1) = mkApp('rotable','Kırma & Titreşim','Crushing & Vibrating','Döner tabla / turntable','Rotary table / turntable', ...
        'Helis-konik redüktörlü motor','Helical-bevel geared motor','J=0,5·m·r² ; α=(2π·n/60)/t ; Mᴛ=J·α+Tf','J=0.5·m·r² ; α=(2π·n/60)/t ; Mᴛ=J·α+Tf',1.5,0.95, ...
        [mkVar('m','Tabla + yük m','Table + load m','kg',2000), mkVar('r','Yarıçap r','Radius r','mm',800), ...
         mkVar('n','Çalışma devri n','Operating speed n','rpm',5), mkVar('t','Hızlanma süresi t','Accel time t','s',3), ...
         mkVar('Tf','Sürtünme momenti Tf','Friction torque Tf','Nm',200)], @calc_rotable);

    % ---------- Pompa & Fan ----------
    apps(end+1) = mkApp('pump','Pompa & Fan','Pumps & Fans','Santrifüj pompa','Centrifugal pump', ...
        'Helis redüktörlü motor','Helical geared motor','Po=Q·H·SG/(367·ηp) ; Mᴛ=9550·Po/n','Po=Q·H·SG/(367·ηp) ; Mᴛ=9550·Po/n',1.25,0.97, ...
        pumpVars(50,30,0.70,1450), @calc_pump);
    apps(end+1) = mkApp('recip','Pompa & Fan','Pumps & Fans','Pistonlu / pozitif deplasmanlı pompa','Reciprocating / PD pump', ...
        'Helis redüktörlü motor (darbe)','Helical geared motor (shock)','Po=Q·H·SG/(367·ηp) ; Mᴛ=9550·Po/n','Po=Q·H·SG/(367·ηp) ; Mᴛ=9550·Po/n',1.5,0.96, ...
        pumpVars(20,60,0.85,300), @calc_pump);

    apps(end+1) = mkApp('fan','Pompa & Fan','Pumps & Fans','Santrifüj fan / körük','Centrifugal fan / blower', ...
        'Helis redüktörlü motor','Helical geared motor','Po=(Q/3600)·Δp/(1000·ηf) ; Mᴛ=9550·Po/n','Po=(Q/3600)·Δp/(1000·ηf) ; Mᴛ=9550·Po/n',1.25,0.97, ...
        [mkVar('Q','Hava debisi Q','Air flow Q','m3/h',5000), mkVar('dp','Basınç artışı Δp','Pressure rise Δp','Pa',1000), ...
         mkVar('fe','Fan verimi ηf','Fan eff. ηf','',0.65), mkVar('n','Fan devri n','Fan speed n','rpm',1450)], @calc_fan);
end

function vars = specVars(dQ, dE, dn)
    vars = [mkVar('Q','Kapasite Q','Capacity Q','t/h',dQ), mkVar('E','Özgül enerji E','Specific energy E','kWh/t',dE), ...
            mkVar('n','Çıkış devri n','Output speed n','rpm',dn)];
end
function vars = pumpVars(dQ, dH, dpe, dn)
    vars = [mkVar('Q','Debi Q','Flow Q','m3/h',dQ), mkVar('H','Basma yüksekliği H','Head H','m',dH), ...
            mkVar('SG','Özgül ağırlık SG','Specific gravity SG','',1.0), mkVar('pe','Pompa verimi ηp','Pump eff. ηp','',dpe), ...
            mkVar('n','Pompa devri n','Pump speed n','rpm',dn)];
end

% ======================================================================
% Calculators — each returns s.MT, s.n, s.Pout (NaN if not set) and s.steps
% ======================================================================
function s = calc_belt_h(v)
    G=9.81; r=v.D/2000; MT=v.k*v.m*G*r; n=9.55*v.v/r;
    s.MT=MT; s.n=n; s.Pout=NaN;
    s.steps=[st('Tambur yarıçapı','Drum radius',r,'m'), st('Tambur momenti','Drum moment',MT,'Nm'), st('Tambur devri','Drum speed',n,'d/dk')];
end
function s = calc_belt_inc(v)
    G=9.81; r=v.D/2000; rad=v.a*pi/180; fac=cos(rad)+sin(rad); MT=v.k*fac*v.m*G*r; n=9.55*v.v/r;
    s.MT=MT; s.n=n; s.Pout=NaN;
    s.steps=[st('Tambur yarıçapı','Drum radius',r,'m'), st('Eğim faktörü','Incline factor',fac,''), ...
             st('Tambur momenti','Drum moment',MT,'Nm'), st('Tambur devri','Drum speed',n,'d/dk')];
end
function s = calc_screw(v)
    Qdk=v.Q/60; n=Qdk/v.Gk; pit=v.L/v.h; Qtop=v.Gk*pit; vel=v.h*n/1000; P=Qtop*vel/(60*75*1.36*v.ho);
    MT=NaN; if n>0, MT=9550*P/n; end
    s.MT=MT; s.n=n; s.Pout=P;
    s.steps=[st('Helezon devri','Screw speed',n,'d/dk'), st('Toplam yük','Total load',Qtop,'kg'), ...
             st('İlerleme hızı','Advance speed',vel,'m/dk'), st('Güç','Power',P,'kW')];
end
function s = calc_elevator(v)
    P=v.k*v.Q*v.H/367; D=v.D/1000; n=60*v.v/(pi*D); MT=NaN; if n>0, MT=9550*P/n; end
    s.MT=MT; s.n=n; s.Pout=P;
    s.steps=[st('Çıkış gücü','Output power',P,'kW'), st('Kafa tamburu devri','Head pulley speed',n,'d/dk'), st('Çıkış momenti','Output moment',MT,'Nm')];
end
function s = calc_chain(v)
    G=9.81; r=v.D/2000; MT=v.f*v.m*G*r; D=v.D/1000; n=v.v/(pi*D);
    s.MT=MT; s.n=n; s.Pout=NaN;
    s.steps=[st('Dişli yarıçapı','Sprocket radius',r,'m'), st('Çıkış momenti','Output moment',MT,'Nm'), st('Çıkış devri','Output speed',n,'d/dk')];
end
function s = calc_vib(v)
    w=2*pi*v.n/60; A=v.A/1000; P=v.k*v.m*A*A*w^3/1000; MT=NaN; if v.n>0, MT=9550*P/v.n; end
    s.MT=MT; s.n=v.n; s.Pout=P;
    s.steps=[st('Açısal hız','Angular speed',w,'rad/s'), st('Çıkış gücü','Output power',P,'kW'), st('Çıkış momenti','Output moment',MT,'Nm')];
end
function s = calc_hoist(v)
    G=9.81; r=v.D/2000; z=max(1,v.z); MT=v.m*G*r/z; vms=v.v/60; n=9.55*vms*z/r;
    s.MT=MT; s.n=n; s.Pout=NaN;
    s.steps=[st('Tambur yarıçapı','Drum radius',r,'m'), st('Palanga kat sayısı','Rope falls',z,''), ...
             st('Tambur momenti','Drum moment',MT,'Nm'), st('Tambur devri','Drum speed',n,'d/dk')];
end
function s = calc_pulley(v)
    G=9.81; r=v.D/2000; z=max(1,v.z); MT=v.m*G*r/z/v.re; vms=v.v/60; n=9.55*vms*z/r;
    s.MT=MT; s.n=n; s.Pout=NaN;
    s.steps=[st('Tambur yarıçapı','Drum radius',r,'m'), st('Tambur momenti','Drum moment',MT,'Nm'), st('Tambur devri','Drum speed',n,'d/dk')];
end
function s = calc_travel(v)
    G=9.81; MTkgm=v.Q*v.f + v.mu*v.Q*(v.d/2000); MT=MTkgm*G; n=60000*v.v/(pi*v.D);
    s.MT=MT; s.n=n; s.Pout=NaN;
    s.steps=[st('Tekerlek momenti','Wheel moment',MT,'Nm'), st('Tekerlek devri','Wheel speed',n,'d/dk')];
end
function s = calc_slew(v)
    J=v.m*v.r^2; w=2*pi*v.n/60; al=0; if v.t>0, al=w/v.t; end; MT=J*al+v.Tf;
    s.MT=MT; s.n=v.n; s.Pout=NaN;
    s.steps=[st('Atalet momenti','Inertia',J,'kg·m²'), st('Açısal ivme','Ang. accel',al,'rad/s²'), st('Çıkış momenti','Output moment',MT,'Nm')];
end
function s = calc_lift(v)
    G=9.81; F=v.Q*(1-v.b)*G; P=F*v.v/1000; D=v.D/1000; rf=max(1,v.rf); n=60*rf*v.v/(pi*D); MT=NaN; if n>0, MT=9550*P/n; end
    s.MT=MT; s.n=n; s.Pout=P;
    s.steps=[st('Dengesiz kuvvet','Out-of-balance force',F,'N'), st('Çıkış gücü','Output power',P,'kW'), st('Kasnak devri','Sheave speed',n,'d/dk')];
end
function s = calc_mixer_b(v)
    rd=v.Dd/2000; bb=v.b/1000; rho=v.ro*1000;
    blade=@(k) (k>0)*rd*bb*(k/1000)*rho*10;
    M1=blade(v.k1); M2=blade(v.k2); M3=blade(v.k3); MT=M1+M2+M3;
    s.MT=MT; s.n=v.n; s.Pout=NaN;
    s.steps=[st('1. kanat momenti','Blade-1 moment',M1,'Nm'), st('2. kanat momenti','Blade-2 moment',M2,'Nm'), ...
             st('3. kanat momenti','Blade-3 moment',M3,'Nm'), st('Toplam moment','Total moment',MT,'Nm')];
end
function s = calc_mixer_np(v)
    N=v.n/60; D=v.D/1000; P=v.Np*v.ro*N^3*D^5/1000; MT=NaN; if v.n>0, MT=9550*P/v.n; end
    s.MT=MT; s.n=v.n; s.Pout=P;
    s.steps=[st('Devir (1/s)','Rev/s',N,'1/s'), st('Çıkış gücü','Output power',P,'kW'), st('Çıkış momenti','Output moment',MT,'Nm')];
end
function s = calc_kiln(v)
    G=9.81; D=v.D/1000; MT=(1+v.k/100)*v.m*G*(D/2)*v.e;
    s.MT=MT; s.n=v.n; s.Pout=NaN;
    s.steps=st('Çıkış momenti','Output moment',MT,'Nm');
end
function s = calc_extruder(v)
    P=v.SME*v.Q; MT=NaN; if v.n>0, MT=9550*P/v.n; end
    s.MT=MT; s.n=v.n; s.Pout=P;
    s.steps=[st('Çıkış gücü','Output power',P,'kW'), st('Çıkış momenti','Output moment',MT,'Nm')];
end
function s = calc_specE(v)
    P=v.E*v.Q; MT=NaN; if v.n>0, MT=9550*P/v.n; end
    s.MT=MT; s.n=v.n; s.Pout=P;
    s.steps=[st('Çıkış gücü','Output power',P,'kW'), st('Çıkış momenti','Output moment',MT,'Nm')];
end
function s = calc_ball(v)
    E=10*v.Wi*(1/sqrt(v.Pp)-1/sqrt(v.F)); P=E*v.Q; MT=NaN; if v.n>0, MT=9550*P/v.n; end
    s.MT=MT; s.n=v.n; s.Pout=P;
    s.steps=[st('Özgül enerji (Bond)','Specific energy (Bond)',E,'kWh/t'), st('Çıkış gücü','Output power',P,'kW'), st('Çıkış momenti','Output moment',MT,'Nm')];
end
function s = calc_sifter(v)
    w=2*pi*v.n/60; r=v.r/1000; P=v.k*v.m*r*r*w^3/1000; MT=NaN; if v.n>0, MT=9550*P/v.n; end
    s.MT=MT; s.n=v.n; s.Pout=P;
    s.steps=[st('Açısal hız','Angular speed',w,'rad/s'), st('Çıkış gücü','Output power',P,'kW'), st('Çıkış momenti','Output moment',MT,'Nm')];
end
function s = calc_rotable(v)
    r=v.r/1000; J=0.5*v.m*r*r; w=2*pi*v.n/60; al=0; if v.t>0, al=w/v.t; end; MT=J*al+v.Tf;
    s.MT=MT; s.n=v.n; s.Pout=NaN;
    s.steps=[st('Atalet momenti','Inertia',J,'kg·m²'), st('Açısal ivme','Ang. accel',al,'rad/s²'), st('Çıkış momenti','Output moment',MT,'Nm')];
end
function s = calc_pump(v)
    P=NaN; if v.pe>0, P=v.Q*v.H*v.SG/(367*v.pe); end; MT=NaN; if v.n>0, MT=9550*P/v.n; end
    s.MT=MT; s.n=v.n; s.Pout=P;
    s.steps=[st('Çıkış gücü','Output power',P,'kW'), st('Çıkış momenti','Output moment',MT,'Nm')];
end
function s = calc_fan(v)
    P=NaN; if v.fe>0, P=(v.Q/3600)*v.dp/1000/v.fe; end; MT=NaN; if v.n>0, MT=9550*P/v.n; end
    s.MT=MT; s.n=v.n; s.Pout=P;
    s.steps=[st('Çıkış gücü','Output power',P,'kW'), st('Çıkış momenti','Output moment',MT,'Nm')];
end

% ======================================================================
function printResult(a, r, lang)
    en = strcmp(lang, 'en');
    H = @(tr, e) ternary(en, e, tr);
    fprintf('\n%s  |  %s\n', pick(a.grpTR, a.grpEN, lang), r.series);
    fprintf('>> %s\n', r.name);
    fprintf('%s: %s\n\n', H('Formül','Formula'), r.formula);
    fprintf('  %s\n', H('HESAP ADIMLARI','CALCULATION STEPS'));
    for i = 1:numel(r.steps)
        sp = r.steps(i);
        fprintf('   %-26s = %s %s\n', pick(sp.tr, sp.en, lang), fmtn(sp.val), sp.u);
    end
    fprintf('   %-26s = %.2f kW -> %s kW\n', H('Motor gücü','Motor power'), r.Pmotor, fmtn(r.motor_kW));
    fprintf('   %-26s = %s Nm\n', H('Gerekli nominal moment','Required nominal moment'), sprintf('%.0f', r.Mn));
    fprintf('\n  %s\n', H('SONUÇ','RESULT'));
    fprintf('   %-28s %s Nm\n', H('Gerekli nominal moment Mn','Required nominal moment Mn'), sprintf('%.0f', r.Mn));
    fprintf('   %-28s %s Nm\n', H('Çıkış momenti Mt','Output moment Mt'), sprintf('%.0f', r.MT));
    fprintf('   %-28s %s d/dk\n', H('Çıkış devri n','Output speed n'), fmtn(r.n));
    fprintf('   %-28s %.1f :1\n', H('Tahvil i','Ratio i'), r.ratio);
    fprintf('   %-28s %s kW\n', H('Motor gücü','Motor power'), fmtn(r.motor_kW));
    fprintf('   %-28s %.2f\n', H('Servis faktörü Sf','Service factor Sf'), r.sf);
    fprintf('\n');
end

function y = ternary(cond, a, b)
    if cond, y = a; else, y = b; end
end

function interactive(apps, lang)
    en = strcmp(lang, 'en');
    fprintf('\n=== %s ===\n', ternary(en, 'I-MAK GEARBOX SELECTOR', 'İ-MAK REDÜKTÖR SEÇİCİ'));
    lastG = '';
    for i = 1:numel(apps)
        g = pick(apps(i).grpTR, apps(i).grpEN, lang);
        if ~strcmp(g, lastG), fprintf('\n  %s\n', g); lastG = g; end
        fprintf('   %2d) %s\n', i, pick(apps(i).nameTR, apps(i).nameEN, lang));
    end
    sel = str2double(input(sprintf('\n%s: ', ternary(en,'Number','Numara')), 's'));
    if isnan(sel) || sel < 1 || sel > numel(apps), fprintf('Invalid.\n'); return; end
    a = apps(round(sel));
    v = struct();
    fprintf('\n%s (Enter = %s):\n', pick(a.nameTR,a.nameEN,lang), ternary(en,'default','varsayılan'));
    for i = 1:numel(a.vars)
        vr = a.vars(i);
        raw = input(sprintf('  %s [%g]: ', pick(vr.tr,vr.en,lang), vr.def), 's');
        if isempty(raw), v.(vr.id) = vr.def; else
            x = str2double(strrep(raw, ',', '.')); if isnan(x), x = vr.def; end; v.(vr.id) = x;
        end
    end
    v.n1  = askNum('Motor devri n1','Motor speed n1',1450,en);
    v.eta = askNum('Reduktor verimi eta','Gearbox efficiency eta',a.eta,en);
    v.sf  = askNum('Servis faktoru Sf','Service factor Sf',a.sf,en);
    r = computeResult(a, v, v.n1, v.eta, v.sf, lang);
    printResult(a, r, lang);
end

function val = askNum(tr, en, def, isen)
    if isen, p = en; else, p = tr; end
    raw = input(sprintf('  %s [%g]: ', p, def), 's');
    if isempty(raw), val = def; else
        val = str2double(strrep(raw, ',', '.')); if isnan(val), val = def; end
    end
end
