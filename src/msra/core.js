/* ---------- MSRA Log: standard, data and MSL matching (Library 1.10.0) ---------- */
const MS_STD = __MSRA_STD__;   // the Oxypro standard from The Borough log: items [disc, stage, title, material keys], mats [key, disc, description]
const MS_DISC = [
  { code: 'MEC', name: 'MECHANICAL (HVAC)', sum: 'Method Statement - HVAC', tab: 'HVAC' },
  { code: 'PLU', name: 'PLUMBING & DRAINAGE', sum: 'Method Statement - PLUMBING', tab: 'Plumbing' },
  { code: 'ELE', name: 'ELECTRICAL', sum: 'Method Statement - ELECTRICAL', tab: 'Electrical' },
  { code: 'ELV', name: 'EXTRA LOW VOLTAGE (ELV)', sum: 'Method Statement - ELV', tab: 'ELV' },
  { code: 'FF', name: 'FIRE FIGHTING', sum: 'Method Statement - FIRE FIGHTING', tab: 'Fire Fighting' },
  { code: 'LPG', name: 'LPG', sum: 'Method Statement - LPG', tab: 'LPG' },
  { code: 'MEP', name: 'MEP GENERAL', sum: 'Method Statement - MEP', tab: 'MEP General' }
];
const MS_CODES = MS_DISC.map(d => d.code);
const MS_DNAME = Object.fromEntries(MS_DISC.map(d => [d.code, d.name]));
const MS_STATUS = ['A', 'B', 'C', 'D', 'E', 'UR', 'n/a'];
const MS_COUNTED = ['A', 'B', 'C', 'D', 'E', 'UR'];
const MS_FILL = { A: '#00B050', B: '#92D050', C: '#FF0000', D: '#C00000', E: '#00B0F0', UR: '#FFFF00', 'n/a': '#D9D9D9' };
const MS_LEGEND = [['A', 'APPROVED'], ['B', 'APPROVED AS NOTED'], ['C', 'REVISE & RESUBMIT'], ['D', 'REJECTED'], ['E', 'INFORMATION & RECORD'], ['UR', 'UNDER REVIEW BY CONSULTANT']];
const MS_STAGE = { I: 'INSTALLATION METHOD STATEMENTS', T: 'TESTING & COMMISSIONING METHOD STATEMENTS' };
const MS_BLOCK_MAX = 6;
const msId = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-3);
const msIso = v => /^\d{4}-\d{2}-\d{2}$/.test(String(v || '')) ? String(v) : '';
const msDay = iso => { const m = msIso(iso).match(/^(\d{4})-(\d{2})-(\d{2})$/); return m ? Date.UTC(+m[1], +m[2] - 1, +m[3]) / 86400000 : null; };
const msFromDay = n => { const d = new Date(n * 86400000); return d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0'); };
const msToday = () => { const d = new Date(); return Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000; };
const MS_MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
// d-mmm-yy, as the log shows dates
function msFmt(iso) { const m = msIso(iso).match(/^(\d{4})-(\d{2})-(\d{2})$/); return m ? `${+m[3]}-${MS_MON[+m[2] - 1]}-${m[1].slice(2)}` : ''; }
function msFmtLong(iso) { const m = msIso(iso).match(/^(\d{4})-(\d{2})-(\d{2})$/); return m ? `${+m[3]}/${MS_MON[+m[2] - 1]}/${m[1]}` : ''; }
function msStatus(v) {
  const s = String(v == null ? '' : v).trim(); if (!s) return '';
  if (/^n\/?a$/i.test(s)) return 'n/a';
  if (/^ur/i.test(s)) return 'UR';
  const c = s[0].toUpperCase(); return 'ABCDE'.includes(c) ? c : '';
}
const msReview = it => { const a = msDay(it.sub), b = msDay(it.ret); return a != null && b != null ? b - a : ''; };

/* Title Case for method statement titles (house rule): minor words lower case, acronyms kept */
const MS_MINOR = new Set(['of', 'and', '&', 'with', 'for', 'to', 'the', 'in', 'on', 'by', 'or', 'a', 'an', 'incl.', 'incl', 'as', 'at', 'from', 'per']);
const MS_ACR = new Set(['GI', 'PI', 'CHW', 'FAHU', 'AHU', 'FCU', 'PICV', 'VFD', 'VRF', 'DX', 'VCD', 'NRD', 'FD', 'MVCD', 'MSD', 'MSFD', 'SMFD', 'UPVC', 'HDPE', 'PPR', 'PEX', 'GRP', 'PRV', 'LV', 'MV', 'HV', 'LSF', 'LSZH', 'PVC', 'XLPE', 'SWA', 'FP-400', 'DP', 'MDB', 'SMDB', 'EMDB', 'ESMDB', 'MCC', 'DB', 'EDB', 'ATS', 'ELV', 'BMS', 'ICT', 'UPS', 'CCTV', 'FM-200', 'LPG', 'MEP', 'IST', 'TAB', 'BOH', 'FOH', 'CO', 'IP', 'SIRA', 'ODF', 'HCP', 'RCP', 'SCP', 'ONU', 'CAT6', 'JRC', 'DRV', 'NRV', 'IR', 'DEWA', 'DCD', 'DM', 'WRAS', 'PN20', 'PN25', 'MATV', 'IPTV', 'PA', 'BGM', 'RMU', 'TV', 'AV', 'EV', 'FA', 'HVAC', 'CPVC', 'MS', 'SS', 'HDG']);
function msTitleCase(t) {
  const s = String(t || '').trim().replace(/\s+/g, ' '); if (!s) return '';
  let i = 0;
  return s.split(' ').map(w => {
    const first = i++ === 0;
    return w.split(/([\/(),-])/).map(p => {
      if (!p || /^[\/(),-]$/.test(p)) return p;
      const u = p.toUpperCase();
      if (u === 'UPVC') return 'uPVC';
      if (MS_ACR.has(u) || /^[A-Z]{1,3}\d+[A-Z]*$/.test(u)) return u;
      const l = p.toLowerCase();
      if (!first && MS_MINOR.has(l)) return l;
      return l.charAt(0).toUpperCase() + l.slice(1);
    }).join('');
  }).join(' ');
}

/* ---------- the log ---------- */
const msBlankItem = (d, s, t, m) => ({ id: msId(), d, s, b: '', t: t || '', ref: '', rev: '0', plan: '', sub: '', ret: '', st: '', fin: '', rem: '', m: m || [] });
// x: the item's place in the standard, so a planner's MSL can be linked to it later
function msStandardItems() { return MS_STD.items.map(([d, s, t], x) => ({ ...msBlankItem(d, s, t, []), x })); }
function msUp(v) { return String(v || '').replace(/^m\/s\.?\s*/i, '').trim().toUpperCase(); }
function msDefaultBlock(p) {
  const real = v => { const t = String(v || '').replace(/^m\/s\.?\s*/i, '').trim(); return /^(n\/?a|not applicable|-|–)$/i.test(t) ? '' : t; };
  let project = msUp(p.name || p.no);
  if (p.levels) project += ` (${msUp(p.levels)})`;
  if (p.area) project += `, ${msUp(p.area)}`;
  if (p.code) project += ` (${msUp(p.code)})`;
  return [
    { label: 'PROJECT', value: project },
    { label: 'CLIENT', value: msUp(real(p.client)) },
    { label: 'CONSULTANT', value: msUp(real(p.leadConsultant) || real(p.mepConsultant)) },
    { label: 'MEP CONSULTANT', value: msUp(real(p.mepConsultant)) },
    { label: 'CONTRACTOR', value: msUp(real(p.mainContractor)) },
    { label: 'MEP CONTRACTOR', value: 'OXYPRO ELECTROMECHANICAL WORK LLC' }
  ];
}
function msNewLog(p, how) {
  return { no: p.no, v: 1, rev: '00', block: msDefaultBlock(p), items: how === 'empty' ? [] : msStandardItems(), msl: null, start: how, createdAt: new Date().toISOString(), updatedAt: '' };
}
// cleans a log read from the library or from a saved file
function msClean(x, p) {
  const s = v => String(v == null ? '' : v).slice(0, 2000);
  const log = { no: p.no, v: 1, rev: s(x.rev || '00').slice(0, 10), start: s(x.start).slice(0, 20), createdAt: s(x.createdAt), updatedAt: s(x.updatedAt), updatedBy: s(x.updatedBy).slice(0, 120) };
  log.block = Array.isArray(x.block) && x.block.length ? x.block.slice(0, MS_BLOCK_MAX).map(r => ({ label: s(r && r.label).slice(0, 60), value: s(r && r.value).slice(0, 400) })) : msDefaultBlock(p);
  log.items = (Array.isArray(x.items) ? x.items : []).filter(it => it && MS_CODES.includes(it.d)).slice(0, 1500).map(it => ({
    id: s(it.id).slice(0, 24) || msId(), d: it.d, s: it.s === 'T' ? 'T' : 'I', b: s(it.b).slice(0, 80), t: s(it.t).slice(0, 400), ref: s(it.ref).slice(0, 120), rev: s(it.rev).slice(0, 10),
    plan: msIso(it.plan), sub: msIso(it.sub), ret: msIso(it.ret), st: msStatus(it.st), fin: msStatus(it.fin), rem: s(it.rem).slice(0, 400),
    m: Array.isArray(it.m) ? it.m.map(k => s(k).slice(0, 12)).filter(Boolean).slice(0, 60) : [],
    ...(Number.isInteger(it.x) && it.x >= 0 && it.x < MS_STD.items.length ? { x: it.x } : {})
  }));
  const m = x.msl;
  log.msl = m && Array.isArray(m.items) ? {
    file: s(m.file).slice(0, 200), sheet: s(m.sheet).slice(0, 200), uploaded: msIso(m.uploaded), lagI: Math.max(0, Math.min(365, parseInt(m.lagI, 10) || 0)), lagT: Math.max(0, Math.min(365, parseInt(m.lagT, 10) || 0)),
    items: m.items.slice(0, 1500).map(r => ({ k: s(r.k).slice(0, 12), d: MS_CODES.includes(r.d) ? r.d : 'MEP', sn: s(r.sn).slice(0, 10), desc: s(r.desc).slice(0, 300), lead: s(r.lead).slice(0, 40), date: msIso(r.date), rem: s(r.rem).slice(0, 200) })).filter(r => r.k)
  } : null;
  return log;
}
const msItemsOf = (log, d, st) => log.items.filter(it => it.d === d && (!st || it.s === st));

/* counts as the workbook's formulas make them */
function msCounts(items) {
  const c = { total: items.length, A: 0, B: 0, C: 0, D: 0, E: 0, UR: 0, na: 0, filled: 0, planned: 0, overdue: 0, soon: 0, notSub: 0 };
  const t0 = msToday();
  for (const it of items) {
    if (it.fin === 'n/a') c.na++; else if (it.fin) c[it.fin]++;
    if (it.fin) c.filled++;
    const pd = msDay(it.plan);
    if (pd != null) { c.planned++; if (!it.sub) { if (pd < t0) c.overdue++; else if (pd - t0 <= 7) c.soon++; } }
    if (!it.sub && !it.fin) c.notSub++;
  }
  c.sub = c.A + c.B + c.C + c.D + c.E + c.UR;            // the strip's TOTAL (n/a not counted)
  c.toSubOverall = c.total - (c.sub - (c.C + c.D));      // =D-(E-(H+I))
  c.toSubSection = (c.total - c.filled) + c.C + c.D;     // =(D-E)+H+I, E = COUNTA of Final Status
  return c;
}
function msProgress(it) {
  const f = it.fin;
  if (f === 'A' || f === 'B') return 'Approved';
  if (f === 'E') return 'For Record';
  if (f === 'UR') return 'Under Review';
  if (f === 'C' || f === 'D') return 'Resubmission Required';
  if (it.sub) return 'Submitted';
  const pd = msDay(it.plan); if (pd != null && pd < msToday()) return 'Overdue';
  return 'Not Submitted';
}

/* ---------- the planner's Material Submittal Log (MSL) ---------- */
const MS_DISC_WORDS = [
  ['ELV', /\b(ELV|EXTRA LOW VOLTAGE|LOW CURRENT)\b/], ['FF', /\b(FIRE FIGHTING|FIREFIGHTING|FIRE PROTECTION|FIRE SUPPRESSION|FF)\b/], ['LPG', /\b(LPG|GAS SYSTEMS?)\b/],
  ['PLU', /\b(PLUMBING|DRAINAGE|PLU|PL|PH|PUBLIC HEALTH)\b/], ['MEC', /\b(HVAC|MECHANICAL|MEC|MECH|ACMV|AIR CONDITIONING)\b/], ['ELE', /\b(ELECTRICAL|ELE|ELEC|EL)\b/], ['MEP', /\b(MEP|GENERAL|COMMON)\b/]
];
function msDiscOf(text) { const t = ' ' + String(text || '').toUpperCase().replace(/[^A-Z0-9]+/g, ' ') + ' '; for (const [c, re] of MS_DISC_WORDS) if (re.test(t)) return c; return ''; }
const MS_SN_HDR = /^(sr\.?\s*no\.?|s\.?\s*no\.?|sl\.?\s*no\.?|sn|no\.?|#|item\s*no\.?|serial(\s*no\.?)?|s\/n)$/i;
function msCellText(v) { return v == null ? '' : v instanceof Date ? '' : String(v).replace(/\s+/g, ' ').trim(); }
function msCellDate(v) {
  if (v instanceof Date && !isNaN(v)) { const d = new Date(v.getTime() + 12 * 3600000); return d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0'); }
  if (typeof v === 'number' && v > 20000 && v < 80000) return msFromDay(Math.round(v) - 25569);
  const s = msCellText(v); let m;
  if ((m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/))) return msFromDay(Date.UTC(+m[1], +m[2] - 1, +m[3]) / 86400000);
  if ((m = s.match(/^(\d{1,2})[-\/ .]([A-Za-z]{3})[A-Za-z]*[-\/ .](\d{2,4})$/))) { const mo = MS_MON.findIndex(x => x.toLowerCase() === m[2].toLowerCase()); if (mo >= 0) { const y = +m[3] < 100 ? 2000 + +m[3] : +m[3]; return msFromDay(Date.UTC(y, mo, +m[1]) / 86400000); } }
  if ((m = s.match(/^(\d{1,2})[\/.-](\d{1,2})[\/.-](\d{2,4})$/))) { const y = +m[3] < 100 ? 2000 + +m[3] : +m[3]; if (+m[2] <= 12) return msFromDay(Date.UTC(y, +m[2] - 1, +m[1]) / 86400000); }
  return '';
}
/* Reads every visible sheet of the planner's log: finds the header row (the "Description" column), the SN, planned submission date and lead type columns,
   and discipline section rows ("ELECTRICAL", "PLUMBING", …) or takes the discipline from the sheet name. grids: [{name, rows}] */
function msParseMsl(grids) {
  const out = [], sheetsUsed = [];
  for (const g of grids) {
    const rows = g.rows; if (!rows || !rows.length) continue;
    let h = -1, cDesc = -1;
    for (let r = 0; r < Math.min(rows.length, 40) && h < 0; r++) {
      const row = rows[r] || [];
      for (let c = 0; c < row.length; c++) { const t = msCellText(row[c]); if (t.length < 60 && /description/i.test(t)) { h = r; cDesc = c; break; } }
    }
    if (h < 0) continue;
    const hdr = rows[h] || [], sub = rows[h + 1] || [];
    const width = Math.max(hdr.length, sub.length);
    const top = c => { for (let k = c; k >= Math.max(0, c - 3); k--) { const t = msCellText(hdr[k]); if (t) return t; } return ''; };
    let cSn = -1, cDate = -1, cLead = -1, dateScore = 0;
    for (let c = 0; c < width; c++) {
      const a = msCellText(hdr[c]), b = msCellText(sub[c]), both = (a + ' ' + b).trim();
      if (cSn < 0 && c < cDesc && MS_SN_HDR.test(a)) cSn = c;
      if (cLead < 0 && /lead\s*type/i.test(both)) cLead = c;
      let sc = 0;
      if (/planned\s*submission|submission\s*date.*plan|plan.*submi/i.test(both)) sc = 3;
      else if (/plan/i.test(both) && /submi/i.test(a || top(c))) sc = 2;
      else if (/^planned/i.test(a) && !/approv|order|deliver|install|site|purchase/i.test(top(c))) sc = 1;
      if (sc > dateScore) { dateScore = sc; cDate = c; }
    }
    if (cSn < 0) for (let c = 0; c < cDesc; c++) if (/^(no|sn|sr|s\.no|sl)/i.test(msCellText(hdr[c]))) { cSn = c; break; }
    const sheetDisc = msDiscOf(g.name);
    let disc = sheetDisc, start = h + 1, n = 0;
    // a second header row (Planned / Actual, …) has no item in it
    if (sub && !msCellText(sub[cDesc]) && sub.some(v => /plan|actual|date|status/i.test(msCellText(v)))) start = h + 2;
    for (let r = start; r < rows.length; r++) {
      const row = rows[r] || [], desc = msCellText(row[cDesc]);
      if (!desc) {
        const texts = row.map(msCellText).filter(Boolean);
        if (texts.length && texts.length <= 2 && texts[0].length <= 50) { const d = msDiscOf(texts[0]); if (d && !/^\d+$/.test(texts[0])) disc = d; }
        continue;
      }
      if (/description/i.test(desc) || /^(total|grand total)$/i.test(desc)) continue;
      const snRaw = cSn >= 0 ? msCellText(row[cSn]) : '';
      out.push({ d: disc || 'MEP', sn: /^\d+(\.0+)?$/.test(snRaw) ? String(parseInt(snRaw, 10)) : '', desc, lead: cLead >= 0 ? msCellText(row[cLead]) : '', date: cDate >= 0 ? msCellDate(row[cDate]) : '', guess: !disc });
      n++;
    }
    if (n) sheetsUsed.push(g.name);
  }
  // keys: <DISC>-<SN>; an item without an SN (or a repeated one) gets the next free number in its discipline
  const used = new Map(MS_CODES.map(c => [c, new Set()]));
  for (const r of out) { if (r.sn && !used.get(r.d).has(r.sn)) used.get(r.d).add(r.sn); else { r.rem = r.sn ? `SN ${r.sn} repeated in the planner's log` : "No SN in the planner's log"; r.sn = ''; } }
  for (const r of out) {
    if (!r.sn) { let k = 1; while (used.get(r.d).has(String(k))) k++; r.sn = String(k); used.get(r.d).add(r.sn); }
    r.k = `${r.d}-${String(r.sn).padStart(2, '0')}`;
    if (r.guess) r.rem = (r.rem ? r.rem + '; ' : '') + 'Discipline not found in the log: set to MEP';
    delete r.guess;
  }
  return { items: out, sheets: sheetsUsed };
}

/* matching the planner's materials to the method statements, through the standard's own material list */
const MS_STOP = new Set(['AND', 'OF', 'THE', 'FOR', 'WITH', 'INCL', 'INCLUDING', 'AS', 'APPLICABLE', 'TO', 'IN', 'ON', 'BY', 'OR', 'A', 'AN', 'ALL', 'ETC', 'TYPE', 'TYPES', 'NO', 'INSTALLATION', 'TESTING', 'COMMISSIONING', 'MATERIAL', 'MATERIALS', 'SUBMITTAL', 'ITEM', 'ITEMS', 'WORK', 'WORKS', 'SUPPLY', 'BASED', 'REQUIRED', 'PER', 'ALONG', 'ASSOCIATED', 'INCLUDE', 'INCLUDED', 'INCLUDES', 'COMPLETE', 'RELATED', 'SET', 'SETS']);
const MS_SYN = { CHW: ['CHILLED', 'WATER'], DUCTWORK: ['DUCT'], DUCTING: ['DUCT'], DUCTS: ['DUCT'], GENSET: ['GENERATOR'], DG: ['DIESEL', 'GENERATOR'], LIGHTNING: ['LIGHTNING'], LUMINAIRE: ['LIGHT'], LUMINAIRES: ['LIGHT'], LIGHTING: ['LIGHT'], FIXTURES: ['FIXTURE'], SWITCHBOARD: ['SWITCHGEAR'], SWITCHBOARDS: ['SWITCHGEAR'], PANELS: ['PANEL'], WIRING: ['WIRE'], DEVICES: ['ACCESSORY'], DEVICE: ['ACCESSORY'], ACCESSORIES: ['ACCESSORY'], TRAYS: ['TRAY'], CONDUITS: ['CONDUIT'], VALVES: ['VALVE'], PUMPS: ['PUMP'], FANS: ['FAN'], CABLES: ['CABLE'], WIRES: ['WIRE'], PIPES: ['PIPE'], PIPING: ['PIPE'], FITTINGS: ['FITTING'], HANGERS: ['HANGER'], SUPPORTS: ['SUPPORT'], DAMPERS: ['DAMPER'], LOUVRES: ['LOUVER'], LOUVRE: ['LOUVER'], LOUVERS: ['LOUVER'], ATTENUATORS: ['ATTENUATOR'], SPRINKLERS: ['SPRINKLER'], EXTINGUISHERS: ['EXTINGUISHER'], TANKS: ['TANK'], HEATERS: ['HEATER'], GULLY: ['DRAIN'], GULLIES: ['DRAIN'], DRAINS: ['DRAIN'], BOXES: ['BOX'], GLANDS: ['GLAND'], LUGS: ['LUG'], ISOLATOR: ['ISOLATOR'], ISOLATORS: ['ISOLATOR'], SENSORS: ['SENSOR'], DETECTORS: ['DETECTOR'], UNITS: ['UNIT'], SYSTEMS: ['SYSTEM'], AIRCRAFT: ['AIRCRAFT'], 'AIR CRAFT': ['AIRCRAFT'], CCTV: ['CCTV'], TELEPHONE: ['TELEPHONE'], DATA: ['DATA'], RESISTANCE: ['RATED'], RESISTANT: ['RATED'], CHLORINE: ['CHLORINATION'], FILTRATION: ['WATER', 'TREATMENT'], INERTIA: ['VIBRATION', 'ISOLATOR'], REFRIGERANT: ['DX', 'REFRIGERANT'], VRF: ['DX', 'VRF'], AHU: ['FAHU'], AHUS: ['FAHU'], EXHAUST: ['EXTRACT'], LADDER: ['TRAY'], LSHF: ['LSZH'], LSOH: ['LSZH'], DEVICES: ['ACCESSORY'], STANDBY: ['DIESEL'], GAUGE: ['GAUGE'], THERMOMETER: ['TEMPERATURE'], THERMOMETERS: ['TEMPERATURE'] };
function msTokens(s) {
  const t = String(s || '').toUpperCase().replace(/&/g, ' AND ').replace(/AIR\s+CRAFT/g, 'AIRCRAFT').replace(/FIRE\s+(SEALANTS?|STOP\w*)/g, 'FIRE STOPPING').replace(/BELOW\s*-?\s*GROUND|UNDER\s*GROUND|BURIED/g, 'BELOWGROUND').replace(/ABOVE\s*-?\s*GROUND/g, 'ABOVEGROUND')
    .replace(/[^A-Z0-9]+/g, ' ').trim().split(' ');
  const out = [];
  for (let w of t) {
    if (!w || MS_STOP.has(w) || /^\d+$/.test(w)) continue;
    if (MS_SYN[w]) { out.push(...MS_SYN[w]); continue; }
    if (w.length > 4 && w.endsWith('IES')) w = w.slice(0, -3) + 'Y'; else if (w.length > 3 && w.endsWith('S') && !w.endsWith('SS') && !/^(BUS|STATUS|PLUS|CAMPUS|GAS)$/.test(w)) w = w.slice(0, -1);
    if (MS_SYN[w]) { out.push(...MS_SYN[w]); continue; }
    out.push(w);
  }
  return [...new Set(out)];
}
const MS_GENERIC = new Set(['SYSTEM', 'ACCESSORY', 'UNIT', 'CONTROL', 'PANEL', 'PIPE', 'FITTING', 'EQUIPMENT', 'PACKAGE', 'ASSEMBLY', 'MANUAL', 'AUTOMATIC']);
let MS_IDX = null;
function msIndex() {
  if (MS_IDX) return MS_IDX;
  const docs = MS_STD.mats.map(([k, d, desc]) => ({ k, d, toks: msTokens(desc) }));
  const titles = MS_STD.items.map(([d, s, t], i) => ({ i, d, s, toks: msTokens(t) }));
  const df = new Map(), N = docs.length + titles.length;
  for (const x of docs.concat(titles)) for (const t of x.toks) df.set(t, (df.get(t) || 0) + 1);
  // words found nowhere in the standard say little about where an item belongs; generic words say less than names of equipment
  const w = t => Math.log(1 + N / (df.get(t) || 4)) * (MS_GENERIC.has(t) ? 0.5 : 1);
  const norm = toks => Math.sqrt(toks.reduce((a, t) => a + w(t) * w(t), 0)) || 1;
  docs.forEach(x => { x.n = norm(x.toks); }); titles.forEach(x => { x.n = norm(x.toks); });
  const byKey = new Map(); MS_STD.items.forEach(([, , , keys], i) => keys.forEach(k => { if (!byKey.has(k)) byKey.set(k, []); byKey.get(k).push(i); }));
  return (MS_IDX = { docs, titles, w, norm, byKey });
}
// half cosine, half the share of the planner's wording found in the standard's
function msSim(a, an, b, bn, w) { let s = 0; const B = new Set(b); for (const t of a) if (B.has(t)) s += w(t) * w(t); return 0.5 * s / (an * bn) + 0.5 * s / (an * an); }
const msNear = (a, b) => a === b || ((a === 'ELE' || a === 'ELV') && (b === 'ELE' || b === 'ELV')) || a === 'MEP' || b === 'MEP';
/* for one planner material: the standard items (by index in MS_STD.items) it belongs to, or [] */
function msMatch(mat) {
  const X = msIndex(), toks = msTokens(mat.desc); if (!toks.length) return { idx: [], score: 0 };
  const n = X.norm(toks);
  let best = null, bs = 0;
  for (const d of X.docs) { const s = msSim(toks, n, d.toks, d.n, X.w) * (msNear(mat.d, d.d) ? 1 : 0.7); if (s > bs) { bs = s; best = d; } }
  if (best && bs >= 0.4) return { idx: X.byKey.get(best.k) || [], score: bs, via: best.k };
  // no close standard material: the installation and T&C method statements whose titles fit best
  const pick = st => { let b = null, s0 = 0; for (const t of X.titles) if (t.s === st) { const s = msSim(toks, n, t.toks, t.n, X.w) * (msNear(mat.d, t.d) ? 1 : 0.7); if (s > s0) { s0 = s; b = t; } } return s0 >= 0.35 ? b : null; };
  const a = pick('I'), b = pick('T');
  return { idx: [a, b].filter(Boolean).map(t => t.i), score: bs, via: '' };
}
