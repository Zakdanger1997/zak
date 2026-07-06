#!/usr/bin/env python3
"""Single self-contained file: 3D hero intro + full per-application selector in ONE
page. The 'Open app' button switches views in-page (no navigation between files)."""
import pathlib
HERE = pathlib.Path(__file__).parent
OUT  = pathlib.Path("/home/user/zak/gearbox-selector")
LOGO  = (HERE/"logo.txt").read_text().strip()
THREE = (HERE/"three.min.js").read_text()
ORBIT = (HERE/"OrbitControls.js").read_text()
ENGINE = (HERE/"engine2.js").read_text().replace("</script>\n</body>\n</html>", "").strip()
# in the combined file the hero owns id="tagline"; the selector header uses id="tagline2"
ENGINE = ENGINE.replace('$("tagline")', '$("tagline2")')

# ---------- selector CSS (responsive: desktop + phone) ----------
CSS_SELECTOR = '''
  :root{--bg:#16191d;--panel:#1e2228;--panel2:#262b32;--line:#333a43;--ink:#eceef1;--muted:#8b939e;--red:#e11d13;--amber:#f0a726;--green:#35c98b;--mono:ui-monospace,"SF Mono","Cascadia Mono",Menlo,Consolas,monospace;--sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
  *{box-sizing:border-box}html,body{margin:0}
  html.hero-open,html.hero-open body{overflow:hidden;height:100%}
  body{background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.45;-webkit-font-smoothing:antialiased;padding-bottom:92px}
  .wrap{max-width:1120px;margin:0 auto;padding:0 16px}
  header.top{border-bottom:1px solid var(--line);background:linear-gradient(#1c2026,#181b20)}
  .topbar{display:flex;align-items:center;gap:14px;padding:12px 0}
  .brand{display:flex;align-items:center;gap:12px}
  .logo-badge{display:inline-flex;background:#fff;border-radius:6px;padding:5px 9px;line-height:0;box-shadow:0 1px 0 rgba(0,0,0,.35)}
  .logo-badge img{height:28px;width:auto;display:block}
  .brand-title{font-size:18px;font-weight:700;letter-spacing:.3px;padding-left:12px;border-left:1px solid var(--line)}
  .headright{margin-left:auto;display:flex;align-items:center;gap:12px}
  .homebtn{background:var(--panel2);color:var(--muted);border:1px solid var(--line);border-radius:7px;padding:8px 11px;font:700 13px var(--sans);cursor:pointer}
  .homebtn:hover{color:var(--ink)}
  .tagline{color:var(--muted);font-size:12px;letter-spacing:.3px;text-align:right;max-width:230px}
  .langtog{display:flex;border:1px solid var(--line);border-radius:7px;overflow:hidden}
  .langtog button{background:var(--panel2);color:var(--muted);border:0;padding:8px 13px;font:700 13px var(--sans);cursor:pointer}
  .langtog button.on{background:var(--red);color:#fff}
  .apppick{padding:18px 0 4px}
  label.f{display:block;margin:0 0 12px}
  label.f .lab{display:block;font-size:11.5px;letter-spacing:.5px;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
  select,input[type=number]{width:100%;background:var(--panel2);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:10px 12px;font-size:15px;font-family:var(--sans)}
  input[type=number]{font-family:var(--mono)}
  select:focus,input:focus{outline:2px solid var(--red);border-color:var(--red)}
  #appSel{font-size:16px;font-weight:600;padding:12px}
  .apppage{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin-bottom:16px}
  .apphead{display:flex;align-items:flex-start;gap:14px;border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:14px}
  .appgroup{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--red);font-weight:700}
  .apptitle{margin:3px 0 0;font-size:22px;font-weight:700}
  .series{margin-left:auto;text-align:right;font-size:12.5px;color:var(--muted);background:var(--panel2);border:1px solid var(--line);border-left:3px solid var(--green);border-radius:6px;padding:8px 11px;max-width:260px}
  .dfrow{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
  .box{background:var(--panel2);border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin-bottom:12px}
  .boxk{font-size:10.5px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);font-weight:700;margin-bottom:10px}
  .diagbox{margin-bottom:0}.formbox{margin-bottom:0;display:flex;flex-direction:column}
  .dia{height:130px;display:grid;place-items:center}.dia svg{max-height:130px}
  .formulaBox{font-family:var(--mono);font-size:13px;color:var(--ink);background:#12151a;border:1px solid var(--line);border-radius:6px;padding:12px;line-height:1.7;flex:1;display:flex;align-items:center}
  .inputs{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}.inputs label.f{margin-bottom:0}
  .steps{display:flex;flex-direction:column}
  .step{display:flex;gap:12px;padding:8px 2px;border-bottom:1px dashed var(--line);font-size:13px}.step:last-child{border-bottom:0}
  .step .sl{flex:0 0 40%;color:var(--muted)}.step .se{flex:1;font-family:var(--mono);font-size:12.5px}.step .se b{color:var(--ink)}
  .resultbox{background:linear-gradient(#20252c,#191d22)}
  .metrics{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:var(--line);border:1px solid var(--line);border-radius:8px;overflow:hidden}
  .metrics .m{background:var(--panel);padding:12px 14px}
  .metrics .m.red{background:#241a1a;border-left:3px solid var(--red)}
  .metrics .m .k{font-size:10px;letter-spacing:.6px;text-transform:uppercase;color:var(--muted)}
  .metrics .m .v{font-family:var(--mono);font-size:21px;margin-top:4px}.metrics .m .v small{font-size:12px;color:var(--muted)}
  .rec{margin-top:12px;border:1px solid var(--line);border-left:3px solid var(--green);border-radius:6px;padding:11px 13px;background:var(--panel2)}
  .rec .k{font-size:10.5px;letter-spacing:.8px;text-transform:uppercase;color:var(--green);font-weight:700;margin-bottom:4px}.recline{font-size:13.5px}
  .disclaimer{font-size:11.5px;color:var(--muted);padding:2px 0 24px;text-align:center;line-height:1.6}
  .actionbar{position:fixed;left:0;right:0;bottom:0;background:#14171b;border-top:1px solid var(--line);z-index:20}
  .actionbar .inner{max-width:1120px;margin:0 auto;padding:12px 16px;display:flex;gap:10px}
  .btn{flex:1;border:1px solid var(--line);background:var(--panel2);color:var(--ink);padding:12px;border-radius:7px;font:600 14px var(--sans);cursor:pointer}
  .btn.primary{background:var(--red);border-color:var(--red);color:#fff}.btn.ghost{flex:0 0 auto}
  @media(max-width:820px){
    .dfrow{grid-template-columns:1fr}.inputs{grid-template-columns:1fr 1fr}.metrics{grid-template-columns:1fr 1fr}
    .apphead{flex-direction:column;gap:8px}.series{margin-left:0;text-align:left;max-width:none}.apptitle{font-size:19px}
    .step{flex-direction:column;gap:2px}.step .sl{flex:none}
    select,input[type=number]{font-size:16px;min-height:46px}
    .brand-title{font-size:15px}.tagline{display:none}
  }
  @media print{body{background:#fff;color:#000;padding:0}.actionbar,.tagline,.langtog,.homebtn{display:none}.apppage,.box,.metrics .m,.rec,.formulaBox{border-color:#ccc;background:#fff!important}}
'''

# ---------- hero CSS (scoped under #hero3d) ----------
CSS_HERO = '''
  #hero3d{position:fixed;inset:0;z-index:100;display:flex;flex-direction:column;background:#14171b}
  #hero3d #c{position:absolute;inset:0;width:100%;height:100%;display:block;touch-action:none}
  #hero3d .ui{position:absolute;inset:0;pointer-events:none;display:flex;flex-direction:column}
  #hero3d .htop{display:flex;align-items:center;gap:12px;padding:16px 18px}
  #hero3d .hlogo{background:#fff;border-radius:7px;padding:6px 10px;line-height:0;box-shadow:0 2px 10px rgba(0,0,0,.5);pointer-events:auto}
  #hero3d .hlogo img{height:30px;display:block}
  #hero3d .hbrand{font-size:18px;font-weight:700;letter-spacing:.3px;padding-left:12px;border-left:1px solid #333a43;text-shadow:0 1px 6px #000;color:#eceef1}
  #hero3d .hlang{margin-left:auto;display:flex;border:1px solid #333a43;border-radius:8px;overflow:hidden;pointer-events:auto}
  #hero3d .hlang button{background:rgba(38,43,50,.7);color:#9aa2ad;border:0;padding:8px 14px;font:700 13px system-ui;cursor:pointer}
  #hero3d .hlang button.on{background:#e11d13;color:#fff}
  #hero3d .hspace{flex:1}
  #hero3d .hero{padding:0 18px 42px;max-width:640px}
  #hero3d .hero h1{margin:0 0 6px;font-size:clamp(30px,7vw,54px);font-weight:800;letter-spacing:-1px;line-height:1;text-shadow:0 3px 18px #000;color:#eceef1}
  #hero3d .hero h1 .r{color:#e11d13}
  #hero3d #tagline{color:#d6dae0;font-size:clamp(14px,3.4vw,19px);margin-bottom:22px;text-shadow:0 2px 10px #000}
  #hero3d .hbtn{pointer-events:auto;border:1px solid #333a43;background:#e11d13;border-color:#e11d13;color:#fff;padding:15px 24px;border-radius:11px;font:800 16px system-ui;cursor:pointer;box-shadow:0 8px 26px rgba(225,29,19,.4);transition:transform .12s}
  #hero3d .hbtn:hover{transform:translateY(-2px)}
  #hero3d #hint{position:absolute;left:0;right:0;bottom:12px;text-align:center;color:#9aa2ad;font-size:12px;pointer-events:none;text-shadow:0 1px 6px #000}
'''

# ---------- hero markup ----------
BODY_HERO = '''<div id="hero3d">
  <canvas id="c"></canvas>
  <div class="ui">
    <div class="htop">
      <span class="hlogo"><img src="__LOGO__" alt="I-MAK"></span>
      <span class="hbrand">Redüktör Seçici</span>
      <span class="hlang"><button id="lt" class="on">TR</button><button id="le">EN</button></span>
    </div>
    <div class="hspace"></div>
    <div class="hero">
      <h1>İ-MAK <span class="r">3B</span><br>Redüktör</h1>
      <div id="tagline"></div>
      <button class="hbtn" id="btnOpen"></button>
    </div>
  </div>
  <div id="hint"></div>
</div>'''

# ---------- selector markup ----------
BODY_APP = '''<div id="marker"></div>
<header class="top"><div class="wrap topbar">
  <div class="brand"><span class="logo-badge"><img src="__LOGO__" alt="I-MAK"></span><span class="brand-title">Redüktör Seçici</span></div>
  <div class="headright">
    <button class="homebtn" id="btnHome" title="3B">◱ 3B</button>
    <div class="langtog"><button id="btnLangTr" class="on">TR</button><button id="btnLangEn">EN</button></div>
    <div class="tagline" id="tagline2"></div>
  </div>
</div></header>
<main class="wrap">
  <div class="apppick"><label class="f"><span class="lab" id="lblApp">Uygulama</span><select id="appSel"></select></label></div>
  <section class="apppage">
    <div class="apphead">
      <div><div class="appgroup" id="appGroup"></div><h1 class="apptitle" id="appTitle"></h1></div>
      <div class="series"><span id="appSeries"></span></div>
    </div>
    <div class="dfrow">
      <div class="box diagbox"><div class="boxk" id="lblDiagram">Şema</div><div class="dia" id="dia"></div></div>
      <div class="box formbox"><div class="boxk" id="lblFormula">Formül</div><div class="formulaBox" id="formulaBox"></div></div>
    </div>
    <div class="box"><div class="boxk" id="lblInputs">Girdiler</div><div class="inputs" id="inputs"></div></div>
    <div class="box"><div class="boxk" id="lblSteps">Hesap adımları</div><div class="steps" id="steps"></div></div>
    <div class="box resultbox"><div class="boxk" id="lblResult">Sonuç</div>
      <div class="metrics">
        <div class="m red"><div class="k" id="lblMn">Gerekli nominal moment</div><div class="v" id="rMn">—</div></div>
        <div class="m"><div class="k" id="lblMT">Çıkış momenti</div><div class="v" id="rMT">—</div></div>
        <div class="m"><div class="k" id="lblN">Çıkış devri</div><div class="v" id="rn">—</div></div>
        <div class="m"><div class="k" id="lblI">Tahvil</div><div class="v" id="ri">—</div></div>
        <div class="m"><div class="k" id="lblP">Motor gücü</div><div class="v" id="rP">—</div></div>
        <div class="m"><div class="k" id="lblSf">Servis faktörü</div><div class="v" id="rSf">—</div></div>
      </div>
      <div class="rec"><div class="k" id="lblRec">Önerilen İ-MAK ürünü</div><div class="recline" id="recLine"></div></div>
    </div>
  </section>
  <p class="disclaimer" id="disc"></p>
</main>
<div class="actionbar"><div class="inner">
  <button class="btn primary" id="copyBtn"></button>
  <button class="btn" id="printBtn"></button>
  <button class="btn ghost" id="resetBtn"></button>
</div></div>'''

# ---------- hero scene JS (IIFE so it can't collide with the selector engine) ----------
HERO_JS = r'''(function(){
  const canvas=document.getElementById('c');
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.setSize(innerWidth,innerHeight);
  renderer.outputEncoding=THREE.sRGBEncoding; renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.05;
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x14171b); scene.fog=new THREE.Fog(0x14171b,24,52);
  const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,0.1,200); camera.position.set(1,5,21);
  const controls=new THREE.OrbitControls(camera,renderer.domElement);
  controls.enableDamping=true; controls.dampingFactor=0.08; controls.autoRotate=true; controls.autoRotateSpeed=0.9;
  controls.minDistance=11; controls.maxDistance=38; controls.enablePan=false; controls.minPolarAngle=0.7; controls.maxPolarAngle=2.2; controls.target.set(0,0.4,0);
  scene.add(new THREE.HemisphereLight(0xcbd8ff,0x090b0e,0.6));
  const key=new THREE.DirectionalLight(0xffffff,1.15); key.position.set(9,13,11); scene.add(key);
  const rim=new THREE.PointLight(0xe11d13,1.1,70); rim.position.set(-12,5,-7); scene.add(rim);
  const fill=new THREE.DirectionalLight(0x8aa6ff,0.35); fill.position.set(-7,-5,9); scene.add(fill);
  function gearGeom(teeth,m,th){const pitch=m*teeth/2,add=0.9*m,ded=1.15*m,rt=pitch+add,rr=pitch-ded;
    const s=new THREE.Shape(),ta=2*Math.PI/teeth;
    for(let i=0;i<teeth;i++){const a=i*ta;const p=(r,ang,f)=>{const x=r*Math.cos(ang),y=r*Math.sin(ang);(i===0&&f)?s.moveTo(x,y):s.lineTo(x,y);};
      p(rr,a,true);p(rr,a+ta*0.05);p(rt,a+ta*0.22);p(rt,a+ta*0.30);p(rr,a+ta*0.47);p(rr,a+ta*0.5);}
    s.closePath();const h=new THREE.Path();h.absarc(0,0,pitch*0.30,0,Math.PI*2,true);s.holes.push(h);
    const g=new THREE.ExtrudeGeometry(s,{depth:th,bevelEnabled:true,bevelThickness:0.06,bevelSize:0.06,bevelSegments:2,steps:1,curveSegments:20});g.center();return g;}
  const mat=(c,r)=>new THREE.MeshStandardMaterial({color:c,metalness:0.88,roughness:r||0.34});
  const RED=0xe11d13,STEEL=0xc4ccd6,DARK=0x2b3038,asm=new THREE.Group(),m=0.5,th=1.5;
  const defs=[{t:30,c:RED},{t:19,c:STEEL,extra:0.35},{t:13,c:RED}];let px=0,pp=0;const gears=[];
  defs.forEach((d,i)=>{const pitch=m*d.t/2; if(i>0)px+=pp+pitch;
    const mesh=new THREE.Mesh(gearGeom(d.t,m,th+(d.extra||0)),mat(d.c)); mesh.position.x=px;
    const ta=2*Math.PI/d.t; mesh.rotation.z=(i%2?ta/2:0); mesh.userData={t:d.t,dir:(i%2?-1:1)}; gears.push(mesh); asm.add(mesh);
    const shaft=new THREE.Mesh(new THREE.CylinderGeometry(pitch*0.17,pitch*0.17,th*2.6,22),mat(DARK,0.6)); shaft.rotation.x=Math.PI/2; shaft.position.set(px,0,0); asm.add(shaft);
    const hub=new THREE.Mesh(new THREE.CylinderGeometry(pitch*0.34,pitch*0.34,th+0.4,26),mat(d.c===RED?0xb3170f:0x9aa2ac,0.5)); hub.rotation.x=Math.PI/2; hub.position.set(px,0,0); hub.userData={follow:mesh}; asm.add(hub);
    pp=pitch;});
  asm.position.x=-gears[1].position.x; asm.rotation.set(-0.52,0,0.1); scene.add(asm);
  const plate=new THREE.Mesh(new THREE.CircleGeometry(15,64),new THREE.MeshStandardMaterial({color:0x191d23,metalness:0.35,roughness:0.92})); plate.position.z=-3.4; scene.add(plate);
  function spin(){gears.forEach(g=>{g.rotation.z+=0.011*g.userData.dir*(19/g.userData.t);}); asm.children.forEach(o=>{if(o.userData&&o.userData.follow)o.rotation.z=o.userData.follow.rotation.z;});}
  let heroOn=true;
  function resize(){camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);}
  addEventListener('resize',resize);
  (function loop(){requestAnimationFrame(loop); if(!heroOn)return; spin(); controls.update(); renderer.render(scene,camera);})();
  const TXT={tagline:{tr:"Uygulamaya özel redüktör seçimi",en:"Per-application gearbox selection"},
    open:{tr:"Uygulamayı aç  →",en:"Open the app  →"}, hint:{tr:"3B modeli döndürmek için sürükleyin · yakınlaştırmak için tekerlek",en:"Drag to rotate · scroll to zoom"}};
  let hlang='tr';
  function hApply(){document.getElementById('tagline').textContent=TXT.tagline[hlang];
    document.getElementById('btnOpen').textContent=TXT.open[hlang];
    document.getElementById('hint').textContent=TXT.hint[hlang];
    document.getElementById('lt').classList.toggle('on',hlang==='tr');
    document.getElementById('le').classList.toggle('on',hlang==='en');}
  document.getElementById('lt').onclick=()=>{hlang='tr';hApply();};
  document.getElementById('le').onclick=()=>{hlang='en';hApply();};
  hApply();
  const hero=document.getElementById('hero3d');
  function show(){heroOn=true;hero.style.display='flex';document.documentElement.classList.add('hero-open');resize();}
  function hide(){heroOn=false;hero.style.display='none';document.documentElement.classList.remove('hero-open');window.scrollTo(0,0);}
  document.getElementById('btnOpen').onclick=hide;
  const home=document.getElementById('btnHome'); if(home) home.onclick=show;
})();'''

HTML = ('<!DOCTYPE html>\n<html lang="tr" class="hero-open">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">\n'
        '<meta name="theme-color" content="#14171b">\n<title>İ-MAK Redüktör Seçici — 3B</title>\n'
        '<style>' + CSS_SELECTOR + CSS_HERO + '</style>\n</head>\n<body>\n'
        + BODY_HERO + '\n' + BODY_APP + '\n'
        + '<script>' + THREE + '</script>\n'
        + '<script>' + ORBIT + '</script>\n'
        + '<script>' + HERO_JS + '</script>\n'
        + '<script>' + ENGINE + '</script>\n'
        + '</body>\n</html>\n')
HTML = HTML.replace("__LOGO__", LOGO)

(OUT/"imak-reduktor-secici-3d.html").write_text(HTML, encoding="utf-8")
print("wrote", OUT/"imak-reduktor-secici-3d.html", f"({len(HTML):,} bytes)")
