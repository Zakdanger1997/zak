// ============================================================================
//  İ-MAK Redüktör Seçici  /  I-MAK Gearbox Selector   —   C++ console version
//  Per-application sizing: same 26 applications & formulas as the web app.
//  Formula sources: İ-MAK ArGe Teknik Eğitim Sunumu + standard drive engineering.
//  Build:  g++ -std=c++17 -O2 -o imak_reduktor imak_reduktor.cpp
//  Run:    ./imak_reduktor
// ============================================================================
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <map>
#include <functional>
#include <cmath>
#include <sstream>
#include <algorithm>
#include <limits>

static const double G = 9.81;
static int LANG = 0;                       // 0 = TR, 1 = EN
static std::string T(const std::string& tr, const std::string& en){ return LANG ? en : tr; }

// ---- standard IEC motor sizes (kW); pick the first >= required power ----
static const std::vector<double> IEC = {0.12,0.18,0.25,0.37,0.55,0.75,1.1,1.5,2.2,3,4,5.5,
    7.5,11,15,18.5,22,30,37,45,55,75,90,110,132,160,200,250,315,355};
static double iecUp(double p){ for(double s:IEC) if(s>=p-1e-9) return s; return IEC.back(); }

// ---- number formatting: trim trailing zeros, TR uses comma as decimal mark ----
static std::string num(double x, int dec=2){
    if(!std::isfinite(x)) return "-";
    std::ostringstream os; os<<std::fixed<<std::setprecision(dec)<<x;
    std::string s=os.str();
    if(s.find('.')!=std::string::npos){
        while(s.back()=='0') s.pop_back();
        if(s.back()=='.') s.pop_back();
    }
    if(LANG==0) std::replace(s.begin(), s.end(), '.', ',');   // Turkish decimal comma
    return s;
}
static std::string autor(double x){ // auto decimals by magnitude
    double a=std::fabs(x);
    int d = a<10?2 : a<100?1 : 0;
    return num(x,d);
}

// ---------------------------------------------------------------------------
struct Var  { std::string id, tr, en, unit; double def; };
struct Step { std::string tr, en, expr; double res; std::string unit; };
struct Res  { double MT=std::nan(""), n=std::nan(""), Pout=std::nan(""); std::vector<Step> steps; };
struct App {
    std::string id, grpTR, grpEN, nameTR, nameEN, serTR, serEN, fTR, fEN;
    double sf, eta;
    std::vector<Var> vars;
    std::function<Res(std::map<std::string,double>&)> calc;
};

static Var V(std::string id,std::string tr,std::string en,std::string u,double def){ return {id,tr,en,u,def}; }
static Step ST(std::string tr,std::string en,std::string expr,double res,std::string u){ return {tr,en,expr,res,u}; }

// convenience for building expression strings
static std::string E(std::initializer_list<std::string> parts){ std::string s; for(auto&p:parts)s+=p; return s; }

std::vector<App> build_apps(){
    std::vector<App> A;
    auto PI = M_PI;

    // ---------- Konveyör & Taşıma ----------
    A.push_back({"belt_h","Konveyör & Taşıma","Conveying & Handling","Bantlı konveyör — yatay","Belt conveyor — horizontal",
      "İRK Serisi (helis-konik)","İRK series (helical-bevel)",
      "Mᴛ = k·m·g·r ; n = 9,55·v/r ; Pm = Mᴛ·n/(9550·η)","Mᴛ = k·m·g·r ; n = 9.55·v/r ; Pm = Mᴛ·n/(9550·η)",
      1.25,0.96,
      {V("m","Yük kütlesi m","Load mass m","kg",10000),V("D","Tambur çapı Ø","Drum Ø","mm",250),
       V("v","Bant hızı v","Belt speed v","m/s",1.0),V("k","Sürtünme katsayısı k","Friction coeff. k","",0.125)},
      [](std::map<std::string,double>&v){Res r;double rr=v["D"]/2000;double MT=v["k"]*v["m"]*G*rr;double n=9.55*v["v"]/rr;
        r.MT=MT;r.n=n;r.steps={ST("Tambur yarıçapı","Drum radius","r=D/2000",rr,"m"),
        ST("Tambur momenti","Drum moment","Mᴛ=k·m·g·r",MT,"Nm"),ST("Tambur devri","Drum speed","n=9,55·v/r",n,"d/dk")};return r;}});

    A.push_back({"belt_inc","Konveyör & Taşıma","Conveying & Handling","Bantlı konveyör — eğimli","Belt conveyor — inclined",
      "İRK Serisi (helis-konik)","İRK series (helical-bevel)",
      "Mᴛ = k·(cosα+sinα)·m·g·r ; n = 9,55·v/r","Mᴛ = k·(cosα+sinα)·m·g·r ; n = 9.55·v/r",
      1.25,0.96,
      {V("m","Yük kütlesi m","Load mass m","kg",10000),V("D","Tambur çapı Ø","Drum Ø","mm",250),
       V("v","Bant hızı v","Belt speed v","m/s",1.0),V("a","Eğim α","Incline α","deg",25),V("k","Sürtünme katsayısı k","Friction coeff. k","",0.125)},
      [](std::map<std::string,double>&v){Res r;double rr=v["D"]/2000;double rad=v["a"]*M_PI/180;double fac=std::cos(rad)+std::sin(rad);
        double MT=v["k"]*fac*v["m"]*G*rr;double n=9.55*v["v"]/rr;r.MT=MT;r.n=n;
        r.steps={ST("Tambur yarıçapı","Drum radius","r=D/2000",rr,"m"),ST("Eğim faktörü","Incline factor","cosα+sinα",fac,""),
        ST("Tambur momenti","Drum moment","Mᴛ=k·(cosα+sinα)·m·g·r",MT,"Nm"),ST("Tambur devri","Drum speed","n=9,55·v/r",n,"d/dk")};return r;}});

    A.push_back({"screw","Konveyör & Taşıma","Conveying & Handling","Helezon (vidalı) konveyör","Screw (auger) conveyor",
      "Helis redüktörlü motor","Helical geared motor",
      "n=(Q/60)/G ; Qₜₒₚ=G·(L/h) ; v=h·n/1000 ; Pₘ=Qₜₒₚ·v/(60·75·1,36·η)","n=(Q/60)/G ; Qₜₒₜ=G·(L/h) ; v=h·n/1000 ; Pₘ=Qₜₒₜ·v/(60·75·1.36·η)",
      1.25,0.96,
      {V("Q","Kapasite Q","Capacity Q","kg/h",8000),V("Gk","Hatve yükü G","Load per pitch G","kg",100),
       V("L","Uzunluk L","Length L","mm",3000),V("h","Hatve h","Pitch h","mm",300),V("ho","Yükleme verimi","Loading eff.","",0.30)},
      [](std::map<std::string,double>&v){Res r;double Qdk=v["Q"]/60;double n=Qdk/v["Gk"];double pit=v["L"]/v["h"];
        double Qtop=v["Gk"]*pit;double vel=v["h"]*n/1000;double P=Qtop*vel/(60*75*1.36*v["ho"]);double MT=n>0?9550*P/n:std::nan("");
        r.MT=MT;r.n=n;r.Pout=P;r.steps={ST("Helezon devri","Screw speed","n=(Q/60)/G",n,"d/dk"),
        ST("Toplam yük","Total load","Qₜₒₚ=G·(L/h)",Qtop,"kg"),ST("İlerleme hızı","Advance speed","v=h·n/1000",vel,"m/dk"),
        ST("Güç","Power","Pₘ=Qₜₒₚ·v/(60·75·1,36·η)",P,"kW")};return r;}});

    A.push_back({"elevator","Konveyör & Taşıma","Conveying & Handling","Kovalı elevatör","Bucket elevator",
      "Helis-konik + geri dönüşsüz","Helical-bevel + backstop","Pₒ=k·Q·H/367 ; n=60·v/(π·D)","Pₒ=k·Q·H/367 ; n=60·v/(π·D)",
      1.4,0.96,
      {V("Q","Kapasite Q","Capacity Q","t/h",50),V("H","Kaldırma yüksekliği H","Lift height H","m",20),
       V("v","Hız v","Speed v","m/s",1.5),V("D","Kafa tamburu Ø","Head pulley Ø","mm",500),V("k","Dolum faktörü k","Fill factor k","",1.25)},
      [](std::map<std::string,double>&v){Res r;double P=v["k"]*v["Q"]*v["H"]/367;double D=v["D"]/1000;double n=60*v["v"]/(M_PI*D);
        double MT=n>0?9550*P/n:std::nan("");r.MT=MT;r.n=n;r.Pout=P;
        r.steps={ST("Çıkış gücü","Output power","Pₒ=k·Q·H/367",P,"kW"),ST("Kafa tamburu devri","Head pulley speed","n=60·v/(π·D)",n,"d/dk"),
        ST("Çıkış momenti","Output moment","Mᴛ=9550·Pₒ/n",MT,"Nm")};return r;}});

    A.push_back({"chain","Konveyör & Taşıma","Conveying & Handling","Zincirli / sıyırıcı konveyör","Chain / drag conveyor",
      "İRK Serisi (helis-konik)","İRK series (helical-bevel)","Mᴛ=f·m·g·r ; n=v/(π·D)","Mᴛ=f·m·g·r ; n=v/(π·D)",
      1.5,0.95,
      {V("m","Hareketli kütle m","Moving mass m","kg",8000),V("D","Zincir dişlisi Ø","Sprocket Ø","mm",250),
       V("v","Zincir hızı v","Chain speed v","m/min",20),V("f","Sürtünme katsayısı f","Friction coeff. f","",0.30)},
      [](std::map<std::string,double>&v){Res r;double rr=v["D"]/2000;double MT=v["f"]*v["m"]*G*rr;double D=v["D"]/1000;double n=v["v"]/(M_PI*D);
        r.MT=MT;r.n=n;r.steps={ST("Dişli yarıçapı","Sprocket radius","r=D/2000",rr,"m"),
        ST("Çıkış momenti","Output moment","Mᴛ=f·m·g·r",MT,"Nm"),ST("Çıkış devri","Output speed","n=v/(π·D)",n,"d/dk")};return r;}});

    A.push_back({"feeder","Konveyör & Taşıma","Conveying & Handling","Titreşimli besleyici","Vibrating feeder",
      "Mil üstü redüktörlü motor","Shaft-mounted geared motor","ω=2π·n/60 ; Pₒ=k·m·A²·ω³/1000","ω=2π·n/60 ; Pₒ=k·m·A²·ω³/1000",
      1.75,0.95,
      {V("m","Titreşen kütle m","Vibrating mass m","kg",300),V("A","Genlik A","Amplitude A","mm",4),
       V("n","Ekssantrik devri","Exciter speed","rpm",750),V("k","Güç faktörü k","Power factor k","",0.40)},
      [](std::map<std::string,double>&v){Res r;double w=2*M_PI*v["n"]/60;double A=v["A"]/1000;double P=v["k"]*v["m"]*A*A*w*w*w/1000;
        double MT=v["n"]>0?9550*P/v["n"]:std::nan("");r.MT=MT;r.n=v["n"];r.Pout=P;
        r.steps={ST("Açısal hız","Angular speed","ω=2π·n/60",w,"rad/s"),ST("Çıkış gücü","Output power","Pₒ=k·m·A²·ω³/1000",P,"kW"),
        ST("Çıkış momenti","Output moment","Mᴛ=9550·Pₒ/n",MT,"Nm")};return r;}});

    // ---------- Kaldırma & Vinç ----------
    A.push_back({"hoist","Kaldırma & Vinç","Lifting & Crane","Vinç kaldırma — direkt tambur","Crane hoist — direct drum",
      "İRC Serisi (kaldırma)","İRC series (hoist)","Mᴛ=m·g·r ; n=9,55·v/r","Mᴛ=m·g·r ; n=9.55·v/r",
      1.5,0.97,
      {V("m","Kaldırılacak yük m","Load m","kg",2000),V("D","Tambur çapı Ø","Drum Ø","mm",300),V("v","Kaldırma hızı v","Lift speed v","m/min",10)},
      [](std::map<std::string,double>&v){Res r;double rr=v["D"]/2000;double MT=v["m"]*G*rr;double vms=v["v"]/60;double n=9.55*vms/rr;
        r.MT=MT;r.n=n;r.steps={ST("Tambur yarıçapı","Drum radius","r=D/2000",rr,"m"),ST("Tambur momenti","Drum moment","Mᴛ=m·g·r",MT,"Nm"),
        ST("Tambur devri","Drum speed","n=9,55·v/r",n,"d/dk")};return r;}});

    A.push_back({"pulley","Kaldırma & Vinç","Lifting & Crane","Palangalı kaldırma","Pulley / block-and-tackle hoist",
      "İRC Serisi (kaldırma)","İRC series (hoist)","Mᴛ=m·g·r/z ; n=9,55·v·z/r","Mᴛ=m·g·r/z ; n=9.55·v·z/r",
      1.5,0.95,
      {V("m","Kaldırılacak yük m","Load m","kg",5000),V("D","Tambur çapı Ø","Drum Ø","mm",400),
       V("v","Kaldırma hızı v","Lift speed v","m/min",8),V("z","Palanga kat sayısı z","Rope falls z","",2),V("re","Palanga verimi","Reeving eff.","",0.95)},
      [](std::map<std::string,double>&v){Res r;double rr=v["D"]/2000;double z=std::max(1.0,v["z"]);double MT=v["m"]*G*rr/z/v["re"];
        double vms=v["v"]/60;double n=9.55*vms*z/rr;r.MT=MT;r.n=n;
        r.steps={ST("Tambur yarıçapı","Drum radius","r=D/2000",rr,"m"),ST("Tambur momenti","Drum moment","Mᴛ=m·g·r/z",MT,"Nm"),
        ST("Tambur devri","Drum speed","n=9,55·v·z/r",n,"d/dk")};return r;}});

    A.push_back({"travel","Kaldırma & Vinç","Lifting & Crane","Yürütme (köprü/araba)","Travel (bridge / trolley)",
      "Yürütme redüktörlü motor","Travel geared motor","Mᴛ=[Q·f+μ·Q·(d/2)]·g ; v=π·D·n/60000","Mᴛ=[Q·f+μ·Q·(d/2)]·g ; v=π·D·n/60000",
      1.25,0.95,
      {V("Q","Yük Q","Load Q","kg",5000),V("D","Tekerlek çapı Ø","Wheel Ø","mm",500),V("d","Rulman çapı Ø","Bearing Ø","mm",100),
       V("v","Yürütme hızı v","Travel speed v","m/s",1.5),V("f","Yuvarlanma katsayısı f","Rolling coeff. f","",0.002),V("mu","Rulman sürtünmesi μ","Bearing friction μ","",0.008)},
      [](std::map<std::string,double>&v){Res r;double MTkgm=v["Q"]*v["f"]+v["mu"]*v["Q"]*(v["d"]/2000);double MT=MTkgm*G;double n=60000*v["v"]/(M_PI*v["D"]);
        r.MT=MT;r.n=n;r.steps={ST("Tekerlek momenti","Wheel moment","Mᴛ=[Q·f+μ·Q·(d/2)]·g",MT,"Nm"),
        ST("Tekerlek devri","Wheel speed","n=60000·v/(π·D)",n,"d/dk")};return r;}});

    A.push_back({"slew","Kaldırma & Vinç","Lifting & Crane","Döner (slewing) tahrik","Slewing drive",
      "Helis-konik redüktörlü motor","Helical-bevel geared motor","J=m·r² ; α=(2π·n/60)/t ; Mᴛ=J·α+Tf","J=m·r² ; α=(2π·n/60)/t ; Mᴛ=J·α+Tf",
      1.5,0.94,
      {V("m","Dönen kütle m","Slewing mass m","kg",5000),V("r","Kütle yarıçapı r","Mass radius r","m",3),
       V("n","Dönme devri","Slew speed","rpm",1.5),V("t","Hızlanma süresi t","Accel time t","s",5),V("Tf","Sürtünme momenti Tf","Friction torque Tf","Nm",500)},
      [](std::map<std::string,double>&v){Res r;double J=v["m"]*v["r"]*v["r"];double w=2*M_PI*v["n"]/60;double al=v["t"]>0?w/v["t"]:0;double MT=J*al+v["Tf"];
        r.MT=MT;r.n=v["n"];r.steps={ST("Atalet momenti","Inertia","J=m·r²",J,"kg·m²"),ST("Açısal ivme","Ang. accel","α=(2π·n/60)/t",al,"rad/s²"),
        ST("Çıkış momenti","Output moment","Mᴛ=J·α+Tf",MT,"Nm")};return r;}});

    A.push_back({"lift","Kaldırma & Vinç","Lifting & Crane","Asansör (halatlı)","Passenger lift (traction)",
      "Sertifikalı asansör tahriki","Certified lift drive","F=Q·(1−b)·g ; Pₒ=F·v/1000 ; n=60·rf·v/(π·D)","F=Q·(1−b)·g ; Pₒ=F·v/1000 ; n=60·rf·v/(π·D)",
      1.75,0.95,
      {V("Q","Kabin yükü Q","Car load Q","kg",1000),V("v","Hız v","Speed v","m/s",1.0),V("b","Denge oranı b","Balance b","",0.5),
       V("D","Kasnak çapı Ø","Sheave Ø","mm",600),V("rf","Askı oranı (1/2)","Roping factor (1/2)","",1)},
      [](std::map<std::string,double>&v){Res r;double F=v["Q"]*(1-v["b"])*G;double P=F*v["v"]/1000;double D=v["D"]/1000;double rf=std::max(1.0,v["rf"]);
        double n=60*rf*v["v"]/(M_PI*D);double MT=n>0?9550*P/n:std::nan("");r.MT=MT;r.n=n;r.Pout=P;
        r.steps={ST("Dengesiz kuvvet","Out-of-balance force","F=Q·(1−b)·g",F,"N"),ST("Çıkış gücü","Output power","Pₒ=F·v/1000",P,"kW"),
        ST("Kasnak devri","Sheave speed","n=60·rf·v/(π·D)",n,"d/dk")};return r;}});

    // ---------- Karıştırma & Proses ----------
    A.push_back({"mixer_b","Karıştırma & Proses","Mixing & Process","Karıştırıcı — kanat yöntemi","Agitator — blade method",
      "Helis redüktörlü motor (karıştırıcı)","Helical geared motor (agitator)","Mₖ=(Ød/2)·b·kᵢ·ρ·10 ; Mᴛ=ΣMₖ","Mₖ=(Ød/2)·b·kᵢ·ρ·10 ; Mᴛ=ΣMₖ",
      1.5,0.95,
      {V("Dd","Pervane çapı Ød","Impeller Ø","mm",1500),V("b","Pervane genişliği b","Blade width b","mm",100),
       V("k1","1. kanat sıvı yük. k₁","Blade-1 liquid h. k₁","mm",3500),V("k2","2. kanat k₂","Blade-2 k₂","mm",2500),
       V("k3","3. kanat k₃","Blade-3 k₃","mm",1500),V("n","Mil devri n","Shaft speed n","rpm",20),V("ro","Yoğunluk ρ","Density ρ","gr/cm³",1.1)},
      [](std::map<std::string,double>&v){Res r;double rd=v["Dd"]/2000,bb=v["b"]/1000,rho=v["ro"]*1000;
        auto blade=[&](double k){return k>0?rd*bb*(k/1000)*rho*10:0.0;};
        double M1=blade(v["k1"]),M2=blade(v["k2"]),M3=blade(v["k3"]);double MT=M1+M2+M3;r.MT=MT;r.n=v["n"];
        r.steps={ST("1. kanat momenti","Blade-1 moment","M₁=(Ød/2)·b·k₁·ρ·10",M1,"Nm"),ST("2. kanat momenti","Blade-2 moment","M₂",M2,"Nm"),
        ST("3. kanat momenti","Blade-3 moment","M₃",M3,"Nm"),ST("Toplam moment","Total moment","Mᴛ=ΣMₖ",MT,"Nm")};return r;}});

    A.push_back({"mixer_np","Karıştırma & Proses","Mixing & Process","Karıştırıcı — güç sayısı (Np)","Agitator — power number (Np)",
      "Helis redüktörlü motor","Helical geared motor","N=n/60 ; Pₒ=Np·ρ·N³·D⁵/1000","N=n/60 ; Pₒ=Np·ρ·N³·D⁵/1000",
      1.5,0.96,
      {V("Np","Güç sayısı Np","Power number Np","",1.5),V("ro","Yoğunluk ρ","Density ρ","kg/m³",1000),
       V("D","Pervane çapı Ø","Impeller Ø","mm",500),V("n","Mil devri n","Shaft speed n","rpm",60)},
      [](std::map<std::string,double>&v){Res r;double N=v["n"]/60;double D=v["D"]/1000;double P=v["Np"]*v["ro"]*N*N*N*std::pow(D,5)/1000;
        double MT=v["n"]>0?9550*P/v["n"]:std::nan("");r.MT=MT;r.n=v["n"];r.Pout=P;
        r.steps={ST("Devir (1/s)","Rev/s","N=n/60",N,"1/s"),ST("Çıkış gücü","Output power","Pₒ=Np·ρ·N³·D⁵/1000",P,"kW"),
        ST("Çıkış momenti","Output moment","Mᴛ=9550·Pₒ/n",MT,"Nm")};return r;}});

    A.push_back({"kiln","Karıştırma & Proses","Mixing & Process","Döner fırın / kurutma tamburu","Rotary kiln / drying drum",
      "Helis-konik redüktörlü motor","Helical-bevel geared motor","Mᴛ=(1+k)·m·g·(D/2)·e","Mᴛ=(1+k)·m·g·(D/2)·e",
      1.5,0.95,
      {V("D","İç çap Ø","Internal Ø","mm",3000),V("m","Dönen yük m","Rotating load m","kg",20000),
       V("e","Eksantriklik e","Eccentricity e","",0.35),V("n","Dönme devri n","Rotation speed n","rpm",2),V("k","Sürtünme payı k","Friction allow. k","%",20)},
      [](std::map<std::string,double>&v){Res r;double D=v["D"]/1000;double MT=(1+v["k"]/100)*v["m"]*G*(D/2)*v["e"];r.MT=MT;r.n=v["n"];
        r.steps={ST("Çıkış momenti","Output moment","Mᴛ=(1+k)·m·g·(D/2)·e",MT,"Nm")};return r;}});

    A.push_back({"extruder","Karıştırma & Proses","Mixing & Process","Ekstruder (vida)","Extruder (screw)",
      "Helis redüktörlü motor (yüksek eksenel)","Helical geared motor (high axial)","Pₒ=SME·Q ; Mᴛ=9550·Pₒ/n","Pₒ=SME·Q ; Mᴛ=9550·Pₒ/n",
      1.5,0.96,
      {V("Q","Debi Q","Throughput Q","kg/h",200),V("SME","Özgül mek. enerji","Specific mech. energy","kWh/kg",0.20),V("n","Vida devri n","Screw speed n","rpm",100)},
      [](std::map<std::string,double>&v){Res r;double P=v["SME"]*v["Q"];double MT=v["n"]>0?9550*P/v["n"]:std::nan("");r.MT=MT;r.n=v["n"];r.Pout=P;
        r.steps={ST("Çıkış gücü","Output power","Pₒ=SME·Q",P,"kW"),ST("Çıkış momenti","Output moment","Mᴛ=9550·Pₒ/n",MT,"Nm")};return r;}});

    // ---------- Değirmen & Öğütme ----------
    auto specEnergy=[](std::string id,std::string trn,std::string enn,std::string serTR,std::string serEN,double sf,double eta,double defQ,double defE,double defn){
        return App{id,"Değirmen & Öğütme","Milling & Grinding",trn,enn,serTR,serEN,"Pₒ=E·Q ; Mᴛ=9550·Pₒ/n","Pₒ=E·Q ; Mᴛ=9550·Pₒ/n",sf,eta,
          {V("Q","Kapasite Q","Capacity Q","t/h",defQ),V("E","Özgül enerji E","Specific energy E","kWh/t",defE),V("n","Çıkış devri n","Output speed n","rpm",defn)},
          [](std::map<std::string,double>&v){Res r;double P=v["E"]*v["Q"];double MT=v["n"]>0?9550*P/v["n"]:std::nan("");r.MT=MT;r.n=v["n"];r.Pout=P;
            r.steps={ST("Çıkış gücü","Output power","Pₒ=E·Q",P,"kW"),ST("Çıkış momenti","Output moment","Mᴛ=9550·Pₒ/n",MT,"Nm")};return r;}};
    };
    A.push_back(specEnergy("roller","Valsli değirmen (un)","Roller mill (flour)","Helis redüktörlü motor","Helical geared motor",1.5,0.96,10,10,300));
    A.push_back(specEnergy("hammer","Çekiçli değirmen","Hammer mill","Helis redüktörlü motor (darbe)","Helical geared motor (shock)",1.75,0.96,5,15,1500));

    A.push_back({"ballmill","Değirmen & Öğütme","Milling & Grinding","Bilyalı değirmen (Bond)","Ball mill (Bond)",
      "Değirmen tipi redüktör","Mill-duty geared drive","E=10·Wi·(1/√P₈₀−1/√F₈₀) ; Pₒ=E·Q","E=10·Wi·(1/√P₈₀−1/√F₈₀) ; Pₒ=E·Q",
      1.75,0.95,
      {V("Q","Kapasite Q","Capacity Q","t/h",20),V("Wi","İş indeksi Wi","Work index Wi","kWh/t",13),
       V("F","Besleme F₈₀","Feed F₈₀","µm",10000),V("Pp","Ürün P₈₀","Product P₈₀","µm",100),V("n","Değirmen devri n","Mill speed n","rpm",18)},
      [](std::map<std::string,double>&v){Res r;double Ee=10*v["Wi"]*(1/std::sqrt(v["Pp"])-1/std::sqrt(v["F"]));double P=Ee*v["Q"];
        double MT=v["n"]>0?9550*P/v["n"]:std::nan("");r.MT=MT;r.n=v["n"];r.Pout=P;
        r.steps={ST("Özgül enerji (Bond)","Specific energy (Bond)","E=10·Wi·(1/√P₈₀−1/√F₈₀)",Ee,"kWh/t"),
        ST("Çıkış gücü","Output power","Pₒ=E·Q",P,"kW"),ST("Çıkış momenti","Output moment","Mᴛ=9550·Pₒ/n",MT,"Nm")};return r;}});

    A.push_back({"sifter","Değirmen & Öğütme","Milling & Grinding","Elek / plansifter","Sifter / plansifter",
      "Helis redüktörlü motor","Helical geared motor","ω=2π·n/60 ; Pₒ=k·m·r²·ω³/1000","ω=2π·n/60 ; Pₒ=k·m·r²·ω³/1000",
      1.5,0.96,
      {V("m","Salınan kütle m","Gyrating mass m","kg",300),V("r","Salınım yarıçapı r","Gyration throw r","mm",40),
       V("n","Devir n","Speed n","rpm",220),V("k","Sönüm faktörü k","Damping factor k","",0.35)},
      [](std::map<std::string,double>&v){Res r;double w=2*M_PI*v["n"]/60;double rr=v["r"]/1000;double P=v["k"]*v["m"]*rr*rr*w*w*w/1000;
        double MT=v["n"]>0?9550*P/v["n"]:std::nan("");r.MT=MT;r.n=v["n"];r.Pout=P;
        r.steps={ST("Açısal hız","Angular speed","ω=2π·n/60",w,"rad/s"),ST("Çıkış gücü","Output power","Pₒ=k·m·r²·ω³/1000",P,"kW"),
        ST("Çıkış momenti","Output moment","Mᴛ=9550·Pₒ/n",MT,"Nm")};return r;}});

    A.push_back(specEnergy("pellet","Pelet değirmeni","Pellet mill","Helis-konik redüktör (ağır)","Helical-bevel (heavy)",1.75,0.95,8,45,250));

    // ---------- Kırma & Titreşim ----------
    { App c=specEnergy("crusher","Kırıcı (taş / cevher)","Crusher (stone / ore)","Helis-konik redüktör (ağır)","Helical-bevel (heavy duty)",1.75,0.95,50,2,200);
      c.grpTR="Kırma & Titreşim"; c.grpEN="Crushing & Vibrating"; A.push_back(c); }

    A.push_back({"vibscreen","Kırma & Titreşim","Crushing & Vibrating","Titreşimli elek","Vibrating screen",
      "Mil üstü redüktörlü motor","Shaft-mounted geared motor","ω=2π·n/60 ; Pₒ=k·m·A²·ω³/1000","ω=2π·n/60 ; Pₒ=k·m·A²·ω³/1000",
      1.75,0.95,
      {V("m","Titreşen kütle m","Vibrating mass m","kg",800),V("A","Genlik A","Amplitude A","mm",5),
       V("n","Ekssantrik devri","Exciter speed","rpm",900),V("k","Güç faktörü k","Power factor k","",0.5)},
      [](std::map<std::string,double>&v){Res r;double w=2*M_PI*v["n"]/60;double A=v["A"]/1000;double P=v["k"]*v["m"]*A*A*w*w*w/1000;
        double MT=v["n"]>0?9550*P/v["n"]:std::nan("");r.MT=MT;r.n=v["n"];r.Pout=P;
        r.steps={ST("Açısal hız","Angular speed","ω=2π·n/60",w,"rad/s"),ST("Çıkış gücü","Output power","Pₒ=k·m·A²·ω³/1000",P,"kW"),
        ST("Çıkış momenti","Output moment","Mᴛ=9550·Pₒ/n",MT,"Nm")};return r;}});

    A.push_back({"rotable","Kırma & Titreşim","Crushing & Vibrating","Döner tabla / turntable","Rotary table / turntable",
      "Helis-konik redüktörlü motor","Helical-bevel geared motor","J=0,5·m·r² ; α=(2π·n/60)/t ; Mᴛ=J·α+Tf","J=0.5·m·r² ; α=(2π·n/60)/t ; Mᴛ=J·α+Tf",
      1.5,0.95,
      {V("m","Tabla + yük m","Table + load m","kg",2000),V("r","Yarıçap r","Radius r","mm",800),
       V("n","Çalışma devri n","Operating speed n","rpm",5),V("t","Hızlanma süresi t","Accel time t","s",3),V("Tf","Sürtünme momenti Tf","Friction torque Tf","Nm",200)},
      [](std::map<std::string,double>&v){Res r;double rr=v["r"]/1000;double J=0.5*v["m"]*rr*rr;double w=2*M_PI*v["n"]/60;double al=v["t"]>0?w/v["t"]:0;
        double MT=J*al+v["Tf"];r.MT=MT;r.n=v["n"];r.steps={ST("Atalet momenti","Inertia","J=0,5·m·r²",J,"kg·m²"),
        ST("Açısal ivme","Ang. accel","α=(2π·n/60)/t",al,"rad/s²"),ST("Çıkış momenti","Output moment","Mᴛ=J·α+Tf",MT,"Nm")};return r;}});

    // ---------- Pompa & Fan ----------
    auto pumpApp=[](std::string id,std::string trn,std::string enn,std::string serTR,std::string serEN,double sf,double eta,double dQ,double dH,double dpe,double dn){
      return App{id,"Pompa & Fan","Pumps & Fans",trn,enn,serTR,serEN,"Pₒ=Q·H·SG/(367·ηp) ; Mᴛ=9550·Pₒ/n","Pₒ=Q·H·SG/(367·ηp) ; Mᴛ=9550·Pₒ/n",sf,eta,
        {V("Q","Debi Q","Flow Q","m³/h",dQ),V("H","Basma yüksekliği H","Head H","m",dH),V("SG","Özgül ağırlık SG","Specific gravity SG","",1.0),
         V("pe","Pompa verimi ηp","Pump eff. ηp","",dpe),V("n","Pompa devri n","Pump speed n","rpm",dn)},
        [](std::map<std::string,double>&v){Res r;double P=v["pe"]>0?v["Q"]*v["H"]*v["SG"]/(367*v["pe"]):std::nan("");double MT=v["n"]>0?9550*P/v["n"]:std::nan("");
          r.MT=MT;r.n=v["n"];r.Pout=P;r.steps={ST("Çıkış gücü","Output power","Pₒ=Q·H·SG/(367·ηp)",P,"kW"),
          ST("Çıkış momenti","Output moment","Mᴛ=9550·Pₒ/n",MT,"Nm")};return r;}};
    };
    A.push_back(pumpApp("pump","Santrifüj pompa","Centrifugal pump","Helis redüktörlü motor","Helical geared motor",1.25,0.97,50,30,0.70,1450));
    A.push_back(pumpApp("recip","Pistonlu / pozitif deplasmanlı pompa","Reciprocating / PD pump","Helis redüktörlü motor (darbe)","Helical geared motor (shock)",1.5,0.96,20,60,0.85,300));

    A.push_back({"fan","Pompa & Fan","Pumps & Fans","Santrifüj fan / körük","Centrifugal fan / blower",
      "Helis redüktörlü motor","Helical geared motor","Pₒ=(Q/3600)·Δp/(1000·ηf) ; Mᴛ=9550·Pₒ/n","Pₒ=(Q/3600)·Δp/(1000·ηf) ; Mᴛ=9550·Pₒ/n",
      1.25,0.97,
      {V("Q","Hava debisi Q","Air flow Q","m³/h",5000),V("dp","Basınç artışı Δp","Pressure rise Δp","Pa",1000),
       V("fe","Fan verimi ηf","Fan eff. ηf","",0.65),V("n","Fan devri n","Fan speed n","rpm",1450)},
      [](std::map<std::string,double>&v){Res r;double P=v["fe"]>0?(v["Q"]/3600)*v["dp"]/1000/v["fe"]:std::nan("");double MT=v["n"]>0?9550*P/v["n"]:std::nan("");
        r.MT=MT;r.n=v["n"];r.Pout=P;r.steps={ST("Çıkış gücü","Output power","Pₒ=(Q/3600)·Δp/(1000·ηf)",P,"kW"),
        ST("Çıkış momenti","Output moment","Mᴛ=9550·Pₒ/n",MT,"Nm")};return r;}});

    return A;
}

// ---------------------------------------------------------------------------
static std::string prompt_line(){ std::string s; std::getline(std::cin, s); return s; }

int main(){
    std::vector<App> apps = build_apps();

    std::cout << "Dil / Language:  1) Turkce   2) English\n> ";
    { std::string l=prompt_line(); if(!l.empty() && (l[0]=='2'||l[0]=='e'||l[0]=='E')) LANG=1; }

    while(true){
        std::cout << "\n============================================================\n";
        std::cout << T("  İ-MAK REDÜKTÖR SEÇİCI  —  Uygulama seçin","  I-MAK GEARBOX SELECTOR  —  choose an application") << "\n";
        std::cout << "============================================================\n";
        std::string lastGrp;
        for(size_t i=0;i<apps.size();++i){
            std::string g = LANG?apps[i].grpEN:apps[i].grpTR;
            if(g!=lastGrp){ std::cout << "\n  " << g << "\n"; lastGrp=g; }
            std::cout << "   " << std::setw(2) << (i+1) << ") " << (LANG?apps[i].nameEN:apps[i].nameTR) << "\n";
        }
        std::cout << "\n   0) " << T("Çıkış","Quit") << "\n> ";
        std::string sel = prompt_line();
        if(sel.empty()) continue;
        int idx; try{ idx=std::stoi(sel); }catch(...){ continue; }
        if(idx==0) break;
        if(idx<1 || idx>(int)apps.size()){ std::cout << T("Geçersiz seçim.","Invalid choice.") << "\n"; continue; }
        App& a = apps[idx-1];

        std::cout << "\n------------------------------------------------------------\n";
        std::cout << (LANG?a.grpEN:a.grpTR) << "  |  " << (LANG?a.serEN:a.serTR) << "\n";
        std::cout << ">> " << (LANG?a.nameEN:a.nameTR) << "\n";
        std::cout << T("Formül","Formula") << ":  " << (LANG?a.fEN:a.fTR) << "\n";
        std::cout << T("(Enter = varsayılan değer)","(Enter = default value)") << "\n\n";

        std::map<std::string,double> v;
        for(auto& var : a.vars){
            std::string lab = LANG?var.en:var.tr;
            std::cout << "  " << lab << (var.unit.empty()?"":(" ("+var.unit+")"))
                      << " [" << num(var.def) << "]: ";
            std::string in = prompt_line();
            double val = var.def;
            if(!in.empty()){ std::replace(in.begin(),in.end(),',','.'); try{ val=std::stod(in); }catch(...){ val=var.def; } }
            v[var.id]=val;
        }
        // global inputs
        auto ask=[&](std::string tr,std::string en,double def)->double{
            std::cout << "  " << T(tr,en) << " [" << num(def) << "]: ";
            std::string in=prompt_line(); if(in.empty()) return def; std::replace(in.begin(),in.end(),',','.');
            try{ return std::stod(in); }catch(...){ return def; } };
        double n1 = ask("Motor devri n₁ (d/dk)","Motor speed n₁ (rpm)",1450);
        double eta= ask("Redüktör verimi η","Gearbox efficiency η",a.eta);
        double sf = ask("Servis faktörü Sf","Service factor Sf",a.sf);

        Res r = a.calc(v);
        double MT=r.MT, n=r.n, Pout=r.Pout;
        if(!std::isfinite(MT) && std::isfinite(Pout) && n>0) MT=9550*Pout/n;
        if(!std::isfinite(Pout) && std::isfinite(MT) && n>0) Pout=MT*n/9550;
        double Pmotor = (eta>0)?Pout/eta:std::nan("");
        double rec = std::isfinite(Pmotor)?iecUp(Pmotor):std::nan("");
        double ratio = (n1>0&&n>0)?n1/n:std::nan("");
        if(sf<1) sf=1;
        double Mn = std::isfinite(MT)?MT*sf:std::nan("");

        std::cout << "\n  " << T("HESAP ADIMLARI","CALCULATION STEPS") << "\n  ----------------------------------------\n";
        for(auto& s : r.steps)
            std::cout << "   " << std::left << std::setw(26) << (LANG?s.en:s.tr)
                      << " = " << autor(s.res) << " " << s.unit << "\n";
        std::cout << "   " << std::left << std::setw(26) << T("Motor gücü","Motor power")
                  << " = " << num(Pmotor,2) << " kW -> " << num(rec, rec<10?1:0) << " kW\n";
        std::cout << "   " << std::left << std::setw(26) << T("Gerekli nominal moment","Required nominal moment")
                  << " = " << num(Mn,0) << " Nm\n";

        std::cout << "\n  " << T("SONUÇ","RESULT") << "\n  ----------------------------------------\n";
        std::cout << "   " << std::left << std::setw(28) << T("Gerekli nominal moment Mₙ","Required nominal moment Mₙ") << num(Mn,0) << " Nm\n";
        std::cout << "   " << std::left << std::setw(28) << T("Çıkış momenti Mᴛ","Output moment Mᴛ") << num(MT,0) << " Nm\n";
        std::cout << "   " << std::left << std::setw(28) << T("Çıkış devri n","Output speed n") << autor(n) << " d/dk\n";
        std::cout << "   " << std::left << std::setw(28) << T("Tahvil i","Ratio i") << num(ratio,1) << " :1\n";
        std::cout << "   " << std::left << std::setw(28) << T("Motor gücü","Motor power") << num(rec, rec<10?1:0) << " kW\n";
        std::cout << "   " << std::left << std::setw(28) << T("Servis faktörü Sf","Service factor Sf") << num(sf,2) << "\n";
        std::cout << "\n   " << T("Öneri","Suggestion") << ": "
                  << T("Nominal momenti Mₙ ≥ ","Choose an I-MAK unit with nominal moment Mₙ ≥ ")
                  << num(Mn,0) << " Nm"
                  << T(" olan bir İ-MAK redüktörü seçin (i ≈ "," at ratio i ≈ ")
                  << num(ratio,1) << ":1).\n";
        std::cout << "   " << (LANG?a.serEN:a.serTR) << "\n";
        std::cout << "------------------------------------------------------------\n";
    }
    std::cout << T("\nGörüşmek üzere!\n","\nGoodbye!\n");
    return 0;
}
