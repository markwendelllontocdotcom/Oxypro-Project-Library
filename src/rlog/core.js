/* ---------- WIR Log and MIR Log (request logs): model ----------
   The Oxypro standard workbooks "WIR Log - Standard.xlsx" and "MIR Log - Standard.xlsx" (user, 16 Nov 2026):
   Summary, seven discipline logs (MEC, PLU, ELE, ELV, FF, LPG, MEP), the Transmittal Sheet and the hidden guide sheets.
   A log row: reference no., revision, level, location, description, planned / submitted / return dates, status, final status, remark. */
const RL_KIND = {
  wir: { key: 'wir', short: 'WIR', name: 'WIR Log', item: 'WIR', items: 'WIRs', long: 'Work Inspection Request (WIR)', title: 'WORK INSPECTION REQUEST (WIR)',
    loc: 'Location Reference\nArea/Zone/Room no.', desc: 'Description', file: 'WIR Log', pat: 'OXY-WIR-MEP-{DISC}-{NNNN}', descPh: 'Description of the work to inspect' },
  mir: { key: 'mir', short: 'MIR', name: 'MIR Log', item: 'MIR', items: 'MIRs', long: 'Material Inspection Request (MIR)', title: 'MATERIAL INSPECTION REQUEST (MIR)',
    loc: 'Delivery / Storage Location\nArea/Zone/Store', desc: 'Material Description', file: 'MIR Log', pat: 'OXY-MIR-MEP-{DISC}-{NNNN}', descPh: 'Material delivered' }
};
// the discipline sheets, in the workbook's order; head = the name printed in C9 of the sheet, sum = the row of the Summary
const RL_DISC = [
  { code: 'MEC', head: 'MECHANICAL (HVAC)', sum: 'HVAC' },
  { code: 'PLU', head: 'PLUMBING & DRAINAGE', sum: 'PLUMBING' },
  { code: 'ELE', head: 'ELECTRICAL', sum: 'ELECTRICAL' },
  { code: 'ELV', head: 'ELV SYSTEMS', sum: 'ELV' },
  { code: 'FF', head: 'FIRE FIGHTING', sum: 'FIRE FIGHTING' },
  { code: 'LPG', head: 'LPG', sum: 'LPG' },
  { code: 'MEP', head: 'MEP', sum: 'MEP' }
];
const RL_CODES = RL_DISC.map(d => d.code);
const RL_BLOCK = [['client', 'CLIENT'], ['consultant', 'CONSULTANT'], ['mepConsultant', 'MEP CONSULTANT'], ['mainContractor', 'MAIN CONTRACTOR'], ['mepContractor', 'MEP CONTRACTOR']];
const RL_PART = 400;          // rows kept in one stored part
const RL_MAX = 7000;          // rows the standard's Transmittal Sheet reads from each log (rows 12 to 7011)
const RL_TPL_ROWS = 50;       // rows the standard has ready in each log

const rlBlankItem = (d, ref) => ({ id: msId(), d, ref: ref || '', rev: '0', lvl: '', loc: '', desc: '', plan: '', sub: '', ret: '', st: '', fin: '', rem: '' });
function rlDefaultBlock(p) {
  const b = msDefaultBlock(p || {}), get = re => { const r = b.find(x => re.test(x.label)); return r ? r.value : ''; };
  return { title: b[0] ? b[0].value : msUp(p && p.name), client: get(/^CLIENT$/i), consultant: get(/^CONSULTANT$/i), mepConsultant: get(/^MEP CONSULTANT$/i),
    mainContractor: get(/^(MAIN )?CONTRACTOR$/i), mepContractor: get(/^MEP CONTRACTOR$/i) || 'OXYPRO ELECTROMECHANICAL WORK LLC' };
}
function rlNewLog(kind, p) { return { kind, v: 1, rev: '00', pat: RL_KIND[kind].pat, block: rlDefaultBlock(p), items: [] }; }
function rlClean(kind, x, p) {
  const s = v => String(v == null ? '' : v), d0 = rlDefaultBlock(p), b = (x && x.block) || {};
  const block = { title: s(b.title != null ? b.title : d0.title).slice(0, 400) };
  for (const [k] of RL_BLOCK) block[k] = s(b[k] != null ? b[k] : d0[k]).slice(0, 400);
  const items = (Array.isArray(x && x.items) ? x.items : []).filter(it => it && RL_CODES.includes(it.d)).map(it => ({
    id: s(it.id) || msId(), d: it.d, ref: s(it.ref).slice(0, 120), rev: s(it.rev).slice(0, 10), lvl: s(it.lvl).slice(0, 60), loc: s(it.loc).slice(0, 200), desc: s(it.desc).slice(0, 600),
    plan: msIso(it.plan), sub: msIso(it.sub), ret: msIso(it.ret), st: msStatus(it.st), fin: msStatus(it.fin), rem: s(it.rem).slice(0, 400) }));
  return { kind, v: 1, rev: s((x && x.rev) || '00').slice(0, 10), pat: s((x && x.pat) || RL_KIND[kind].pat).slice(0, 80), block, items,
    updatedAt: (x && x.updatedAt) || '', createdAt: (x && x.createdAt) || '' };
}
const rlItemsOf = (log, d) => log.items.filter(it => it.d === d);
// as the workbook counts them: by Final Status (column M); the total is the sum of the six codes
function rlCounts(items) {
  const c = { A: 0, B: 0, C: 0, D: 0, E: 0, UR: 0, n: items.length, overdue: 0, soon: 0 }, t0 = msToday();
  for (const it of items) {
    if (c[it.fin] != null && it.fin !== 'n/a' && it.fin) c[it.fin]++;
    const pd = msDay(it.plan); if (pd != null && !it.sub) { if (pd < t0) c.overdue++; else if (pd - t0 <= 7) c.soon++; }
  }
  c.sub = c.A + c.B + c.C + c.D + c.E + c.UR; c.re = c.C + c.D;
  return c;
}
// the next reference number of a discipline, from the log's pattern ({DISC} the sheet code, {N...} the running number)
function rlRefParts(pat, d) {
  const m = String(pat || '').match(/^(.*?)\{(N+)\}(.*)$/i);
  const fill = t => t.replace(/\{DISC\}/gi, d);
  return m ? { pre: fill(m[1]), n: m[2].length, post: fill(m[3]) } : { pre: fill(String(pat || '')) + (pat ? '-' : ''), n: 4, post: '' };
}
function rlNextRef(log, d) {
  const { pre, n, post } = rlRefParts(log.pat, d);
  let max = 0;
  for (const it of log.items) {
    if (it.d !== d) continue;
    const r = it.ref.trim();
    if (r.length > pre.length + post.length && r.toUpperCase().startsWith(pre.toUpperCase()) && r.toUpperCase().endsWith(post.toUpperCase())) {
      const mid = r.slice(pre.length, r.length - post.length); if (/^\d+$/.test(mid)) max = Math.max(max, +mid);
    }
  }
  return pre + String(max + 1).padStart(n, '0') + post;
}
// rows of a day for the Transmittal Sheet: as the workbook, the requests whose Submitted Date is that day, sheet by sheet
function rlOnDay(log, iso) { const out = []; if (!msIso(iso)) return out; for (const d of RL_CODES) for (const it of rlItemsOf(log, d)) if (it.sub === iso) out.push(it); return out; }
