"""v1.3.0: top sheet Designs C and D (clean, optional background photo), photo picker with upload and drag, design thumbnails."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

# ---- CSS: design cards and photo tiles replace the two-button switch
rep(""".seg{display:flex;border:1px solid var(--line-strong);border-radius:6px;overflow:hidden}
.seg button{flex:1;min-width:0;min-height:40px;padding:6px 10px;border:0;background:var(--surface);color:var(--fg);cursor:pointer;font:600 13.5px/1.2 var(--f-body)}
.seg button + button{border-left:1px solid var(--line-strong)}
.seg button[aria-pressed="true"]{background:var(--chip-on-bg);color:var(--chip-on-fg)}
.seg small{display:block;font-weight:400;font-size:12px;opacity:.75}
""", """.designs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.dcard{display:flex;flex-direction:column;gap:6px;min-width:0;padding:6px;border:1px solid var(--line-strong);border-radius:6px;background:var(--surface);color:var(--fg);cursor:pointer;text-align:left;font:600 13px/1.2 var(--f-body)}
.dcard:hover{border-color:var(--muted)}
.dcard[aria-pressed="true"]{border-color:var(--red);box-shadow:inset 0 0 0 1px var(--red)}
.dcard small{display:block;font-weight:400;color:var(--muted);font-size:12px;margin-top:1px}
.dthumb{display:block;width:100%;max-width:100%;height:auto;aspect-ratio:29.7/21;background:var(--paper);border-radius:3px;box-shadow:0 0 0 1px var(--line)}
.ptiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(70px,1fr));gap:6px;max-height:252px;overflow:auto;padding:2px}
.ptile{position:relative;aspect-ratio:4/3;max-width:100%;min-width:0;border:1px solid var(--line-strong);border-radius:4px;background:var(--surface-2);color:var(--fg);cursor:pointer;padding:4px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font:600 11.5px/1.15 var(--f-body);overflow:hidden}
.ptile:hover{border-color:var(--muted)}
.ptile small{font-weight:400;color:var(--muted);font-size:10.5px;margin-top:2px}
.ptile img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ptile[aria-pressed="true"]::after{content:"";position:absolute;inset:0;border-radius:3px;box-shadow:inset 0 0 0 2px var(--red)}
.ptile.up{border-style:dashed;background:var(--surface)}
.sheet-wrap.cover-photo .sheet{cursor:grab}
.sheet-wrap.cover-photo .sheet:active{cursor:grabbing}
""")
rep('Version 1.2.0 (27 Oct 2026)', 'Version 1.3.0 (27 Oct 2026)')
rep("  $('#sheet-wrap').classList.toggle('excluded', onCover && !cv.include);",
    "  $('#sheet-wrap').classList.toggle('excluded', onCover && !cv.include); $('#sheet-wrap').classList.remove('cover-photo');")
rep("'The top sheet is page 1 of the PDF and PowerPoint. Its list of projects follows the order of the sheets.'",
    "'The top sheet is page 1 of the PDF and PowerPoint. Drag its photo to choose what shows. The project list follows the order of the sheets.'")
rep("  } else if (tgt.kind === 'sheet') {", "  } else if (tgt.kind === 'cover') {\n    coverDevicePhoto(blob);\n  } else if (tgt.kind === 'sheet') {")
rep("  $('#sheet-form').addEventListener('click', e => { if (e.target.closest('#save-lib')) saveSheetToLibrary(); const d = e.target.closest('[data-design]'); if (d) setDesign(d.dataset.design); });",
    """  $('#sheet-form').addEventListener('click', e => {
    if (e.target.closest('#save-lib')) return saveSheetToLibrary();
    const d = e.target.closest('[data-design]'); if (d) return setDesign(d.dataset.design);
    const p = e.target.closest('[data-cph]'); if (p) return setCoverPhoto(p.dataset.cph);
    if (e.target.closest('[data-cph-upload]')) { S.fileTarget = { kind: 'cover' }; $('#file-photo').value = ''; $('#file-photo').click(); }
  });""")
rep("  if (window.ResizeObserver) new ResizeObserver(fitSheet).observe($('#sheet-wrap')); else window.addEventListener('resize', fitSheet);",
    "  if (window.ResizeObserver) new ResizeObserver(fitSheet).observe($('#sheet-wrap')); else window.addEventListener('resize', fitSheet);\n  bindCoverDrag();")
rep("const v = d && (d.design === 'A' || d.design === 'B') ? d.design : null;", "const v = d && DESIGNS[d.design] ? d.design : null;")

# ---- replace the whole top sheet block
a = s.index("/* ---------- top sheet (cover) ---------- */")
b = s.index("/* ---------- PDF and PowerPoint ---------- */")
COVER = r"""/* ---------- top sheet (cover) ---------- */
const NAVY = '#13294B', NAVY_D = '#0B1A33', NAVY_M = '#1E3A66', CRED = '#D81F27';
const ON_NAVY = { red: '#F0525A', soft: '#C9D3E3', muted: '#8FA3C4', fine: '#AFC0DA' };
const PAL_NAVY = { eyebrow: ON_NAVY.red, title: '#FFFFFF', sub: ON_NAVY.soft, label: ON_NAVY.muted, value: '#FFFFFF', date: ON_NAVY.soft };
const PAL_LIGHT = { eyebrow: CRED, title: '#1F2733', sub: '#566070', label: '#7A8699', value: '#1F2733', date: '#566070' };
const LIST_LIGHT = { head: CRED, no: NAVY, name: '#2B2B2B', more: '#6E6E6E', rule: '#E3E6EB' };
const LIST_NAVY = { head: ON_NAVY.red, no: '#FFFFFF', name: '#E3E9F2', more: ON_NAVY.muted, rule: '#3B5076' };
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const COMPANY = {
  name: 'Oxypro Electromechanical Works LLC', addr1: 'Office 204A, Gulf Towers, Oud Metha Road', addr2: 'P.O. Box 3286, Dubai, United Arab Emirates',
  web: 'info@oxyprotech.com  ·  www.oxyprotech.com', tagline: 'THE COMPLETE SOLUTION FOR BUILDING SERVICES', eyebrow: 'DESIGN & BUILD MEP CONTRACTOR'
};
const ADDR_SHORT = `${COMPANY.addr1}, P.O. Box 3286, Dubai, UAE`;
const DESIGNS = { A: ['Design A', 'Navy split'], B: ['Design B', 'Navy band'], C: ['Design C', 'Clean light'], D: ['Design D', 'Clean centred'] };
const CLEAN = d => d === 'C' || d === 'D';
// where the photo sits on each design (x, y, w, h in cm)
const PHOTO_BOX = { A: [8.6, 0, 21.1, 12.4], B: [0, 3, 29.7, 10.6], C: [0, 0, 29.7, 21], D: [0, 0, 29.7, 21] };
const LOGO_AR = 655 / 185;
const FM = { Caladea: [0.9, 0.25], Carlito: [0.952, 0.2686] };
const fontCss = t => `${t.bold ? '700 ' : ''}${t.pt}pt ${t.font}`;
const textW = (str, t) => measure(str, fontCss(t)) / CM + (t.ls ? t.ls * t.pt * PT * str.length : 0);
const alignX = (t, ln) => t.align === 'right' ? t.x + t.w - textW(ln, t) : t.align === 'center' ? t.x + (t.w - textW(ln, t)) / 2 : t.x;
const NAT = new Map();   // natural sizes of loaded photos, for dragging
async function loadPhoto(src) { const img = await loadImg(src); NAT.set(src, [img.naturalWidth, img.naturalHeight]); return img; }

function coverDefaults(sheets) {
  const n = sheets.length, d = new Date();
  const ems = [...new Set(sheets.map(x => (S.projects.get(x.no) || {}).emirate).filter(Boolean))].map(k => EMIRATES[k] || k);
  return {
    include: true, title: n === 1 ? 'Project Profile' : 'Project References',
    subtitle: n === 1 ? (sheets[0].name || '') : (ems.length ? `Selected projects in ${joinAnd(ems)}` : 'Selected projects'),
    preparedFor: '', date: MONTHS[d.getMonth()] + ' ' + d.getFullYear(), photo: 'auto', device: null, focus: null, edited: []
  };
}
function photoKeyValid(key, sheets, cv) {
  if (key === 'auto' || key === 'none') return true;
  if (key === 'device') return !!cv.device;
  const [no, slot] = String(key).split(':'); const x = sheets.find(y => y.no === no); return !!(x && x.photos[+slot]);
}
function mergeCover(old, sheets) {
  const cv = coverDefaults(sheets);
  // a new presentation keeps typed text and the chosen photo but always starts with the top sheet included
  const keep = old ? (old.edited || []).filter(k => k !== 'include') : [];
  for (const k of keep) cv[k] = old[k];
  if (old) { cv.device = old.device; if (keep.includes('photo')) cv.focus = old.focus; }
  cv.edited = keep;
  if (!photoKeyValid(cv.photo, sheets, cv)) { cv.photo = 'auto'; cv.focus = null; cv.edited = cv.edited.filter(k => k !== 'photo'); }
  return cv;
}
// clean designs start without a photo; the navy designs use the first project's main photo
const photoKey = (cv, design) => cv.edited.includes('photo') ? cv.photo : (CLEAN(design) ? 'none' : 'auto');
function coverPhoto(cv, sheets, design) {
  if (!cv) return null;
  const key = photoKey(cv, design); let ph = null;
  if (key === 'none') return null;
  if (key === 'device') ph = cv.device;
  else if (key === 'auto') { for (const x of sheets) if (x.photos[0]) { ph = x.photos[0]; break; } }
  else { const [no, slot] = key.split(':'); const x = sheets.find(y => y.no === no); ph = x ? x.photos[+slot] : null; }
  if (!ph) return null;
  return { src: ph.src, x: cv.focus ? cv.focus.x : (+ph.x || 50), y: cv.focus ? cv.focus.y : (+ph.y || 50) };
}
function fitTitle(str, maxW, big, small) {
  const t = String(str || '').replace(/\s+/g, ' ').trim(); if (!t) return { pt: big, lines: [] };
  for (let pt = big; pt >= small; pt -= 2) { const ls = wrapAll(t, pt + 'pt Caladea', maxW * CM); if (ls.length <= 2) return { pt, lines: ls }; }
  return { pt: small, lines: wrap(t, small + 'pt Caladea', maxW * CM, 2) };
}
// eyebrow, title, red rule, subtitle, prepared for and date; returns where the block ends
function coverText(T, R, cv, o) {
  const { x: X, w: W, pal } = o, al = o.align || 'left'; let y = o.y;
  T.push({ str: COMPANY.eyebrow, x: X, y, w: W, font: 'Carlito', bold: true, pt: 9, ls: 0.14, color: pal.eyebrow, align: al });
  y += 0.62;
  const tt = fitTitle(cv.title, W, o.big, o.big - 10);
  if (tt.lines.length) { T.push({ lines: tt.lines, x: X, y, w: W, font: 'Caladea', pt: tt.pt, lh: 1.08, color: pal.title, align: al }); y += tt.lines.length * tt.pt * 1.08 * PT; }
  R.push({ x: al === 'center' ? X + (W - 2) / 2 : X, y: y + 0.38, w: 2.0, h: 0.11, color: CRED }); y += 0.92;
  const sp = o.sub || 12, sub = cv.subtitle ? wrap(cv.subtitle, sp + 'pt Carlito', W * CM, 2) : [];
  if (sub.length) { T.push({ lines: sub, x: X, y, w: W, font: 'Carlito', pt: sp, lh: 1.3, color: pal.sub, align: al }); y += sub.length * sp * 1.3 * PT; }
  y += 0.75;
  if (cv.preparedFor) {
    T.push({ str: 'PREPARED FOR', x: X, y, w: W, font: 'Carlito', bold: true, pt: 8, ls: 0.14, color: pal.label, align: al }); y += 0.42;
    const pf = wrap(cv.preparedFor, '13pt Carlito', W * CM, 2);
    T.push({ lines: pf, x: X, y, w: W, font: 'Carlito', pt: 13, lh: 1.2, color: pal.value, align: al }); y += pf.length * 13 * 1.2 * PT + 0.28;
  }
  if (cv.date) { T.push({ str: cv.date, x: X, y, w: W, font: 'Carlito', pt: 11, color: pal.date, align: al }); y += 11 * 1.2 * PT; }
  return y;
}
// "In this presentation" list, filled column by column
function coverList(T, R, sheets, o) {
  const n = sheets.length, c = o.c;
  T.push({ str: `IN THIS PRESENTATION  ·  ${n} PROJECT${n === 1 ? '' : 'S'}`, x: o.x, y: o.y, w: o.w, font: 'Carlito', bold: true, pt: 8.5, ls: 0.14, color: c.head, align: o.align || 'left' });
  const cols = n <= o.one ? 1 : Math.min(o.maxCols, Math.ceil(n / o.rows)), cap = cols * o.rows;
  const items = n > cap ? sheets.slice(0, cap - 1).map(x => [x.no, x.name || 'Untitled']).concat([['', `+ ${n - cap + 1} more project${n - cap + 1 === 1 ? '' : 's'}`]]) : sheets.map(x => [x.no, x.name || 'Untitled']);
  const per = Math.ceil(items.length / cols), cw = (o.w - o.gap * (cols - 1)) / cols, y0 = o.y + 0.72;
  const x0 = o.align === 'center' && cols === 1 ? o.x + (o.w - Math.min(cw, 12)) / 2 : o.x, cwx = o.align === 'center' && cols === 1 ? Math.min(cw, 12) : cw;
  items.forEach(([no, name], i) => {
    const ci = Math.floor(i / per), r = i % per, x = x0 + ci * (cwx + o.gap), y = y0 + r * o.rowH;
    if (no) T.push({ str: no, x, y, w: 1.3, font: 'Carlito', bold: true, pt: 10, color: c.no });
    T.push({ lines: wrap(name, '10pt Carlito', (cwx - 1.35) * CM, 1), x: x + 1.35, y, w: cwx - 1.35, font: 'Carlito', pt: 10, color: no ? c.name : c.more });
    R.push({ x, y: y + o.rowH - 0.2, w: cwx, h: 0.018, color: c.rule });
  });
}
// rows that fit between the end of the title block and the footer
const fitRows = (top, bottom, rowH, max) => Math.max(2, Math.min(max, Math.floor((bottom - top - 0.72) / rowH)));
function coverLayout(design, cv, sheets) {
  const T = [], R = [], photo = !!coverPhoto(cv, sheets, design);
  if (design === 'B') {
    T.push({ str: COMPANY.tagline, x: 12, y: 1.32, w: 16.4, align: 'right', font: 'Carlito', bold: true, pt: 8.5, ls: 0.14, color: NAVY });
    coverText(T, R, cv, { x: 1.3, w: 11.4, y: 4.3, big: 34, pal: PAL_NAVY });
    coverList(T, R, sheets, { x: 1.3, y: 14.3, w: 27.1, one: 4, rows: 5, maxCols: 3, gap: 0.9, rowH: 0.72, c: LIST_LIGHT });
    const nm = { str: COMPANY.name, x: 1.3, y: 20.02, w: 9, font: 'Carlito', bold: true, pt: 9, color: '#FFFFFF' };
    T.push(nm, { str: ADDR_SHORT, x: 1.3 + textW(nm.str, nm) + 0.45, y: 20.02, w: 12, font: 'Carlito', pt: 8.5, color: ON_NAVY.fine },
      { str: COMPANY.web, x: 18.4, y: 20.02, w: 10, align: 'right', font: 'Carlito', pt: 8.5, color: ON_NAVY.fine });
    return { texts: T, rects: R, logo: { dark: false, x: 1.3, y: 0.62, h: 1.75 } };
  }
  if (design === 'C') {
    const end = coverText(T, R, cv, { x: 1.6, w: 15.5, y: 5.9, big: 42, sub: 13, pal: PAL_LIGHT });
    const ly = Math.max(13.55, end + 0.6);
    coverList(T, R, sheets, { x: 1.6, y: ly, w: 26.5, one: 4, rows: fitRows(ly, 18.75, 0.72, 5), maxCols: 3, gap: 0.9, rowH: 0.72, c: LIST_LIGHT });
    R.push({ x: 1.6, y: 19.0, w: 26.5, h: 0.03, color: NAVY });
    const nm = { str: COMPANY.name, x: 1.6, y: 19.38, w: 9, font: 'Carlito', bold: true, pt: 9, color: NAVY };
    T.push(nm, { str: ADDR_SHORT, x: 1.6 + textW(nm.str, nm) + 0.45, y: 19.38, w: 12, font: 'Carlito', pt: 8.5, color: '#566070' },
      { str: COMPANY.web, x: 18.1, y: 19.38, w: 10, align: 'right', font: 'Carlito', pt: 8.5, color: '#566070' });
    return { texts: T, rects: R, logo: { dark: false, x: 1.6, y: 1.45, h: 1.75 } };
  }
  if (design === 'D') {
    const pal = photo ? PAL_NAVY : PAL_LIGHT, lh = 2.0;
    const end = coverText(T, R, cv, { x: 3.85, w: 22, y: 5.55, big: 44, sub: 13, pal, align: 'center' });
    const ly = Math.max(13.3, end + 0.6);
    coverList(T, R, sheets, { x: 3.1, y: ly, w: 23.5, one: 4, rows: fitRows(ly, 18.6, 0.72, 5), maxCols: 3, gap: 0.9, rowH: 0.72, c: photo ? LIST_NAVY : LIST_LIGHT, align: 'center' });
    T.push({ str: COMPANY.name, x: 2, y: 18.95, w: 25.7, align: 'center', font: 'Carlito', bold: true, pt: 9, color: photo ? '#FFFFFF' : NAVY },
      { str: `${ADDR_SHORT}  ·  ${COMPANY.web}`, x: 2, y: 19.42, w: 25.7, align: 'center', font: 'Carlito', pt: 8.5, color: photo ? ON_NAVY.fine : '#566070' });
    return { texts: T, rects: R, logo: { dark: photo, x: (29.7 - lh * LOGO_AR) / 2, y: 1.75, h: lh } };
  }
  coverText(T, R, cv, { x: 1.3, w: 8.8, y: 6.1, big: 36, pal: PAL_NAVY });
  T.push({ str: COMPANY.name, x: 1.3, y: 17.55, w: 8.8, font: 'Carlito', bold: true, pt: 9.5, color: '#FFFFFF' },
    { lines: [COMPANY.addr1, COMPANY.addr2, COMPANY.web], x: 1.3, y: 18.06, w: 8.8, font: 'Carlito', pt: 8.5, lh: 1.3, color: ON_NAVY.fine });
  coverList(T, R, sheets, { x: 13.4, y: 13.3, w: 15.5, one: 7, rows: 7, maxCols: 2, gap: 0.8, rowH: 0.74, c: LIST_LIGHT });
  T.push({ str: COMPANY.tagline, x: 13.4, y: 19.9, w: 15.5, font: 'Carlito', bold: true, pt: 8, ls: 0.14, color: '#6E6E6E' });
  return { texts: T, rects: R, logo: { dark: true, x: 1.3, y: 1.3, h: 1.75 } };
}
// background artwork (photo, veils, navy shapes, red accents, the logo's dot ring) as one raster
async function coverBg(design, photo, dpi) {
  const k = dpi / 2.54, W = Math.round(29.7 * k), H = Math.round(21 * k);
  const c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d');
  const path = pts => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x * k, y * k) : g.moveTo(x * k, y * k)); g.closePath(); };
  const poly = (pts, fill) => { path(pts); g.fillStyle = fill; g.fill(); };
  const lin = (x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0 * k, y0 * k, x1 * k, y1 * k); stops.forEach(([o, col]) => gr.addColorStop(o, col)); return gr; };
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
  if (photo) { try { img = await loadPhoto(photo.src); } catch (e) { img = null; } }
  const drawPhoto = () => {
    const [x, y, w, h] = PHOTO_BOX[design], bw = w * k, bh = h * k, sc = Math.max(bw / img.naturalWidth, bh / img.naturalHeight), dw = img.naturalWidth * sc, dh = img.naturalHeight * sc;
    g.save(); g.beginPath(); g.rect(x * k, y * k, bw, bh); g.clip(); g.imageSmoothingQuality = 'high';
    g.drawImage(img, x * k + (bw - dw) * (photo.x / 100), y * k + (bh - dh) * (photo.y / 100), dw, dh); g.restore();
  };
  g.fillStyle = '#FFFFFF'; g.fillRect(0, 0, W, H);
  if (design === 'B') {
    const band = [[0, 3], [29.7, 3], [29.7, 13.6], [0, 13.6]];
    if (img) drawPhoto();
    else { poly(band, lin(0, 3, 29.7, 13.6, [[0, NAVY_M], [1, NAVY]])); dots(band, 23.4, 8.3, 0.9, 8.6, '150,176,222', 0.3); }
    const panel = [[0, 3], [16.2, 3], [13.6, 13.6], [0, 13.6]];
    poly(panel, img ? 'rgba(11,26,51,0.88)' : NAVY_D);
    if (!img) dots(panel, 1.2, 12.6, 0.9, 6.5, '150,176,222', 0.12);
    poly([[16.2, 3], [16.75, 3], [14.15, 13.6], [13.6, 13.6]], CRED);
    g.fillStyle = NAVY_D; g.fillRect(0, 19.55 * k, W, H - 19.55 * k);
    g.fillStyle = CRED; g.fillRect(0, 19.55 * k, W, 0.08 * k);
  } else if (design === 'C') {
    if (img) {
      drawPhoto();   // the photo shows through a white veil: strongest top right, almost white behind the text and list
      g.fillStyle = lin(0, 0, 29.7, 0, [[0, 'rgba(255,255,255,0.94)'], [0.45, 'rgba(255,255,255,0.88)'], [1, 'rgba(255,255,255,0.42)']]); g.fillRect(0, 0, W, 12.6 * k);
      g.fillStyle = lin(0, 11.2, 0, 12.6, [[0, 'rgba(255,255,255,0)'], [1, 'rgba(255,255,255,0.95)']]); g.fillRect(0, 11.2 * k, W, 1.4 * k);
      g.fillStyle = 'rgba(255,255,255,0.95)'; g.fillRect(0, 12.6 * k, W, H - 12.6 * k);
    }
    g.fillStyle = CRED; g.fillRect(0, 0, W, 0.16 * k);
    g.fillStyle = NAVY; g.fillRect(0, H - 0.22 * k, W, 0.22 * k);
  } else if (design === 'D') {
    if (img) { drawPhoto(); g.fillStyle = 'rgba(11,26,51,0.8)'; g.fillRect(0, 0, W, H); }
    g.strokeStyle = img ? 'rgba(255,255,255,0.55)' : NAVY; g.lineWidth = 0.035 * k; g.strokeRect(0.9 * k, 0.9 * k, 27.9 * k, 19.2 * k);
    g.fillStyle = CRED; g.fillRect(13.85 * k, 0.84 * k, 2.0 * k, 0.12 * k); g.fillRect(13.85 * k, 20.04 * k, 2.0 * k, 0.12 * k);
  } else {
    const area = [[8.6, 0], [29.7, 0], [29.7, 12.4], [8.6, 12.4]];
    if (img) drawPhoto();
    else { poly(area, lin(8.6, 0, 29.7, 12.4, [[0, NAVY_M], [1, NAVY]])); dots(area, 24.6, 6.0, 0.9, 9.4, '150,176,222', 0.3); }
    g.fillStyle = NAVY; g.fillRect(8.6 * k, 12.4 * k, 21.1 * k, 0.1 * k);
    const panel = [[0, 0], [13, 0], [10.4, 21], [0, 21]];
    poly(panel, lin(0, 0, 0, 21, [[0, NAVY], [1, NAVY_D]]));
    dots(panel, 1.0, 19.9, 0.9, 8.2, '150,176,222', 0.13);
    poly([[13, 0], [13.6, 0], [11, 21], [10.4, 21]], CRED);
  }
  return c;
}
function logoSrc(dark) { return $(dark ? '.logo-d' : '.logo-l').getAttribute('src'); }
// the whole top sheet on a canvas (design thumbnails)
async function coverCanvas(design, cv, sheets, dpi) {
  const c = await coverBg(design, coverPhoto(cv, sheets, design), dpi), g = c.getContext('2d'), k = dpi / 2.54;
  const L = coverLayout(design, cv, sheets), lg = L.logo;
  try { g.drawImage(await loadImg(logoSrc(lg.dark)), lg.x * k, lg.y * k, lg.h * LOGO_AR * k, lg.h * k); } catch (e) { /* no logo in thumbnail */ }
  for (const r of L.rects) { g.fillStyle = r.color; g.fillRect(r.x * k, r.y * k, Math.max(1, r.w * k), Math.max(0.6, r.h * k)); }
  for (const t of L.texts) {
    const lh = t.lh || 1.2, [asc, desc] = FM[t.font], sz = t.pt * PT;
    g.font = `${t.bold ? '700 ' : ''}${(sz * k).toFixed(2)}px ${t.font}`; g.fillStyle = t.color;
    if ('letterSpacing' in g) g.letterSpacing = t.ls ? (t.ls * sz * k).toFixed(2) + 'px' : '0px';
    (t.lines || [t.str]).forEach((ln, i) => g.fillText(ln, alignX(t, ln) * k, (t.y + i * lh * sz + ((lh - asc - desc) / 2 + asc) * sz) * k));
  }
  return c;
}
let coverToken = 0;
async function buildCover() {
  const tok = ++coverToken;
  $('#sheet').innerHTML = '<canvas class="cover-bg" id="cover-bg" tabindex="0" aria-label="Top sheet photo. Drag or use the arrow keys to choose what shows."></canvas><div id="cover-fg"></div>';
  fitSheet();
  await fontsReady; if (tok !== coverToken) return;
  updateCoverText();
  await paintCoverBg(110, tok);
  renderThumbs();
}
async function paintCoverBg(dpi, tok) {
  const ph = coverPhoto(S.pres.cover, S.pres.sheets, S.coverDesign);
  const bg = await coverBg(S.coverDesign, ph, dpi);
  if ((tok && tok !== coverToken) || S.pres.cur !== -1) return;
  const c = $('#cover-bg'); if (!c) return;
  $('#sheet-wrap').classList.toggle('cover-photo', !!ph);
  c.width = bg.width; c.height = bg.height; c.getContext('2d').drawImage(bg, 0, 0);
}
function updateCoverText() {
  const fg = $('#cover-fg'); if (!fg || S.pres.cur !== -1) return;
  const L = coverLayout(S.coverDesign, S.pres.cover, S.pres.sheets);
  const lg = L.logo;
  fg.innerHTML = `<img class="cv-logo" src="${logoSrc(lg.dark)}" alt="Oxypro" style="left:${lg.x.toFixed(3)}cm;top:${lg.y}cm;height:${lg.h}cm;width:${(lg.h * LOGO_AR).toFixed(3)}cm">`
    + L.rects.map(r => `<span class="cv-rect" style="left:${r.x.toFixed(3)}cm;top:${r.y.toFixed(3)}cm;width:${r.w.toFixed(3)}cm;height:${r.h}cm;background:${r.color}"></span>`).join('')
    + L.texts.map(t => `<div class="cv" style="left:${t.x.toFixed(3)}cm;top:${t.y.toFixed(3)}cm;width:${t.w.toFixed(3)}cm;font:${t.bold ? 700 : 400} ${t.pt}pt/${(t.pt * (t.lh || 1.2)).toFixed(2)}pt ${t.font === 'Caladea' ? 'Caladea,Cambria,Georgia,serif' : 'Carlito,Calibri,sans-serif'};color:${t.color};${t.ls ? `letter-spacing:${t.ls}em;` : ''}${t.align ? `text-align:${t.align};` : ''}">${esc((t.lines || [t.str]).join('\n'))}</div>`).join('');
}
let thumbTok = 0, thumbTimer = 0;
const queueThumbs = () => { clearTimeout(thumbTimer); thumbTimer = setTimeout(renderThumbs, 350); };
async function renderThumbs() {
  const tok = ++thumbTok;
  for (const d of Object.keys(DESIGNS)) {
    if (!document.querySelector(`[data-thumb="${d}"]`)) return;
    const c = await coverCanvas(d, S.pres.cover, S.pres.sheets, 30);
    const el = document.querySelector(`[data-thumb="${d}"]`);
    if (tok !== thumbTok || !el) return;
    el.width = c.width; el.height = c.height; el.getContext('2d').drawImage(c, 0, 0);
  }
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
  const cv = S.pres.cover, d = S.coverDesign, w = canWrite(), key = photoKey(cv, d);
  const tiles = [['none', 'No photo', null, CLEAN(d) ? 'Clean background' : 'Navy pattern'], ['auto', 'Automatic', null, 'First main photo']];
  for (const x of S.pres.sheets) x.photos.forEach((p, j) => { if (p) tiles.push([`${x.no}:${j}`, `${x.no} ${SLOT_NAMES[j].toLowerCase()}`, p.src]); });
  if (cv.device) tiles.push(['device', 'Your uploaded photo', cv.device.src]);
  const hasPhoto = !!coverPhoto(cv, S.pres.sheets, d);
  $('#sheet-form').innerHTML = `<h3>Top sheet</h3>
    <div class="field"><span class="flabel">Design</span>
      <div class="designs" role="group" aria-label="Top sheet design">${Object.entries(DESIGNS).map(([k, [a, b]]) => `<button type="button" class="dcard" data-design="${k}" aria-pressed="${d === k}"><canvas class="dthumb" data-thumb="${k}" width="351" height="248"></canvas><span>${a}<small>${b}</small></span></button>`).join('')}</div>
      <span class="hint">${w ? 'The design you choose is used for every presentation.' : 'Only library editors can change the design for everyone; this choice applies to this presentation.'}</span></div>
    <label class="check-row"><input type="checkbox" id="c-include" data-ck="include"${cv.include ? ' checked' : ''}> Include the top sheet in the PDF and PowerPoint</label>
    ${COVER_FIELDS.map(([k, label, type, hint]) => `<div class="field"><label for="c-${k}">${esc(label)}</label>${type === 'txt' ? `<textarea class="txt" id="c-${k}" data-ck="${k}">${esc(cv[k])}</textarea>` : `<input class="inp" id="c-${k}" data-ck="${k}" value="${esc(cv[k])}">`}${hint ? `<span class="hint">${esc(hint)}</span>` : ''}</div>`).join('')}
    <div class="field"><span class="flabel">${CLEAN(d) ? 'Background photo' : 'Photo'}</span>
      <div class="ptiles" role="group" aria-label="Photo">${tiles.map(([k, label, src, sub]) => `<button type="button" class="ptile" data-cph="${esc(k)}" aria-pressed="${key === k}" aria-label="${esc(label)}" title="${esc(label)}">${src ? `<img src="${esc(src)}" alt="">` : `${esc(label)}<small>${esc(sub)}</small>`}</button>`).join('')}
        <button type="button" class="ptile up" data-cph-upload>+ Upload<small>From your device</small></button></div>
      <span class="hint">${hasPhoto ? 'Drag the photo on the top sheet to choose what shows.' : CLEAN(d) ? 'Pick any project photo or upload one to use it as the background.' : 'Without a photo the top sheet uses a navy dot pattern from the Oxypro logo.'}</span></div>`;
}
function coverInput(el) {
  const cv = S.pres.cover, k = el.dataset.ck;
  cv[k] = el.type === 'checkbox' ? el.checked : el.value;
  if (!cv.edited.includes(k)) cv.edited.push(k);
  if (k === 'include') { renderPres(); return; }
  updateCoverText(); queueThumbs();
}
function setCoverPhoto(key) {
  const cv = S.pres.cover; if (!cv) return;
  cv.photo = key; cv.focus = null; if (!cv.edited.includes('photo')) cv.edited.push('photo');
  buildCover(); renderCoverForm();
}
function coverDevicePhoto(blob) {
  const cv = S.pres.cover; if (!cv) return;
  cv.device = { blob, src: URL.createObjectURL(blob), x: 50, y: 50 };
  setCoverPhoto('device');
}
async function setDesign(d) {
  if (!DESIGNS[d] || d === S.coverDesign) return;
  S.coverDesign = d; renderRail(); buildCover(); renderCoverForm();
  if (!canWrite()) return;
  try { await DB.doc('settings/cover').set({ design: d, updatedAt: new Date().toISOString() }); toast(`${DESIGNS[d][0]} is now the top sheet for every presentation`); }
  catch (e) { toast(writeError(e)); }
}
// drag (or arrow keys) to choose which part of the photo shows
function bindCoverDrag() {
  const sheet = $('#sheet'); let dr = null, raf = 0;
  const repaint = dpi => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => paintCoverBg(dpi)); };
  const geom = ph => {
    const nat = NAT.get(ph.src); if (!nat) return null;
    const [, , bw, bh] = PHOTO_BOX[S.coverDesign], sc = Math.max(bw / nat[0], bh / nat[1]);
    return { ox: nat[0] * sc - bw, oy: nat[1] * sc - bh };
  };
  sheet.addEventListener('pointerdown', e => {
    if (S.pres.cur !== -1 || e.button) return;
    const cv = S.pres.cover, ph = coverPhoto(cv, S.pres.sheets, S.coverDesign); if (!ph) return;
    const gm = geom(ph); if (!gm) return;
    const r = sheet.getBoundingClientRect(), k = parseFloat(getComputedStyle(sheet).getPropertyValue('--k')) || 0.5;
    const px = (e.clientX - r.left) / k / CM, py = (e.clientY - r.top) / k / CM, [bx, by, bw, bh] = PHOTO_BOX[S.coverDesign];
    if (px < bx || px > bx + bw || py < by || py > by + bh) return;
    e.preventDefault(); try { sheet.setPointerCapture(e.pointerId); } catch (err) { /* ignore */ }
    dr = { sx: e.clientX, sy: e.clientY, x0: ph.x, y0: ph.y, k, moved: false, ...gm };
  });
  sheet.addEventListener('pointermove', e => {
    if (!dr) return;
    const dx = (e.clientX - dr.sx) / dr.k / CM, dy = (e.clientY - dr.sy) / dr.k / CM;
    if (Math.abs(dx) + Math.abs(dy) > 0.05) dr.moved = true;
    S.pres.cover.focus = { x: dr.ox > 0.05 ? clamp(dr.x0 - dx / dr.ox * 100, 0, 100) : dr.x0, y: dr.oy > 0.05 ? clamp(dr.y0 - dy / dr.oy * 100, 0, 100) : dr.y0 };
    repaint(56);
  });
  const end = () => { if (!dr) return; const moved = dr.moved; dr = null; if (moved) { repaint(110); queueThumbs(); } };
  sheet.addEventListener('pointerup', end); sheet.addEventListener('pointercancel', end);
  sheet.addEventListener('keydown', e => {
    if (S.pres.cur !== -1 || e.target.id !== 'cover-bg') return;
    const step = { ArrowLeft: [-3, 0], ArrowRight: [3, 0], ArrowUp: [0, -3], ArrowDown: [0, 3] }[e.key]; if (!step) return;
    const cv = S.pres.cover, ph = coverPhoto(cv, S.pres.sheets, S.coverDesign); if (!ph) return;
    e.preventDefault(); cv.focus = { x: clamp(ph.x + step[0], 0, 100), y: clamp(ph.y + step[1], 0, 100) }; repaint(110); queueThumbs();
  });
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
  const design = S.coverDesign, bg = await coverBg(design, coverPhoto(cv, sheets, design), 200);
  doc.addImage(bg.toDataURL('image/jpeg', 0.9), 'JPEG', 0, 0, 29.7, 21, undefined, 'FAST');
  const L = coverLayout(design, cv, sheets), logos = await logoPngs(), lg = L.logo;
  doc.addImage(logos[lg.dark ? 'dark' : 'light'], 'PNG', lg.x, lg.y, lg.h * LOGO_AR, lg.h, undefined, 'FAST');
  for (const r of L.rects) { doc.setFillColor(r.color); doc.rect(r.x, r.y, r.w, r.h, 'F'); }
  for (const t of L.texts) {
    const lh = t.lh || 1.2, [asc, desc] = FM[t.font], sz = t.pt * PT;
    doc.setFont(t.font, t.bold ? 'bold' : 'normal'); doc.setFontSize(t.pt); doc.setTextColor(t.color);
    (t.lines || [t.str]).forEach((ln, i) => doc.text(ln, alignX(t, ln), t.y + i * lh * sz + ((lh - asc - desc) / 2 + asc) * sz, t.ls ? { charSpace: t.ls * sz } : undefined));
  }
}
async function pptxCover(pptx, cv, sheets, I, strip) {
  const design = S.coverDesign, sl = pptx.addSlide(); sl.background = { color: 'FFFFFF' };
  const bg = await coverBg(design, coverPhoto(cv, sheets, design), 200);
  sl.addImage({ data: strip(bg.toDataURL('image/jpeg', 0.9)), x: 0, y: 0, w: I(29.7), h: I(21), altText: 'Top sheet background' });
  const L = coverLayout(design, cv, sheets), logos = await logoPngs(), lg = L.logo;
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

"""
s = s[:a] + COVER + s[b:]
open(P, 'w').write(s)
print('patched', len(s))
