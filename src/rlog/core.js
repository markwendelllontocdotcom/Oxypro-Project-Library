/* ---------- WIR Log and MIR Log (request logs): model ----------
   The Oxypro standard workbooks "WIR Log - Standard.xlsx" and "MIR Log - Standard.xlsx" (user, 16 Nov 2026):
   Summary, seven discipline logs (MEC, PLU, ELE, ELV, FF, LPG, MEP), the Transmittal Sheet and the hidden guide sheets.
   A log row: reference no., revision, level, location, description, planned / submitted / return dates, status, final status, remark. */
const RL_KIND = {
  wir: { key: 'wir', short: 'WIR', name: 'WIR Log', item: 'WIR', items: 'WIRs', long: 'Work Inspection Request (WIR)', title: 'WORK INSPECTION REQUEST (WIR)',
    loc: 'Location Reference\nArea/Zone/Room no.', desc: 'Description', file: 'WIR Log', pat: 'OXY-WIR-MEP-{DISC}-{NNNN}', descPh: 'Description of the work to inspect' },
  mir: { key: 'mir', short: 'MIR', name: 'MIR Log', item: 'MIR', items: 'MIRs', long: 'Material Inspection Request (MIR)', title: 'MATERIAL INSPECTION REQUEST (MIR)',
    loc: 'Delivery / Storage Location\nArea/Zone/Store', desc: 'Material Description', file: 'MIR Log', pat: 'OXY-MIR-MEP-{DISC}-{NNNN}', descPh: 'Material delivered' },
  // NCR Log and SOR Log (user's standards of 25 Nov 2026): eight logs (HSE too), statuses OPEN / CLOSED / RESUBMIT / UR, a target close-out date
  ncr: { key: 'ncr', nc: true, short: 'NCR', name: 'NCR Log', item: 'NCR', items: 'NCRs', long: 'Non Conformance Report (NCR)', title: 'NON CONFORMANCE REPORT (NCR)',
    desc: 'NCR Description', file: 'NCR Log', pat: '{CODE}-NCR-{DISC}-{NNN}', descPh: 'What does not conform', allowName: 'NCR_Allowance_Days',
    legend: [['OPEN', 'NCR OPEN - CORRECTIVE ACTION PENDING'], ['CLOSED', 'NCR CLOSED OUT'], ['RESUBMIT', 'REVISE & RESUBMIT CORRECTIVE ACTION'], ['UR', 'UNDER REVIEW BY CONSULTANT']] },
  sor: { key: 'sor', nc: true, short: 'SOR', name: 'SOR Log', item: 'SOR', items: 'SORs', long: 'Site Observation Report (SOR)', title: 'SITE OBSERVATION REPORT (SOR)',
    desc: 'SOR Description', file: 'SOR Log', pat: '{CODE}-SOR-{DISC}-{NNN}', descPh: 'What was observed', allowName: 'SOR_Allowance_Days',
    legend: [['OPEN', 'SOR OPEN - CORRECTIVE ACTION PENDING'], ['CLOSED', 'SOR CLOSED OUT'], ['RESUBMIT', 'REVISE & RESUBMIT CORRECTIVE ACTION'], ['UR', 'UNDER REVIEW BY CONSULTANT']] }
};
const RL_KINDS = ['wir', 'mir', 'ncr', 'sor'];
const rlIsNc = kind => !!(RL_KIND[kind] && RL_KIND[kind].nc);
const RL_NC_STATUS = ['OPEN', 'CLOSED', 'RESUBMIT', 'UR'];
const rlNcStatus = v => { const t = String(v == null ? '' : v).trim().toUpperCase(); return RL_NC_STATUS.includes(t) ? t : ''; };
const RL_NC_ALLOW = 14;       // days from the Received Date to the Target Close-out Date (Summary J3 of the workbook)
const RL_NC_TRN = 50;         // rows the NCR / SOR Transmittal Sheet lists
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
const RL_DISC_NC = RL_DISC.concat([{ code: 'HSE', head: 'HEALTH, SAFETY & ENVIRONMENT (HSE)', sum: 'HSE' }]);
const rlDiscs = kind => rlIsNc(kind) ? RL_DISC_NC : RL_DISC;
const rlCodes = kind => rlDiscs(kind).map(d => d.code);
const RL_BLOCK = [['client', 'CLIENT'], ['consultant', 'CONSULTANT'], ['mepConsultant', 'MEP CONSULTANT'], ['mainContractor', 'MAIN CONTRACTOR'], ['mepContractor', 'MEP CONTRACTOR']];
const RL_PART = 400;          // rows kept in one stored part
const RL_MAX = 7000;          // rows the standard's Transmittal Sheet reads from each log (rows 12 to 7011)
const RL_TPL_ROWS = 50;       // rows the standard has ready in each log

const rlBlankItem = (d, ref, kind) => rlIsNc(kind)
  ? { id: msId(), d, ref: ref || '', rev: '0', desc: '', rec: '', close: '', resp: '', st: '', fin: '', rem: '' }
  : { id: msId(), d, ref: ref || '', rev: '0', lvl: '', loc: '', desc: '', plan: '', sub: '', ret: '', st: '', fin: '', rem: '' };
function rlDefaultBlock(p) {
  const b = msDefaultBlock(p || {}), get = re => { const r = b.find(x => re.test(x.label)); return r ? r.value : ''; };
  return { title: b[0] ? b[0].value : msUp(p && p.name), client: get(/^CLIENT$/i), consultant: get(/^CONSULTANT$/i), mepConsultant: get(/^MEP CONSULTANT$/i),
    mainContractor: get(/^(MAIN )?CONTRACTOR$/i), mepContractor: get(/^MEP CONTRACTOR$/i) || 'OXYPRO ELECTROMECHANICAL WORK LLC' };
}
const rlDefaultPat = (kind, p) => RL_KIND[kind].pat.replace('{CODE}', msUp((p && (p.code || p.no)) || 'PRJ'));
function rlNewLog(kind, p) { const log = { kind, v: 1, rev: '00', pat: rlDefaultPat(kind, p), block: rlDefaultBlock(p), items: [] }; if (rlIsNc(kind)) log.allow = RL_NC_ALLOW; return log; }
function rlClean(kind, x, p) {
  const s = v => String(v == null ? '' : v), d0 = rlDefaultBlock(p), b = (x && x.block) || {}, nc = rlIsNc(kind), codes = rlCodes(kind);
  const block = { title: s(b.title != null ? b.title : d0.title).slice(0, 400) };
  for (const [k] of RL_BLOCK) block[k] = s(b[k] != null ? b[k] : d0[k]).slice(0, 400);
  const items = (Array.isArray(x && x.items) ? x.items : []).filter(it => it && codes.includes(it.d)).map(it => nc
    ? { id: s(it.id) || msId(), d: it.d, ref: s(it.ref).slice(0, 120), rev: s(it.rev).slice(0, 10), desc: s(it.desc).slice(0, 600),
        rec: msIso(it.rec), close: msIso(it.close), resp: msIso(it.resp), st: rlNcStatus(it.st), fin: rlNcStatus(it.fin), rem: s(it.rem).slice(0, 400) }
    : { id: s(it.id) || msId(), d: it.d, ref: s(it.ref).slice(0, 120), rev: s(it.rev).slice(0, 10), lvl: s(it.lvl).slice(0, 60), loc: s(it.loc).slice(0, 200), desc: s(it.desc).slice(0, 600),
        plan: msIso(it.plan), sub: msIso(it.sub), ret: msIso(it.ret), st: msStatus(it.st), fin: msStatus(it.fin), rem: s(it.rem).slice(0, 400) });
  const log = { kind, v: 1, rev: s((x && x.rev) || '00').slice(0, 10), pat: s((x && x.pat) || rlDefaultPat(kind, p)).slice(0, 80), block, items,
    updatedAt: (x && x.updatedAt) || '', createdAt: (x && x.createdAt) || '' };
  if (nc) { const a = parseInt(x && x.allow, 10); log.allow = a >= 0 && a <= 365 ? a : RL_NC_ALLOW; }
  return log;
}
// NCR / SOR: the dates the workbook works out
const rlTarget = (it, allow) => { const d = msDay(it.rec); return d == null ? '' : msFromDay(d + allow); };
const rlElapsed = it => { const a = msDay(it.rec), b = msDay(it.close); return a != null && b != null ? b - a : ''; };
const rlRespDays = it => { const c = msDay(it.close); if (c == null) return ''; const r = msDay(it.resp); return Math.max(0, (r == null ? msToday() : r) - c); };
const rlItemsOf = (log, d) => log.items.filter(it => it.d === d);
// as the workbook counts them: by Final Status (column M); the total is the sum of the six codes
function rlCounts(items, kind, allow) {
  const t0 = msToday();
  if (rlIsNc(kind)) {                       // Overdue = OPEN or RESUBMIT past the target date; Closure = CLOSED / total; average of the close-out days
    const c = { OPEN: 0, CLOSED: 0, RESUBMIT: 0, UR: 0, n: items.length, overdue: 0, days: 0, nd: 0 };
    for (const it of items) {
      if (c[it.fin] != null && it.fin) c[it.fin]++;
      const tg = msDay(rlTarget(it, allow == null ? RL_NC_ALLOW : allow)); if (tg != null && tg < t0 && (it.fin === 'OPEN' || it.fin === 'RESUBMIT')) c.overdue++;
      const el = rlElapsed(it); if (el !== '') { c.days += el; c.nd++; }
    }
    c.sub = c.OPEN + c.CLOSED + c.RESUBMIT + c.UR; c.closure = c.sub ? c.CLOSED / c.sub : 0; c.avg = c.nd ? c.days / c.nd : 0;
    return c;
  }
  const c = { A: 0, B: 0, C: 0, D: 0, E: 0, UR: 0, n: items.length, overdue: 0, soon: 0 };
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
function rlOnDay(log, iso) {
  const out = []; if (!msIso(iso)) return out;
  // WIR / MIR: the requests submitted that day. NCR / SOR: the reports closed out that day (the closure submittal), 50 at most as in the workbook
  const nc = rlIsNc(log.kind);
  for (const d of rlCodes(log.kind)) for (const it of rlItemsOf(log, d)) if ((nc ? it.close : it.sub) === iso) out.push(it);
  return nc ? out.slice(0, RL_NC_TRN) : out;
}
