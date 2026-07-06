(function(){
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
})();
