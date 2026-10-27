"""v1.2.0: top sheet (cover) in two designs, library-wide design choice, page 1 of every presentation."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

# ---- CSS
rep(".t.ph{color:var(--paper-ph);font-style:italic}",
    """.t.ph{color:var(--paper-ph);font-style:italic}
.cover-bg{position:absolute;left:0;top:0;width:29.7cm;height:21cm;display:block}
.cv{position:absolute;white-space:pre}
.cv-logo,.cv-rect{position:absolute;display:block}
.sheet-wrap.excluded .sheet{opacity:.35}
.sheet-wrap.excluded::after{content:"Not included in the PDF and PowerPoint";position:absolute;right:12px;bottom:12px;background:var(--chip-on-bg);color:var(--chip-on-fg);padding:6px 10px;border-radius:4px;font-size:13px;font-weight:600}
.seg{display:flex;border:1px solid var(--line-strong);border-radius:6px;overflow:hidden}
.seg button{flex:1;min-width:0;min-height:40px;padding:6px 10px;border:0;background:var(--surface);color:var(--fg);cursor:pointer;font:600 13.5px/1.2 var(--f-body)}
.seg button + button{border-left:1px solid var(--line-strong)}
.seg button[aria-pressed="true"]{background:var(--chip-on-bg);color:var(--chip-on-fg)}
.seg small{display:block;font-weight:400;font-size:12px;opacity:.75}
.flabel{font-weight:600;font-size:13.5px}
.rail-item.cover .rail-no{color:var(--muted)}""")
rep('<p class="hint">Drag a photo inside its frame', '<p class="hint" id="stage-hint">Drag a photo inside its frame')
rep('Version 1.1.0 (27 Oct 2026)', 'Version 1.2.0 (27 Oct 2026)')
rep("  view: 'library', pres: { sheets: [], cur: 0, dirty: new Set() },",
    "  view: 'library', pres: { sheets: [], cur: 0, dirty: new Set(), cover: null }, coverDesign: 'A',")
rep("  S.pres.sheets = sheets; S.pres.cur = 0; S.view = 'pres'; S.detailOpen = false;",
    "  S.pres.sheets = sheets; S.pres.cover = mergeCover(S.pres.cover, sheets); S.pres.cur = -1; S.view = 'pres'; S.detailOpen = false;")
rep("""function renderPres() {
  const n = S.pres.sheets.length;
  $('#pres-count').textContent = n === 1 ? '1 sheet · A4 landscape' : `${n} sheets · A4 landscape · one page per project`;
  renderRail(); buildSheet(); renderSlots(); renderForm(); $('#chooser').hidden = true;
}""",
    """function renderPres() {
  const n = S.pres.sheets.length, cv = S.pres.cover;
  $('#pres-count').textContent = `${cv && cv.include ? 'Top sheet + ' : ''}${n} project sheet${n === 1 ? '' : 's'} · A4 landscape`;
  renderRail(); $('#chooser').hidden = true;
  const onCover = S.pres.cur === -1;
  $('#sheet-wrap').classList.toggle('excluded', onCover && !cv.include);
  $('#stage-hint').textContent = onCover ? 'The top sheet is page 1 of the PDF and PowerPoint. Its list of projects follows the order of the sheets.' : 'Drag a photo inside its frame to choose what shows. Empty frames and grey placeholder text are left out of the PDF and PowerPoint.';
  if (onCover) { $('#slots').innerHTML = ''; buildCover(); renderCoverForm(); }
  else { buildSheet(); renderSlots(); renderForm(); }
}""")
rep("""  $('#rail').innerHTML = '<span class="rail-label">Sheets</span>' + sh.map(""",
    """  $('#rail').innerHTML = '<span class="rail-label">Sheets</span>' + coverRailItem() + sh.map(""")
rep("    if (b.dataset.rm != null) { const i = +b.dataset.rm; P.sheets.splice(i, 1); if (!P.sheets.length) { closePres(); return; } P.cur = Math.min(P.cur, P.sheets.length - 1); renderPres(); }",
    "    if (b.dataset.rm != null) { const i = +b.dataset.rm; P.sheets.splice(i, 1); if (!P.sheets.length) { closePres(); return; } P.cover = mergeCover(P.cover, P.sheets); P.cur = Math.min(P.cur, P.sheets.length - 1); renderPres(); }")
rep("sw(i, i - 1); if (P.cur === i) P.cur = i - 1; else if (P.cur === i - 1) P.cur = i; renderRail(); return; }",
    "sw(i, i - 1); if (P.cur === i) P.cur = i - 1; else if (P.cur === i - 1) P.cur = i; renderRail(); if (P.cur === -1) updateCoverText(); return; }")
rep("sw(i, i + 1); if (P.cur === i) P.cur = i + 1; else if (P.cur === i + 1) P.cur = i; renderRail(); return; }",
    "sw(i, i + 1); if (P.cur === i) P.cur = i + 1; else if (P.cur === i + 1) P.cur = i; renderRail(); if (P.cur === -1) updateCoverText(); return; }")
rep("    const k = e.target.dataset.k; const sh = curSheet(); if (!k || !sh) return;",
    "    if (e.target.dataset.ck) { coverInput(e.target); return; }\n    const k = e.target.dataset.k; const sh = curSheet(); if (!k || !sh) return;")
rep("  $('#sheet-form').addEventListener('click', e => { if (e.target.closest('#save-lib')) saveSheetToLibrary(); });",
    "  $('#sheet-form').addEventListener('click', e => { if (e.target.closest('#save-lib')) saveSheetToLibrary(); const d = e.target.closest('[data-design]'); if (d) setDesign(d.dataset.design); });")

# ---- PDF / PPTX: cover first
rep("    const blob = await buildPdf(S.pres.sheets);", "    const blob = await buildPdf(S.pres.sheets, S.pres.cover && S.pres.cover.include ? S.pres.cover : null);")
rep("async function buildPdf(sheets) {", "async function buildPdf(sheets, cover) {")
rep("    if (i) doc.addPage('a4', 'landscape');", "    if (i || cover) doc.addPage('a4', 'landscape');")
rep("  const icons = await iconPngs();\n  for (let i = 0; i < sheets.length; i++) {",
    "  const icons = await iconPngs();\n  if (cover) await pdfCover(doc, cover, sheets);\n  for (let i = 0; i < sheets.length; i++) {")
rep("    const blob = await buildPptx(S.pres.sheets);", "    const blob = await buildPptx(S.pres.sheets, S.pres.cover && S.pres.cover.include ? S.pres.cover : null);")
rep("async function buildPptx(sheets) {", "async function buildPptx(sheets, cover) {")
rep("  const strip = u => u.replace(/^data:/, '');\n  for (const sh of sheets) {",
    "  const strip = u => u.replace(/^data:/, '');\n  if (cover) await pptxCover(pptx, cover, sheets, I, strip);\n  for (const sh of sheets) {")

# ---- settings subscription
rep("  }, err => { S.dbState = 'error'; S.dbError = (err && err.code) || ''; renderAll(); });\n}",
    """  }, err => { S.dbState = 'error'; S.dbError = (err && err.code) || ''; renderAll(); });
  DB.doc('settings/cover').onSnapshot(snap => {
    const d = snap.exists ? snap.data() : null; const v = d && (d.design === 'A' || d.design === 'B') ? d.design : null;
    if (!v || v === S.coverDesign) return;
    S.coverDesign = v;
    if (S.view === 'pres') { renderRail(); if (S.pres.cur === -1) { buildCover(); renderCoverForm(); } }
  }, () => {});
}""")

# ---- top sheet code
COVER = r"""/* ---------- top sheet (cover) ---------- */
const NAVY = '#13294B', NAVY_D = '#0B1A33', NAVY_M = '#1E3A66', CRED = '#D81F27';
const ON_NAVY = { red: '#F0525A', soft: '#C9D3E3', muted: '#8FA3C4', fine: '#AFC0DA' };
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const COMPANY = {
  name: 'Oxypro Electromechanical Works LLC', addr1: 'Office 204A, Gulf Towers, Oud Metha Road', addr2: 'P.O. Box 3286, Dubai, United Arab Emirates',
  web: 'info@oxyprotech.com  ·  www.oxyprotech.com', tagline: 'THE COMPLETE SOLUTION FOR BUILDING SERVICES', eyebrow: 'DESIGN & BUILD MEP CONTRACTOR'
};
const DESIGNS = { A: ['Design A', 'Navy split'], B: ['Design B', 'Navy band'] };
const LOGO_AR = 655 / 185;
const FM = { Caladea: [0.9, 0.25], Carlito: [0.952, 0.2686] };
const fontCss = t => `${t.bold ? '700 ' : ''}${t.pt}pt ${t.font}`;
const textW = (str, t) => measure(str, fontCss(t)) / CM + (t.ls ? t.ls * t.pt * PT * str.length : 0);
function coverDefaults(sheets) {
  const n = sheets.length, d = new Date();
  const ems = [...new Set(sheets.map(x => (S.projects.get(x.no) || {}).emirate).filter(Boolean))].map(k => EMIRATES[k] || k);
  return {
    include: true, title: n === 1 ? 'Project Profile' : 'Project References',
    subtitle: n === 1 ? (sheets[0].name || '') : (ems.length ? `Selected projects in ${joinAnd(ems)}` : 'Selected projects'),
    preparedFor: '', date: MONTHS[d.getMonth()] + ' ' + d.getFullYear(), photo: 'auto', edited: []
  };
}
function mergeCover(old, sheets) {
  const cv = coverDefaults(sheets);
  if (old) for (const k of old.edited || []) cv[k] = old[k];
  cv.edited = old ? [...(old.edited || [])] : [];
  if (cv.photo !== 'auto' && cv.photo !== 'none' && !sheets.some(x => x.no === cv.photo)) cv.photo = 'auto';
  return cv;
}
function coverPhoto(cv, sheets) {
  if (!cv || cv.photo === 'none') return null;
  for (const x of (cv.photo === 'auto' ? sheets : sheets.filter(y => y.no === cv.photo))) if (x.photos[0]) return x.photos[0];
  return null;
}
function fitTitle(str, maxW, big, small) {
  const t = String(str || '').replace(/\s+/g, ' ').trim(); if (!t) return { pt: big, lines: [] };
  for (let pt = big; pt >= small; pt -= 2) { const ls = wrapAll(t, pt + 'pt Caladea', maxW * CM); if (ls.length <= 2) return { pt, lines: ls }; }
  return { pt: small, lines: wrap(t, small + 'pt Caladea', maxW * CM, 2) };
}
// the text column shared by both designs: eyebrow, title, red rule, subtitle, prepared for, date
function coverText(T, R, cv, X, W, y, big) {
  T.push({ str: COMPANY.eyebrow, x: X, y, w: W, font: 'Carlito', bold: true, pt: 9, ls: 0.14, color: ON_NAVY.red });
  y += 0.62;
  const tt = fitTitle(cv.title, W, big, big - 10);
  if (tt.lines.length) { T.push({ lines: tt.lines, x: X, y, w: W, font: 'Caladea', pt: tt.pt, lh: 1.08, color: '#FFFFFF' }); y += tt.lines.length * tt.pt * 1.08 * PT; }
  R.push({ x: X, y: y + 0.38, w: 2.0, h: 0.11, color: CRED }); y += 0.92;
  const sub = cv.subtitle ? wrap(cv.subtitle, '12pt Carlito', W * CM, 2) : [];
  if (sub.length) { T.push({ lines: sub, x: X, y, w: W, font: 'Carlito', pt: 12, lh: 1.3, color: ON_NAVY.soft }); y += sub.length * 12 * 1.3 * PT; }
  y += 0.75;
  if (cv.preparedFor) {
    T.push({ str: 'PREPARED FOR', x: X, y, w: W, font: 'Carlito', bold: true, pt: 8, ls: 0.14, color: ON_NAVY.muted }); y += 0.42;
    const pf = wrap(cv.preparedFor, '13pt Carlito', W * CM, 2);
    T.push({ lines: pf, x: X, y, w: W, font: 'Carlito', pt: 13, lh: 1.2, color: '#FFFFFF' }); y += pf.length * 13 * 1.2 * PT + 0.28;
  }
  if (cv.date) T.push({ str: cv.date, x: X, y, w: W, font: 'Carlito', pt: 11, color: ON_NAVY.soft });
}
// "In this presentation" list, filled column by column
function coverList(T, R, sheets, o) {
  const n = sheets.length;
  T.push({ str: `IN THIS PRESENTATION  ·  ${n} PROJECT${n === 1 ? '' : 'S'}`, x: o.x, y: o.y, w: o.w, font: 'Carlito', bold: true, pt: 8.5, ls: 0.14, color: o.head });
  const cols = n <= o.one ? 1 : Math.min(o.maxCols, Math.ceil(n / o.rows)), cap = cols * o.rows;
  const items = n > cap ? sheets.slice(0, cap - 1).map(x => [x.no, x.name || 'Untitled']).concat([['', `+ ${n - cap + 1} more project${n - cap + 1 === 1 ? '' : 's'}`]]) : sheets.map(x => [x.no, x.name || 'Untitled']);
  const per = Math.ceil(items.length / cols), cw = (o.w - o.gap * (cols - 1)) / cols, y0 = o.y + 0.72;
  items.forEach(([no, name], i) => {
    const c = Math.floor(i / per), r = i % per, x = o.x + c * (cw + o.gap), y = y0 + r * o.rowH;
    if (no) T.push({ str: no, x, y, w: 1.3, font: 'Carlito', bold: true, pt: 10, color: o.no });
    T.push({ lines: wrap(name, '10pt Carlito', (cw - 1.35) * CM, 1), x: x + 1.35, y, w: cw - 1.35, font: 'Carlito', pt: 10, color: no ? o.name : o.more });
    R.push({ x, y: y + o.rowH - 0.2, w: cw, h: 0.018, color: o.rule });
  });
}
function coverLayout(design, cv, sheets) {
  const T = [], R = [];
  if (design === 'B') {
    T.push({ str: COMPANY.tagline, x: 12, y: 1.32, w: 16.4, align: 'right', font: 'Carlito', bold: true, pt: 8.5, ls: 0.14, color: NAVY });
    coverText(T, R, cv, 1.3, 11.4, 4.3, 34);
    coverList(T, R, sheets, { x: 1.3, y: 14.3, w: 27.1, one: 4, rows: 5, maxCols: 3, gap: 0.9, rowH: 0.72, head: CRED, no: NAVY, name: '#2B2B2B', more: '#6E6E6E', rule: '#E3E6EB' });
    const nm = { str: COMPANY.name, x: 1.3, y: 20.02, w: 9, font: 'Carlito', bold: true, pt: 9, color: '#FFFFFF' };
    T.push(nm);
    T.push({ str: `${COMPANY.addr1}, ${COMPANY.addr2.replace(', United Arab Emirates', ', UAE')}`, x: 1.3 + textW(nm.str, nm) + 0.45, y: 20.02, w: 12, font: 'Carlito', pt: 8.5, color: ON_NAVY.fine });
    T.push({ str: COMPANY.web, x: 18.4, y: 20.02, w: 10, align: 'right', font: 'Carlito', pt: 8.5, color: ON_NAVY.fine });
    return { texts: T, rects: R, logo: { dark: false, x: 1.3, y: 0.62, h: 1.75 } };
  }
  coverText(T, R, cv, 1.3, 8.8, 6.1, 36);
  T.push({ str: COMPANY.name, x: 1.3, y: 17.55, w: 8.8, font: 'Carlito', bold: true, pt: 9.5, color: '#FFFFFF' });
  T.push({ lines: [COMPANY.addr1, COMPANY.addr2, COMPANY.web], x: 1.3, y: 18.06, w: 8.8, font: 'Carlito', pt: 8.5, lh: 1.3, color: ON_NAVY.fine });
  coverList(T, R, sheets, { x: 13.4, y: 13.3, w: 15.5, one: 7, rows: 7, maxCols: 2, gap: 0.8, rowH: 0.74, head: CRED, no: NAVY, name: '#2B2B2B', more: '#6E6E6E', rule: '#E3E6EB' });
  T.push({ str: COMPANY.tagline, x: 13.4, y: 19.9, w: 15.5, font: 'Carlito', bold: true, pt: 8, ls: 0.14, color: '#6E6E6E' });
  return { texts: T, rects: R, logo: { dark: true, x: 1.3, y: 1.3, h: 1.75 } };
}
// background artwork (photo, navy shapes, red stripe, the logo's dot ring) as one raster
async function coverBg(design, photo, dpi) {
  const k = dpi / 2.54, W = Math.round(29.7 * k), H = Math.round(21 * k);
  const c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d');
  const path = pts => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x * k, y * k) : g.moveTo(x * k, y * k)); g.closePath(); };
  const poly = (pts, fill) => { path(pts); g.fillStyle = fill; g.fill(); };
  const lin = (x0, y0, x1, y1, a, b) => { const gr = g.createLinearGradient(x0 * k, y0 * k, x1 * k, y1 * k); gr.addColorStop(0, a); gr.addColorStop(1, b); return gr; };
  const dots = (clipPts, cx, cy, r0, r1, rgb, alpha) => {
    g.save(); path(clipPts); g.clip();
    for (let r = r0; r <= r1; r += 0.4) {
      const t = (r - r0) / (r1 - r0), n = Math.max(6, Math.round(2 * Math.PI * r / 0.4)), dr = 0.085 * (1 - 0.6 * t);
      g.fillStyle = `rgba(${rgb},${(alpha * (1 - 0.55 * t)).toFixed(3)})`;
      for (let i = 0; i < n; i++) { const a = (i + (Math.round(r / 0.4) % 2) * 0.5) / n * Math.PI * 2; g.beginPath(); g.arc((cx + r * Math.cos(a)) * k, (cy + r * Math.sin(a)) * k, dr * k, 0, Math.PI * 2); g.fill(); }
    }
    g.restore();
  };
  let img = null;
  if (photo) { try { img = await loadImg(photo.src); } catch (e) { img = null; } }
  const drawPhoto = (x, y, w, h) => {
    const bw = w * k, bh = h * k, sc = Math.max(bw / img.naturalWidth, bh / img.naturalHeight), dw = img.naturalWidth * sc, dh = img.naturalHeight * sc;
    g.save(); g.beginPath(); g.rect(x * k, y * k, bw, bh); g.clip(); g.imageSmoothingQuality = 'high';
    g.drawImage(img, x * k + (bw - dw) * (photo.x / 100), y * k + (bh - dh) * (photo.y / 100), dw, dh); g.restore();
  };
  g.fillStyle = '#FFFFFF'; g.fillRect(0, 0, W, H);
  if (design === 'B') {
    const band = [[0, 3], [29.7, 3], [29.7, 13.6], [0, 13.6]];
    if (img) drawPhoto(0, 3, 29.7, 10.6);
    else { poly(band, lin(0, 3, 29.7, 13.6, NAVY_M, NAVY)); dots(band, 23.4, 8.3, 0.9, 8.6, '150,176,222', 0.3); }
    const panel = [[0, 3], [16.2, 3], [13.6, 13.6], [0, 13.6]];
    poly(panel, img ? 'rgba(11,26,51,0.88)' : NAVY_D);
    if (!img) dots(panel, 1.2, 12.6, 0.9, 6.5, '150,176,222', 0.12);
    poly([[16.2, 3], [16.75, 3], [14.15, 13.6], [13.6, 13.6]], CRED);
    g.fillStyle = NAVY_D; g.fillRect(0, 19.55 * k, W, H - 19.55 * k);
    g.fillStyle = CRED; g.fillRect(0, 19.55 * k, W, 0.08 * k);
  } else {
    const area = [[8.6, 0], [29.7, 0], [29.7, 12.4], [8.6, 12.4]];
    if (img) drawPhoto(8.6, 0, 21.1, 12.4);
    else { poly(area, lin(8.6, 0, 29.7, 12.4, NAVY_M, NAVY)); dots(area, 24.6, 6.0, 0.9, 9.4, '150,176,222', 0.3); }
    g.fillStyle = NAVY; g.fillRect(8.6 * k, 12.4 * k, 21.1 * k, 0.1 * k);
    const panel = [[0, 0], [13, 0], [10.4, 21], [0, 21]];
    poly(panel, lin(0, 0, 0, 21, NAVY, NAVY_D));
    dots(panel, 1.0, 19.9, 0.9, 8.2, '150,176,222', 0.13);
    poly([[13, 0], [13.6, 0], [11, 21], [10.4, 21]], CRED);
  }
  return c;
}
function logoSrc(dark) { return $(dark ? '.logo-d' : '.logo-l').getAttribute('src'); }
let coverToken = 0;
async function buildCover() {
  const tok = ++coverToken;
  $('#sheet').innerHTML = '<canvas class="cover-bg" id="cover-bg"></canvas><div id="cover-fg"></div>';
  fitSheet();
  await fontsReady;
  updateCoverText();
  const bg = await coverBg(S.coverDesign, coverPhoto(S.pres.cover, S.pres.sheets), 110);
  if (tok !== coverToken || S.pres.cur !== -1) return;
  const c = $('#cover-bg'); if (!c) return;
  c.width = bg.width; c.height = bg.height; c.getContext('2d').drawImage(bg, 0, 0);
}
function updateCoverText() {
  const fg = $('#cover-fg'); if (!fg || S.pres.cur !== -1) return;
  const L = coverLayout(S.coverDesign, S.pres.cover, S.pres.sheets);
  const lg = L.logo;
  fg.innerHTML = `<img class="cv-logo" src="${logoSrc(lg.dark)}" alt="Oxypro" style="left:${lg.x}cm;top:${lg.y}cm;height:${lg.h}cm;width:${(lg.h * LOGO_AR).toFixed(3)}cm">`
    + L.rects.map(r => `<span class="cv-rect" style="left:${r.x.toFixed(3)}cm;top:${r.y.toFixed(3)}cm;width:${r.w.toFixed(3)}cm;height:${r.h}cm;background:${r.color}"></span>`).join('')
    + L.texts.map(t => `<div class="cv" style="left:${t.x.toFixed(3)}cm;top:${t.y.toFixed(3)}cm;width:${t.w.toFixed(3)}cm;font:${t.bold ? 700 : 400} ${t.pt}pt/${(t.pt * (t.lh || 1.2)).toFixed(2)}pt ${t.font === 'Caladea' ? 'Caladea,Cambria,Georgia,serif' : 'Carlito,Calibri,sans-serif'};color:${t.color};${t.ls ? `letter-spacing:${t.ls}em;` : ''}${t.align ? `text-align:${t.align};` : ''}">${esc((t.lines || [t.str]).join('\n'))}</div>`).join('');
}
function coverRailItem() {
  const cv = S.pres.cover; if (!cv) return '';
  return `<div class="rail-item cover${S.pres.cur === -1 ? ' cur' : ''}"><button type="button" class="rail-open" data-cur="-1"><span class="rail-no">Top sheet</span><span class="rail-name">${cv.include ? esc(DESIGNS[S.coverDesign].join(' · ')) : 'Not included'}</span></button></div>`;
}
const COVER_FIELDS = [
  ['title', 'Title', 'inp', ''],
  ['subtitle', 'Subtitle', 'txt', 'Up to two lines'],
  ['preparedFor', 'Prepared for', 'inp', 'Leave empty to leave it off the sheet'],
  ['date', 'Date', 'inp', '']
];
function renderCoverForm() {
  const cv = S.pres.cover, d = S.coverDesign, w = canWrite();
  const opts = [['auto', 'Main photo of the first project that has one']].concat(S.pres.sheets.filter(x => x.photos[0]).map(x => [x.no, `${x.no} · ${x.name}`]), [['none', 'No photo (navy pattern)']]);
  $('#sheet-form').innerHTML = `<h3>Top sheet</h3>
    <div class="field"><span class="flabel">Design</span><div class="seg" role="group" aria-label="Top sheet design">
      ${Object.entries(DESIGNS).map(([k, [a, b]]) => `<button type="button" data-design="${k}" aria-pressed="${d === k}">${a}<small>${b}</small></button>`).join('')}</div>
      <span class="hint">${w ? 'The design you choose is used for every presentation.' : 'Only library editors can change the design for everyone; this choice applies to this presentation.'}</span></div>
    <label class="check-row"><input type="checkbox" id="c-include" data-ck="include"${cv.include ? ' checked' : ''}> Include the top sheet in the PDF and PowerPoint</label>
    ${COVER_FIELDS.map(([k, label, type, hint]) => `<div class="field"><label for="c-${k}">${esc(label)}</label>${type === 'txt' ? `<textarea class="txt" id="c-${k}" data-ck="${k}">${esc(cv[k])}</textarea>` : `<input class="inp" id="c-${k}" data-ck="${k}" value="${esc(cv[k])}">`}${hint ? `<span class="hint">${esc(hint)}</span>` : ''}</div>`).join('')}
    <div class="field"><label for="c-photo">Photo</label><select class="sel" id="c-photo" data-ck="photo">${opts.map(([v, l]) => `<option value="${esc(v)}"${cv.photo === v ? ' selected' : ''}>${esc(l)}</option>`).join('')}</select>
      <span class="hint">Without a photo the top sheet uses a navy dot pattern from the Oxypro logo.</span></div>`;
}
function coverInput(el) {
  const cv = S.pres.cover, k = el.dataset.ck;
  cv[k] = el.type === 'checkbox' ? el.checked : el.value;
  if (!cv.edited.includes(k)) cv.edited.push(k);
  if (k === 'include') { renderPres(); return; }
  if (k === 'photo') { buildCover(); return; }
  updateCoverText();
}
async function setDesign(d) {
  if (!DESIGNS[d] || d === S.coverDesign) return;
  S.coverDesign = d; renderRail(); buildCover(); renderCoverForm();
  if (!canWrite()) return;
  try { await DB.doc('settings/cover').set({ design: d, updatedAt: new Date().toISOString() }); toast(`${DESIGNS[d][0]} is now the top sheet for every presentation`); }
  catch (e) { toast(writeError(e)); }
}
let logoPngCache = null;
async function logoPngs() {
  if (logoPngCache) return logoPngCache;
  const out = {};
  for (const dark of [false, true]) {
    const img = await loadImg(logoSrc(dark)); const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight;
    c.getContext('2d').drawImage(img, 0, 0); out[dark ? 'dark' : 'light'] = c.toDataURL('image/png');
  }
  return (logoPngCache = out);
}
async function pdfCover(doc, cv, sheets) {
  const bg = await coverBg(S.coverDesign, coverPhoto(cv, sheets), 200);
  doc.addImage(bg.toDataURL('image/jpeg', 0.9), 'JPEG', 0, 0, 29.7, 21, undefined, 'FAST');
  const L = coverLayout(S.coverDesign, cv, sheets), logos = await logoPngs(), lg = L.logo;
  doc.addImage(logos[lg.dark ? 'dark' : 'light'], 'PNG', lg.x, lg.y, lg.h * LOGO_AR, lg.h, undefined, 'FAST');
  for (const r of L.rects) { doc.setFillColor(r.color); doc.rect(r.x, r.y, r.w, r.h, 'F'); }
  for (const t of L.texts) {
    const lh = t.lh || 1.2, [asc, desc] = FM[t.font], sz = t.pt * PT;
    doc.setFont(t.font, t.bold ? 'bold' : 'normal'); doc.setFontSize(t.pt); doc.setTextColor(t.color);
    (t.lines || [t.str]).forEach((ln, i) => {
      const x = t.align === 'right' ? t.x + t.w - textW(ln, t) : t.x;
      doc.text(ln, x, t.y + i * lh * sz + ((lh - asc - desc) / 2 + asc) * sz, t.ls ? { charSpace: t.ls * sz } : undefined);
    });
  }
}
async function pptxCover(pptx, cv, sheets, I, strip) {
  const sl = pptx.addSlide(); sl.background = { color: 'FFFFFF' };
  const bg = await coverBg(S.coverDesign, coverPhoto(cv, sheets), 200);
  sl.addImage({ data: strip(bg.toDataURL('image/jpeg', 0.9)), x: 0, y: 0, w: I(29.7), h: I(21), altText: 'Top sheet background' });
  const L = coverLayout(S.coverDesign, cv, sheets), logos = await logoPngs(), lg = L.logo;
  sl.addImage({ data: strip(logos[lg.dark ? 'dark' : 'light']), x: I(lg.x), y: I(lg.y), w: I(lg.h * LOGO_AR), h: I(lg.h), altText: 'Oxypro Electromechanical Contractors' });
  for (const r of L.rects) sl.addShape(pptx.ShapeType.rect, { x: I(r.x), y: I(r.y), w: I(r.w), h: I(r.h), fill: { color: r.color.slice(1) }, line: { type: 'none' } });
  for (const t of L.texts) {
    const lines = t.lines || [t.str], lh = t.lh || 1.2;
    sl.addText(lines.join('\n'), {
      x: I(t.x), y: I(t.y), w: I(t.w), h: I(lines.length * t.pt * lh * PT + 0.12), margin: 0, valign: 'top', fit: 'none', paraSpaceBefore: 0, paraSpaceAfter: 0,
      fontFace: t.font === 'Caladea' ? 'Cambria' : 'Calibri', fontSize: t.pt, bold: !!t.bold, color: t.color.slice(1), align: t.align || 'left',
      lineSpacing: Math.round(t.pt * lh * 10) / 10, ...(t.ls ? { charSpacing: Math.round(t.ls * t.pt * 10) / 10 } : {})
    });
  }
}

/* ---------- PDF and PowerPoint ---------- */"""
rep("/* ---------- PDF and PowerPoint ---------- */", COVER)
open(P, 'w').write(s)
print('patched', len(s))
