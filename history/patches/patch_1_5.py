"""v1.5.0: project summary page (last page) with selectable details; new Master List columns kept as extra details."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('Version 1.4.0 (27 Oct 2026)', 'Version 1.5.0 (27 Oct 2026)')
rep(".check-row{display:flex;align-items:center;gap:10px;font-size:14px}",
    """.check-row{display:flex;align-items:center;gap:10px;font-size:14px}
.checks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px 12px}
.checks .check-row{font-size:13.5px;gap:8px;align-items:flex-start;line-height:1.3}
.checks .check-row input{margin-top:1px;flex:none}
.sum-actions{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.flabel.sub{font-size:12.5px;color:var(--muted);margin-top:4px}
.pager{display:flex;align-items:center;gap:8px;font-size:13.5px;color:var(--muted)}""")
# state
rep("  view: 'library', pres: { sheets: [], cur: 0, dirty: new Set(), cover: null }, coverDesign: 'A',",
    "  view: 'library', pres: { sheets: [], cur: 0, dirty: new Set(), cover: null, summary: null }, coverDesign: 'A',\n  extraCols: [], summaryCols: lsGet('summaryCols'),")
rep("  S.pres.sheets = sheets; S.pres.cover = mergeCover(S.pres.cover, sheets); S.pres.cur = -1;",
    "  S.pres.sheets = sheets; S.pres.cover = mergeCover(S.pres.cover, sheets);\n  S.pres.summary = { include: true, title: (S.pres.summary && S.pres.summary.title) || 'Project Summary', page: 0 };\n  S.pres.cur = -1;")

# ---------- extra Master List columns ----------
rep("function changedKeys(r) {\n  const p = S.projects.get(r.no); if (!p) return [];\n  return Object.keys(r).filter(k => k !== 'no' && r[k] && r[k] !== String(p[k] == null ? '' : p[k]));\n}",
    """function changedKeys(r) {
  const p = S.projects.get(r.no); if (!p) return [];
  const out = Object.keys(r).filter(k => k !== 'no' && k !== 'extra' && r[k] && r[k] !== String(p[k] == null ? '' : p[k]));
  for (const [k, v] of Object.entries(r.extra || {})) if (v && v !== String(((p.extra || {})[k]) == null ? '' : p.extra[k])) out.push('x:' + k);
  return out;
}
// columns of the Master List the library has no field for are kept as extra details
const slugKey = t => String(t).toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 60);
const SKIP_HDR = /^(s\\.?\\s?no\\.?|sr\\.?\\s?no\\.?|sl\\.?\\s?no\\.?|#|no\\.?|serial( no\\.?)?)$/i;
function extraList() {
  const out = S.extraCols.filter(c => c && c.key).slice(), seen = new Set(out.map(c => c.key));
  for (const p of S.projects.values()) for (const k of Object.keys(p.extra || {})) if (!seen.has(k)) { seen.add(k); out.push({ key: k, label: k.replace(/_/g, ' ') }); }
  return out;
}""")
rep("""      grid[hi].forEach((c, i) => { const h = String(c).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim(); if (!h) return; const hit = COLMAP.find(([k, t]) => !taken.has(k) && t(h)); if (hit) { cols[hit[0]] = i; taken.add(hit[0]); } });""",
    """      const xcols = [], xkeys = new Set();
      grid[hi].forEach((c, i) => {
        const h = String(c).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim(); if (!h) return;
        const hit = COLMAP.find(([k, t]) => !taken.has(k) && t(h)); if (hit) { cols[hit[0]] = i; taken.add(hit[0]); return; }
        const label = String(c).replace(/\\s+/g, ' ').trim(), key = slugKey(label);
        if (key && !SKIP_HDR.test(label) && !xkeys.has(key)) { xkeys.add(key); xcols.push({ i, key, label }); }
      });""")
rep("""        for (const k of Object.keys(cols)) if (k !== 'no') d[k] = cleanCell(k, r[cols[k]]);""",
    """        for (const k of Object.keys(cols)) if (k !== 'no') d[k] = cleanCell(k, r[cols[k]]);
        d.extra = {}; for (const xc of xcols) { const v = cleanCell(/date/i.test(xc.label) ? 'startDate' : 'x', r[xc.i]); if (v) d.extra[xc.key] = v; }""")
rep("      if (!best || rows.length > best.rows.length) best = { sheet: name, rows, cols };",
    "      if (!best || rows.length > best.rows.length) best = { sheet: name, rows, cols, xcols };")
rep("  S.imp = { file: file.name, sheet: best.sheet, rows: [...seen.values()], cols: Object.keys(best.cols), update: true };",
    "  S.imp = { file: file.name, sheet: best.sheet, rows: [...seen.values()], cols: Object.keys(best.cols), xcols: best.xcols, update: true };")
rep("""      <p class="d-note" style="margin:0">Columns read: ${esc(joinAnd(I.cols.map(k => XL_LABEL[k])))}.</p>""",
    """      <p class="d-note" style="margin:0">Columns read: ${esc(joinAnd(I.cols.map(k => XL_LABEL[k]).concat(I.xcols.map(c => c.label))))}.</p>
      ${(() => { const known = new Set(extraList().map(c => c.key)), nw = I.xcols.filter(c => !known.has(c.key)); return nw.length ? `<p class="d-note" style="margin:0">New column${nw.length === 1 ? '' : 's'} kept as extra project details and offered in the summary page: ${esc(joinAnd(nw.map(c => c.label)))}.</p>` : ''; })()}""")
rep("""  const todo = I.rows.filter(r => !S.projects.has(r.no) || (I.update && changedKeys(r).length));
  try {""",
    """  const todo = I.rows.filter(r => !S.projects.has(r.no) || (I.update && changedKeys(r).length));
  try {
    const known = new Set(S.extraCols.map(c => c.key)), nw = I.xcols.filter(c => !known.has(c.key));
    if (nw.length) {
      const extra = S.extraCols.concat(nw.map(c => ({ key: c.key, label: c.label })));
      await DB.doc('settings/columns').set({ extra, updatedAt: now }); S.extraCols = extra;
    }""")
rep("        const upd = {}; for (const k of changedKeys(r)) upd[k] = r[k];",
    "        const upd = {}; for (const k of changedKeys(r)) { if (k.startsWith('x:')) { upd.extra = upd.extra || {}; upd.extra[k.slice(2)] = r.extra[k.slice(2)]; } else upd[k] = r[k]; }")
rep("        Object.keys(XL_LABEL).forEach(k => { if (k !== 'no') d[k] = r[k] || ''; });",
    "        Object.keys(XL_LABEL).forEach(k => { if (k !== 'no') d[k] = r[k] || ''; }); d.extra = r.extra || {};")
# export: Master List columns, extra columns, then the library's own Scope Type and photo count
a = s.index("async function exportXlsx() {"); b = s.index("async function saveFile(filename, blob) {")
s = s[:a] + r"""async function exportXlsx() {
  const btn = $('#btn-export'); btn.disabled = true;
  try {
    await loadScript(LIBS.xlsx);
    const a = sortedNos(S.projects).map(no => S.projects.get(no));
    const cols = XL_COLS.filter(c => c[0] !== 'scopeType').concat(extraList().map(c => ['x:' + c.key, c.label, 18]), XL_COLS.filter(c => c[0] === 'scopeType'));
    const get = (p, k) => { const v = k.startsWith('x:') ? (p.extra || {})[k.slice(2)] : p[k]; return String(v == null ? '' : v); };
    const head = cols.map(c => c[1]).concat('Photos in Library');
    const aoa = [['Oxypro Electromechanical Works LLC - Projects Master List'], [], head]
      .concat(a.map(p => cols.map(([k]) => get(p, k)).concat(photosOf(p).filter(Boolean).length)));
    const ws = XLSX.utils.aoa_to_sheet(aoa);
    a.forEach((p, i) => {
      const r = i + 3;
      cols.forEach(([k], c) => {
        const addr = XLSX.utils.encode_cell({ r, c }); const v = get(p, k).trim();
        if (DATE_KEYS.includes(k) || (k.startsWith('x:') && /^\d{4}-\d{2}-\d{2}$/.test(v))) { const n = isoToSerial(v); if (n != null) ws[addr] = { t: 'n', v: n, z: 'dd-mmm-yyyy' }; }
        else if (k === 'value' && isNum(v)) ws[addr] = { t: 'n', v: Number(v.replace(/,/g, '')), z: '#,##0' };
        else if (k === 'duration' && /^\d+(\.\d+)?$/.test(v)) ws[addr] = { t: 'n', v: Number(v) };
      });
    });
    ws['!cols'] = cols.map(c => ({ wch: c[2] })).concat({ wch: 10 });
    ws['!merges'] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: head.length - 1 } }];
    ws['!autofilter'] = { ref: XLSX.utils.encode_range({ s: { r: 2, c: 0 }, e: { r: a.length + 2, c: head.length - 1 } }) };
    const wb = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, ws, 'OXYPRO PROJECT MASTER CASE');
    const buf = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
    await saveFile(`Oxypro - Projects Master List - ${today()}.xlsx`, new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
  } catch (e) { toast('The Excel file could not be made: ' + (e.message || e)); }
  finally { btn.disabled = false; }
}
""" + s[b:]
# library: search, detail panel and edit form show the extra details
rep("p.scopeType, p.scope, p.year, p.status].join(' ').toLowerCase();",
    "p.scopeType, p.scope, p.year, p.status].concat(Object.values(p.extra || {})).join(' ').toLowerCase();")
rep("${dRow('Start date', fmtDate(p.startDate))}${dRow('Handover date', fmtDate(p.handoverDate))}",
    "${dRow('Start date', fmtDate(p.startDate))}${dRow('Handover date', fmtDate(p.handoverDate))}\n        ${extraList().map(c => dRow(c.label, fmtDate((p.extra || {})[c.key]))).join('')}")
rep("""    return `<div class="field${full ? ' full' : ''}"><label for="${id}">${esc(label)}</label>${ctl}${hint}</div>`;
  }).join('');""",
    """    return `<div class="field${full ? ' full' : ''}"><label for="${id}">${esc(label)}</label>${ctl}${hint}</div>`;
  }).join('') + (extraList().length ? '<div class="fieldset-title">More details from the Master List</div>' + extraList().map((c, i) =>
    `<div class="field"><label for="e-x${i}">${esc(c.label)}</label><input class="inp" id="e-x${i}" name="x:${esc(c.key)}" value="${esc(p ? ((p.extra || {})[c.key] || '') : '')}"></div>`).join('') : '');""")
rep("    EDIT_FIELDS.forEach(([k]) => { if (k !== '_h') d[k] = String(fd.get(k) || '').trim(); });",
    "    EDIT_FIELDS.forEach(([k]) => { if (k !== '_h') d[k] = String(fd.get(k) || '').trim(); });\n    d.extra = {}; for (const c of extraList()) d.extra[c.key] = String(fd.get('x:' + c.key) || '').trim();")

# ---------- presentation: summary page in the rail, stage and form ----------
rep("""function renderPres() {
  const n = S.pres.sheets.length, cv = S.pres.cover;
  $('#pres-count').textContent = `${cv && cv.include ? 'Top sheet + ' : ''}${n} project sheet${n === 1 ? '' : 's'} · A4 landscape`;
  renderRail(); $('#chooser').hidden = true;
  const onCover = S.pres.cur === -1;
  $('#sheet-wrap').classList.toggle('excluded', onCover && !cv.include); $('#sheet-wrap').classList.remove('cover-photo');""",
    """function renderPres() {
  const n = S.pres.sheets.length, cv = S.pres.cover, sm = S.pres.summary;
  $('#pres-count').textContent = `${cv && cv.include ? 'Top sheet + ' : ''}${n} project sheet${n === 1 ? '' : 's'}${sm && sm.include ? ' + summary' : ''} · A4 landscape`;
  renderRail(); $('#chooser').hidden = true;
  const onCover = S.pres.cur === -1, onSum = S.pres.cur === -2;
  $('#sheet-wrap').classList.toggle('excluded', (onCover && !cv.include) || (onSum && !sm.include)); $('#sheet-wrap').classList.remove('cover-photo');
  if (onSum) {
    $('#stage-hint').textContent = 'The summary is the last page of the PDF and PowerPoint. Its rows follow the order of the sheets; long lists continue on a second page.';
    $('#slots').innerHTML = ''; buildSummary(); renderSummaryForm(); return;
  }""")
rep("""    + '<button type="button" class="btn btn-sm" data-add-more style="align-self:flex-start">Add projects</button>';""",
    """    + summaryRailItem() + '<button type="button" class="btn btn-sm" data-add-more style="align-self:flex-start">Add projects</button>';""")
rep("""    if (e.target.dataset.ck) { coverInput(e.target); return; }""",
    """    if (e.target.dataset.sk || e.target.dataset.scol) { summaryInput(e.target); return; }
    if (e.target.dataset.ck) { coverInput(e.target); return; }""")
rep("""    if (e.target.closest('[data-set-default]')) return setDefaultDesign();""",
    """    if (e.target.closest('[data-set-default]')) return setDefaultDesign();
    if (e.target.closest('[data-sum-all]')) return setSummaryCols(sumCatalog().map(c => c.key));
    if (e.target.closest('[data-sum-default]')) return setSummaryCols(SUM_DEFAULT.slice());
    const pg = e.target.closest('[data-sum-page]'); if (pg) { S.pres.summary.page += +pg.dataset.sumPage; buildSummary(); renderSummaryForm(); return; }""")
# outputs
rep("    const blob = await buildPdf(S.pres.sheets, S.pres.cover && S.pres.cover.include ? S.pres.cover : null);",
    "    const blob = await buildPdf(S.pres.sheets, S.pres.cover && S.pres.cover.include ? S.pres.cover : null, summaryOut());")
rep("async function buildPdf(sheets, cover) {", "async function buildPdf(sheets, cover, summary) {")
rep("""  doc.setProperties({ title: sheets.length === 1 ? `Oxypro Project Details - ${sheets[0].name}` : 'Oxypro Project References', author: 'Oxypro Electromechanical Works LLC', creator: 'Oxypro Project Library 1.0.0',""",
    """  for (const pg of summary || []) { doc.addPage('a4', 'landscape'); await specPdf(doc, pg); }
  doc.setProperties({ title: sheets.length === 1 ? `Oxypro Project Details - ${sheets[0].name}` : 'Oxypro Project References', author: 'Oxypro Electromechanical Works LLC', creator: 'Oxypro Project Library',""")
rep("    const blob = await buildPptx(S.pres.sheets, S.pres.cover && S.pres.cover.include ? S.pres.cover : null);",
    "    const blob = await buildPptx(S.pres.sheets, S.pres.cover && S.pres.cover.include ? S.pres.cover : null, summaryOut());")
rep("async function buildPptx(sheets, cover) {", "async function buildPptx(sheets, cover, summary) {")
rep("  return await pptx.write({ outputType: 'blob' });",
    "  for (const pg of summary || []) { const sl = pptx.addSlide(); sl.background = { color: 'FFFFFF' }; await specPptx(pptx, sl, pg, I, strip); }\n  return await pptx.write({ outputType: 'blob' });")
# settings subscriptions
rep("  DB.doc('settings/cover').onSnapshot(snap => {",
    """  DB.doc('settings/columns').onSnapshot(snap => {
    const d = snap.exists ? snap.data() : null;
    S.extraCols = d && Array.isArray(d.extra) ? d.extra.filter(c => c && typeof c.key === 'string' && c.key).map(c => ({ key: c.key, label: String(c.label || c.key) })) : [];
    renderDetail(); if (S.view === 'pres' && S.pres.cur === -2) { buildSummary(); renderSummaryForm(); }
  }, () => {});
  DB.doc('settings/summary').onSnapshot(snap => {
    const d = snap.exists ? snap.data() : null; if (!d || !Array.isArray(d.cols)) return;
    S.summaryCols = d.cols.filter(k => typeof k === 'string');
    if (S.view === 'pres' && S.pres.cur === -2 && !document.activeElement.closest('#sheet-form')) { buildSummary(); renderSummaryForm(); }
  }, () => {});
  DB.doc('settings/cover').onSnapshot(snap => {""")

SUMMARY = r"""/* ---------- project summary (last page) ---------- */
const SUM_BASE = [['no', 'Project No'], ['name', 'Project / Building Name'], ['sectors', 'Sector'], ['levels', 'Level / Floors'], ['area', 'Area'], ['emirate', 'Emirate'],
  ['mainContractor', 'Main Contractor'], ['mepConsultant', 'MEP Consultant'], ['leadConsultant', 'Lead Consultant'], ['client', 'Client'], ['scope', 'Scope of Work'],
  ['standards', 'Standards / Authorities'], ['value', 'Contract Value'], ['duration', 'Duration'], ['startDate', 'Start Date'], ['handoverDate', 'Handover Date'],
  ['year', 'Year'], ['status', 'Status'], ['scopeType', 'Scope Type']];
const SUM_DEFAULT = ['no', 'name', 'area', 'client', 'mainContractor', 'mepConsultant', 'year', 'status'];
const SHEET_KEY = { name: 'name', sectors: 'sector', area: 'location', client: 'client', mainContractor: 'mc', levels: 'building', scopeType: 'scopeType', value: 'value', duration: 'duration', scope: 'scope' };
const STATUS_INK = { 'Completed': '#1E7046', 'Handover Stage': '#1D5C96', 'Ongoing': '#87570A' };
const SUM_GEO = { x: 1.3, w: 27.1, top: 4.15, bottom: 19.5, padX: 0.17, padY: 0.13 };
function sumCatalog() { return SUM_BASE.map(([key, label]) => ({ key, label })).concat(extraList().map(c => ({ key: 'x:' + c.key, label: c.label, extra: true }))); }
function sumCols() { const sel = new Set(S.summaryCols || SUM_DEFAULT); return sumCatalog().filter(c => sel.has(c.key)); }
function sumCell(key, sh) {
  const p = S.projects.get(sh.no) || {};
  let v = key === 'no' ? sh.no : key.startsWith('x:') ? (p.extra || {})[key.slice(2)] : SHEET_KEY[key] ? sh[SHEET_KEY[key]] : p[key];
  v = String(v == null ? '' : v).replace(/\s+/g, ' ').trim();
  if (!v) return '–';
  if (/^(n\/?a|not applicable)$/i.test(v)) return 'N/A';
  if (key === 'value') return fmtValue(v);
  if (key === 'duration') return fmtDuration(v);
  if (key === 'emirate') return EMIRATES[v] || v;
  return fmtDate(v);
}
// column widths: what the content needs, capped, then scaled to the table width
function sumWidths(cols, rows, pt) {
  const W = SUM_GEO.w, pad = 2 * SUM_GEO.padX, hf = { font: 'Carlito', bold: true, pt: pt - 0.5, ls: 0.06 };
  const MIN = { no: 1.45, year: 1.55, emirate: 1.9, status: 2.45, duration: 2.1, value: 2.7, startDate: 2.25, handoverDate: 2.25 };
  const CAP = { name: 6.4, scope: 8, area: 6.2, client: 5.4, mainContractor: 5.4, mepConsultant: 5.2 };
  const FLEX = new Set(['name', 'area', 'scope', 'client', 'mainContractor', 'mepConsultant', 'leadConsultant', 'standards', 'sectors', 'levels']);
  const nat = cols.map((c, i) => {
    const longest = Math.max(...c.label.toUpperCase().split(' ').map(wd => textW(wd, hf))) + pad;
    const cw = rows.map(r => textW(r[i], { font: 'Carlito', bold: c.key === 'no', pt })).sort((a, b) => a - b);
    const p90 = cw.length ? cw[Math.min(cw.length - 1, Math.floor(cw.length * 0.9))] : 0;
    const min = Math.max(MIN[c.key] || 2.0, Math.min(longest, 3.0));
    return { min, want: Math.max(min, Math.min(p90 + pad, CAP[c.key] || 5.0)), flex: FLEX.has(c.key) || c.key.startsWith('x:') };
  });
  const sum = a => a.reduce((t, v) => t + v, 0), total = sum(nat.map(n => n.want));
  if (total <= W) {
    const fl = nat.filter(n => n.flex), base = fl.length ? fl : nat, bw = sum(base.map(n => n.want));
    return { fit: true, w: nat.map(n => n.want + (base.includes(n) ? (W - total) * n.want / bw : 0)) };
  }
  const slack = sum(nat.map(n => n.want - n.min)), need = total - W;
  if (slack >= need) return { fit: true, w: nat.map(n => n.want - (n.want - n.min) * need / slack) };
  const mins = sum(nat.map(n => n.min));
  return { fit: false, w: nat.map(n => n.min * W / mins) };
}
function summaryPages(cfg, sheets) {
  const cols = sumCols(); if (!cols.length || !sheets.length) return [];
  const rows = sheets.map(sh => cols.map(c => sumCell(c.key, sh)));
  let pt = cols.length <= 6 ? 9.5 : cols.length <= 8 ? 9 : cols.length <= 10 ? 8.5 : cols.length <= 13 ? 7.5 : 7, wd;
  for (;;) { wd = sumWidths(cols, rows, pt); if (wd.fit || pt <= 6.5) break; pt -= 0.5; }
  const G = SUM_GEO, pad = G.padX, lh = 1.2, line = pt * lh * PT, hpt = pt - 0.5, hline = hpt * lh * PT;
  const xs = []; wd.w.reduce((x, w) => (xs.push(x), x + w), G.x);
  const hf = { font: 'Carlito', bold: true, pt: hpt, ls: 0.06 };
  const head = cols.map((c, i) => wrap(c.label.toUpperCase(), `700 ${hpt}pt Carlito`, (wd.w[i] - 2 * pad - hpt * 0.06 * PT * 12) * CM, 2));
  const hh = Math.max(...head.map(l => l.length)) * hline + 2 * G.padY;
  const cells = rows.map(r => r.map((t, i) => wrap(t, `${cols[i].key === 'no' ? '700 ' : ''}${pt}pt Carlito`, (wd.w[i] - 2 * pad) * CM, cols[i].key === 'scope' ? 3 : 4)));
  const rh = cells.map(r => Math.max(...r.map(l => l.length)) * line + 2 * G.padY);
  const n = sheets.length, date = (S.pres.cover && S.pres.cover.date) || (MONTHS[new Date().getMonth()] + ' ' + new Date().getFullYear());
  const pages = []; let i = 0;
  while (i < rows.length) {
    const T = [], R = [], first = !pages.length;
    T.push({ str: 'PROJECT SUMMARY', x: G.x, y: 1.2, w: 14, font: 'Carlito', bold: true, pt: 8.5, ls: 0.14, color: CRED });
    T.push({ lines: wrap(`${cfg.title || 'Project Summary'}${first ? '' : ' (continued)'}`, '24pt Caladea', 20 * CM, 1), x: G.x, y: 1.65, w: 20, font: 'Caladea', pt: 24, lh: 1.08, color: '#1F2733' });
    T.push({ str: `${n} project${n === 1 ? '' : 's'}  ·  ${date}`, x: G.x, y: 2.75, w: 14, font: 'Carlito', pt: 10.5, color: '#566070' });
    R.push({ x: G.x, y: 3.5, w: 2.0, h: 0.11, color: CRED });
    let y = G.top;
    R.push({ x: G.x, y, w: G.w, h: hh, color: NAVY });
    head.forEach((ls, k) => T.push({ lines: ls, x: xs[k] + pad, y: y + G.padY, w: wd.w[k] - 2 * pad, font: 'Carlito', bold: true, pt: hpt, ls: 0.06, color: '#FFFFFF' }));
    y += hh;
    let k = 0;
    while (i < rows.length && (k === 0 || y + rh[i] <= G.bottom)) {
      if (i % 2) R.push({ x: G.x, y, w: G.w, h: rh[i], color: '#F3F5F8' });
      R.push({ x: G.x, y: y + rh[i] - 0.015, w: G.w, h: 0.015, color: '#DDE2E9' });
      cells[i].forEach((ls, c) => {
        const key = cols[c].key, txt = rows[i][c];
        T.push({ lines: ls, x: xs[c] + pad, y: y + G.padY, w: wd.w[c] - 2 * pad, font: 'Carlito', bold: key === 'no', pt, lh,
          color: txt === '–' ? '#9AA3AF' : key === 'no' ? NAVY : key === 'status' ? (STATUS_INK[txt] || '#2B2B2B') : '#2B2B2B' });
      });
      y += rh[i]; i++; k++;
    }
    pages.push({ texts: T, rects: R, logo: { dark: false, x: 28.4 - 1.15 * LOGO_AR, y: 1.25, h: 1.15 } });
  }
  pages.forEach((pg, j) => {
    pg.rects.push({ x: G.x, y: 19.95, w: G.w, h: 0.02, color: '#C9D1DC' });
    pg.texts.push({ str: `${COMPANY.name}  ·  ${COMPANY.web}`, x: G.x, y: 20.1, w: 18, font: 'Carlito', pt: 8, color: '#6E7785' });
    if (pages.length > 1) pg.texts.push({ str: `Page ${j + 1} of ${pages.length}`, x: 20.4, y: 20.1, w: 8, align: 'right', font: 'Carlito', pt: 8, color: '#6E7785' });
  });
  return pages;
}
const summaryOut = () => S.pres.summary && S.pres.summary.include ? summaryPages(S.pres.summary, S.pres.sheets) : null;
// generic drawing of a laid-out page (texts, rects, logo) to HTML, PDF and PowerPoint
function specHTML(sp) {
  const lg = sp.logo;
  return (lg ? `<img class="cv-logo" src="${logoSrc(lg.dark)}" alt="Oxypro" style="left:${lg.x.toFixed(3)}cm;top:${lg.y}cm;height:${lg.h}cm;width:${(lg.h * LOGO_AR).toFixed(3)}cm">` : '')
    + sp.rects.map(r => `<span class="cv-rect" style="left:${r.x.toFixed(3)}cm;top:${r.y.toFixed(3)}cm;width:${r.w.toFixed(3)}cm;height:${r.h.toFixed(3)}cm;background:${r.color}"></span>`).join('')
    + sp.texts.map(t => `<div class="cv" style="left:${t.x.toFixed(3)}cm;top:${t.y.toFixed(3)}cm;width:${t.w.toFixed(3)}cm;font:${t.bold ? 700 : 400} ${t.pt}pt/${(t.pt * (t.lh || 1.2)).toFixed(2)}pt ${t.font === 'Caladea' ? 'Caladea,Cambria,Georgia,serif' : 'Carlito,Calibri,sans-serif'};color:${t.color};${t.ls ? `letter-spacing:${t.ls}em;` : ''}${t.align ? `text-align:${t.align};` : ''}">${esc((t.lines || [t.str]).join('\n'))}</div>`).join('');
}
async function specPdf(doc, sp) {
  if (sp.logo) { const lg = sp.logo, logos = await logoPngs(); doc.addImage(logos[lg.dark ? 'dark' : 'light'], 'PNG', lg.x, lg.y, lg.h * LOGO_AR, lg.h, undefined, 'FAST'); }
  for (const r of sp.rects) { doc.setFillColor(r.color); doc.rect(r.x, r.y, r.w, r.h, 'F'); }
  for (const t of sp.texts) {
    const lh = t.lh || 1.2, [asc, desc] = FM[t.font], sz = t.pt * PT;
    doc.setFont(t.font, t.bold ? 'bold' : 'normal'); doc.setFontSize(t.pt); doc.setTextColor(t.color);
    (t.lines || [t.str]).forEach((ln, i) => doc.text(ln, alignX(t, ln), t.y + i * lh * sz + ((lh - asc - desc) / 2 + asc) * sz, t.ls ? { charSpace: t.ls * sz } : undefined));
  }
}
async function specPptx(pptx, sl, sp, I, strip) {
  if (sp.logo) { const lg = sp.logo, logos = await logoPngs(); sl.addImage({ data: strip(logos[lg.dark ? 'dark' : 'light']), x: I(lg.x), y: I(lg.y), w: I(lg.h * LOGO_AR), h: I(lg.h), altText: 'Oxypro Electromechanical Contractors' }); }
  for (const r of sp.rects) sl.addShape(pptx.ShapeType.rect, { x: I(r.x), y: I(r.y), w: I(r.w), h: I(Math.max(r.h, 0.02)), fill: { color: r.color.slice(1) }, line: { type: 'none' } });
  for (const t of sp.texts) {
    const lines = t.lines || [t.str], lh = t.lh || 1.2;
    sl.addText(lines.join('\n'), {
      x: I(t.x), y: I(t.y), w: I(t.w), h: I(lines.length * t.pt * lh * PT + 0.1), margin: 0, valign: 'top', fit: 'none', paraSpaceBefore: 0, paraSpaceAfter: 0,
      fontFace: t.font === 'Caladea' ? 'Cambria' : 'Calibri', fontSize: t.pt, bold: !!t.bold, color: t.color.slice(1), align: t.align || 'left',
      lineSpacing: Math.round(t.pt * lh * 10) / 10, ...(t.ls ? { charSpacing: Math.round(t.ls * t.pt * 10) / 10 } : {})
    });
  }
}
function summaryRailItem() {
  const sm = S.pres.summary; if (!sm) return '';
  return `<div class="rail-item cover${S.pres.cur === -2 ? ' cur' : ''}"><button type="button" class="rail-open" data-cur="-2"><span class="rail-no">Last page</span><span class="rail-name">${sm.include ? 'Project summary' : 'Summary · not included'}</span></button></div>`;
}
let sumPagesCache = [];
async function buildSummary() {
  $('#sheet').innerHTML = '<div id="sum-fg"></div>'; fitSheet();
  await fontsReady; if (S.pres.cur !== -2) return;
  sumPagesCache = summaryPages(S.pres.summary, S.pres.sheets);
  const sm = S.pres.summary; sm.page = clamp(sm.page || 0, 0, Math.max(0, sumPagesCache.length - 1));
  const fg = $('#sum-fg'); if (!fg) return;
  fg.innerHTML = sumPagesCache.length ? specHTML(sumPagesCache[sm.page])
    : '<div class="frame-empty" style="pointer-events:none"><span>Tick at least one detail to show in the summary</span></div>';
  const pi = $('#sum-pager'); if (pi) pi.innerHTML = pagerHTML();
}
function pagerHTML() {
  const n = sumPagesCache.length, p = S.pres.summary.page || 0;
  return n > 1 ? `<span>Preview: page ${p + 1} of ${n}</span><button type="button" class="btn btn-sm" data-sum-page="-1"${p === 0 ? ' disabled' : ''}>Previous</button><button type="button" class="btn btn-sm" data-sum-page="1"${p >= n - 1 ? ' disabled' : ''}>Next</button>` : '';
}
function renderSummaryForm() {
  const sm = S.pres.summary, sel = new Set(S.summaryCols || SUM_DEFAULT), cat = sumCatalog();
  const box = c => `<label class="check-row"><input type="checkbox" data-scol="${esc(c.key)}"${sel.has(c.key) ? ' checked' : ''}><span>${esc(c.label)}</span></label>`;
  const base = cat.filter(c => !c.extra), extra = cat.filter(c => c.extra);
  $('#sheet-form').innerHTML = `<h3>Project summary</h3>
    <label class="check-row"><input type="checkbox" id="s-include" data-sk="include"${sm.include ? ' checked' : ''}> Include the summary as the last page</label>
    <div class="field"><label for="s-title">Title</label><input class="inp" id="s-title" data-sk="title" value="${esc(sm.title)}"></div>
    <div class="pager" id="sum-pager">${pagerHTML()}</div>
    <div class="field"><span class="flabel">Details to show (${sel.size ? cat.filter(c => sel.has(c.key)).length : 0} of ${cat.length})</span>
      <div class="sum-actions"><button type="button" class="btn btn-sm" data-sum-all>Select all</button><button type="button" class="btn btn-sm btn-ghost" data-sum-default>Back to default</button></div>
      <div class="checks">${base.map(box).join('')}</div>
      ${extra.length ? `<span class="flabel sub">Added from the Master List</span><div class="checks">${extra.map(box).join('')}</div>` : ''}
      <span class="hint">Columns you add to the Master List appear here after you import it. ${canWrite() ? 'Your choice is remembered for every presentation.' : 'Your choice is remembered in this browser.'}</span></div>`;
}
let sumSaveTimer = 0;
function setSummaryCols(list) {
  const order = sumCatalog().map(c => c.key), set = new Set(list);
  S.summaryCols = order.filter(k => set.has(k)).concat(list.filter(k => !order.includes(k)));
  lsSet('summaryCols', S.summaryCols);
  buildSummary(); renderSummaryForm();
  if (!canWrite()) return;
  clearTimeout(sumSaveTimer);
  sumSaveTimer = setTimeout(() => { DB.doc('settings/summary').set({ cols: S.summaryCols, updatedAt: new Date().toISOString() }).catch(e => toast(writeError(e))); }, 900);
}
function summaryInput(el) {
  const sm = S.pres.summary;
  if (el.dataset.scol) {
    const cur = new Set(S.summaryCols || SUM_DEFAULT); el.checked ? cur.add(el.dataset.scol) : cur.delete(el.dataset.scol);
    return setSummaryCols([...cur]);
  }
  if (el.dataset.sk === 'include') { sm.include = el.checked; renderPres(); return; }
  if (el.dataset.sk === 'title') { sm.title = el.value; buildSummary(); }
}

/* ---------- PDF and PowerPoint ---------- */"""
rep("/* ---------- PDF and PowerPoint ---------- */", SUMMARY)
open(P, 'w').write(s)
print('patched', len(s))
