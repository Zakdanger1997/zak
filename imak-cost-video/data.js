// i.Mak — "The real cost of choosing a drive" — facts + sources (editable).
// Every figure carries its source; the source prints in a small line in-frame.
window.DATA = {
  web: "imakreduktor.com",
  motorShare: 53,          // % of global electricity used by electric motor systems (2023)
  motorShareIndustry: 72,  // % in industry
  // Lifetime total-cost-of-ownership split for an electric drive over ~15–20 yrs
  tco: [
    { label: "Energy",             pct: 90, color: "#920000" },
    { label: "Service & downtime", pct: 7,  color: "#C98A1E" },
    { label: "Purchase price",     pct: 3,  color: "#8A8176" }
  ],
  gearHelical: 98,         // % efficiency per stage (best case)
  gearWormLo: 50,          // worm efficiency low end
  gearWormHi: 90,          // worm efficiency high end
  downtimeAvg: 125000,     // $/hour, average industrial unplanned downtime
  downtimeAuto: 2.3,       // $M/hour, large automotive plant
  configurations: 1000000, // i.Mak product configurations
  sources: {
    motors:  "Source: IEA-4E Electric Motor Systems Annex, 2023",
    tco:     "Source: U.S. Dept. of Energy — electric-motor life-cycle cost",
    gears:   "Source: published helical vs worm gear-efficiency data",
    downtime:"Sources: ABB Value of Reliability, 2023 · Siemens True Cost of Downtime, 2024",
    combined:"Sources: IEA-4E 2023 · U.S. DOE motor life-cycle · ABB Value of Reliability 2023 · Siemens True Cost of Downtime 2024 · published gear-efficiency data"
  }
};
