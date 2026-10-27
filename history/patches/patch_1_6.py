"""v1.6.0: View / Present. A full-screen viewer that runs the presentation page by page (top sheet, project sheets,
summary) exactly as the PDF and PowerPoint will show it, with an All pages overview for a quick review."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('Version 1.5.0 (27 Oct 2026)', 'Version 1.6.0 (27 Oct 2026)')

# ---------- tokens: the viewer is a dark stage in both themes (like a projector screen) ----------
rep("  --paper:#FFFFFF; --paper-ink:#2B2B2B;",
    "  --show-bg:#0D0F12; --show-fg:#F2F3F5; --show-muted:#A8ADB5; --show-line:rgba(255,255,255,.16); --show-hover:rgba(255,255,255,.1);\n  --paper:#FFFFFF; --paper-ink:#2B2B2B;")

# ---------- styles ----------
CSS = r"""
/* ---------- View / Present ---------- */
.show{position:fixed;inset:0;z-index:80;display:flex;flex-direction:column;background:var(--show-bg);color:var(--show-fg);font:15px/1.4 var(--f-body);outline:none;color-scheme:dark}
.show[hidden],.show [hidden]{display:none!important}
.show-bar{flex:0 0 auto;display:flex;align-items:center;gap:12px;min-height:58px;padding:max(8px,env(safe-area-inset-top,0px)) max(16px,env(safe-area-inset-right,0px)) 8px max(16px,env(safe-area-inset-left,0px));transition:opacity .3s}
.show-where{display:flex;align-items:baseline;gap:12px;min-width:0;flex:1 1 auto}
.show-count{font:600 17px/1 var(--f-cond);letter-spacing:.06em;white-space:nowrap;font-variant-numeric:tabular-nums}
.show-label{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--show-muted);font-size:14.5px}
.show-tools{display:flex;gap:6px;flex:0 0 auto}
.sbtn{display:inline-flex;align-items:center;justify-content:center;gap:7px;min-height:38px;padding:0 13px;border-radius:5px;border:1px solid var(--show-line);background:transparent;color:var(--show-fg);font:600 14px/1 var(--f-body);cursor:pointer;white-space:nowrap}
.sbtn:hover{background:var(--show-hover)}
.sbtn[aria-pressed="true"]{background:var(--show-fg);color:var(--show-bg);border-color:var(--show-fg)}
.sbtn svg{width:17px;height:17px;flex:none}
.sbtn-primary{background:var(--red);border-color:var(--red);color:#FFFFFF}
.sbtn-primary:hover{background:var(--red-hover);border-color:var(--red-hover)}
.show :focus-visible{outline:2px solid #FFFFFF;outline-offset:2px}
.show-stage{flex:1 1 auto;position:relative;min-height:0;display:flex;align-items:center;justify-content:center;overflow:hidden;touch-action:pan-y pinch-zoom;user-select:none;-webkit-user-select:none}
.show-deck{position:relative;flex:0 0 auto;background:#FFFFFF;box-shadow:0 10px 50px rgba(0,0,0,.55)}
.show-deck.gone{visibility:hidden}
.show-page{opacity:0;visibility:hidden;transition:opacity .28s ease,visibility 0s linear .28s}
.show-page.on{opacity:1;visibility:visible;transition:opacity .28s ease}
.show .frame{touch-action:auto;cursor:inherit}
.show .frame img{pointer-events:none}
.show-nav{position:absolute;top:50%;z-index:2;transform:translateY(-50%);width:48px;height:48px;border-radius:50%;border:0;background:rgba(18,20,24,.62);color:#FFFFFF;display:grid;place-items:center;cursor:pointer;transition:opacity .3s,background .15s}
.show-nav:hover{background:rgba(18,20,24,.85)}
.show-nav svg{width:24px;height:24px}
.show-nav.prev{left:max(12px,env(safe-area-inset-left,0px))}
.show-nav.next{right:max(12px,env(safe-area-inset-right,0px))}
.show-nav:disabled{opacity:0;pointer-events:none}
.show-busy{position:absolute;inset:0;display:grid;place-items:center;color:var(--show-muted);font-size:15px}
.show-end{position:absolute;inset:0;z-index:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:24px;text-align:center}
.show-end .se-eyebrow{margin:0;font:600 13px var(--f-cond);letter-spacing:.14em;text-transform:uppercase;color:#F0525A}
.show-end h2{margin:0;font:600 30px/1.1 var(--f-cond);letter-spacing:.02em}
.show-end p{margin:0;color:var(--show-muted);max-width:44ch}
.show-end .se-btns{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:10px}
.show-foot{flex:0 0 auto;display:flex;align-items:center;gap:14px;min-height:38px;padding:6px max(16px,env(safe-area-inset-right,0px)) max(8px,env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));transition:opacity .3s}
.show-progress{position:relative;flex:1 1 auto;height:3px;border-radius:2px;background:rgba(255,255,255,.14);overflow:hidden}
.show-progress span{position:absolute;left:0;top:0;bottom:0;width:0;background:var(--red);transition:width .25s ease}
.show-help{margin:0;flex:0 1 auto;color:var(--show-muted);font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
.show-help .h-touch{display:none}
@media (hover:none){.show-help .h-key{display:none}.show-help .h-touch{display:inline}}
.show.fs:not(.gridding) .show-bar{position:absolute;left:0;right:0;top:0;z-index:3;background:rgba(13,15,18,.9);box-shadow:0 1px 0 var(--show-line)}
.show.fs .show-foot{position:absolute;left:0;right:0;bottom:0;z-index:3;min-height:0;padding:0;background:none}
.show.fs .show-help{display:none}
.show.fs .show-progress{border-radius:0}
.show.gridding .show-foot{display:none}
.show.idle .show-nav{opacity:0;pointer-events:none}
.show.fs.idle .show-bar,.show.fs.idle .show-foot{opacity:0;pointer-events:none}
.show.fs.idle{cursor:none}
.show-grid{flex:1 1 auto;min-height:0;overflow:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,230px),1fr));gap:22px 18px;align-content:start;padding:10px max(16px,env(safe-area-inset-right,0px)) 28px max(16px,env(safe-area-inset-left,0px))}
.show-thumb{display:flex;flex-direction:column;gap:8px;min-width:0;padding:0;border:0;background:none;color:var(--show-fg);text-align:left;cursor:pointer;font:inherit}
.show-tf{position:relative;display:block;width:100%;aspect-ratio:29.7/21;overflow:hidden;background:#FFFFFF;border-radius:3px;box-shadow:0 0 0 1px var(--show-line)}
.show-thumb:hover .show-tf{box-shadow:0 0 0 2px var(--show-muted)}
.show-thumb.cur .show-tf{box-shadow:0 0 0 3px var(--red)}
.show-tc{display:flex;gap:8px;align-items:baseline;min-width:0;font-size:13.5px;line-height:1.3}
.show-tc b{font:600 15px var(--f-cond);color:var(--show-muted);font-variant-numeric:tabular-nums}
.show-tc span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
@media (max-width:700px){
  .sbtn .sl{display:none}
  .sbtn{padding:0 10px}
  .show-label{font-size:13px}
  .show-nav{width:40px;height:40px}
  .show-help{display:none}
}
"""
rep(".sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}\n</style>",
    ".sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}\n" + CSS.strip('\n') + "\n</style>")

# ---------- markup ----------
rep("""        <button type="button" class="btn btn-primary" id="dl-pdf">Download PDF</button>""",
    """        <button type="button" class="btn" id="show-btn" title="Run the presentation full screen, or review all pages at a glance"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="3.5" width="19" height="13" rx="1.5"/><path d="M10 7.6v4.8l4.2-2.4z" fill="currentColor" stroke-width="1.4"/><path d="M8 20.5h8M12 16.5v4"/></svg>View / Present</button>
        <button type="button" class="btn btn-primary" id="dl-pdf">Download PDF</button>""")

ICO = {
    'grid': '<rect x="3.5" y="4.5" width="7" height="6" rx="1"/><rect x="13.5" y="4.5" width="7" height="6" rx="1"/><rect x="3.5" y="13.5" width="7" height="6" rx="1"/><rect x="13.5" y="13.5" width="7" height="6" rx="1"/>',
    'fs': '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
    'x': '<path d="M6 6l12 12M18 6L6 18"/>',
    'prev': '<path d="M15 18l-6-6 6-6"/>',
    'next': '<path d="M9 18l6-6-6-6"/>',
}
svg = lambda k, w='2': f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICO[k]}</svg>'
MARKUP = f"""<div class="show" id="show" role="dialog" aria-modal="true" aria-label="Presentation viewer" tabindex="-1" hidden>
  <div class="show-bar" id="show-bar">
    <div class="show-where"><span class="show-count" id="show-count"></span><span class="show-label" id="show-label"></span></div>
    <div class="show-tools">
      <button type="button" class="sbtn" id="show-grid" aria-pressed="false" aria-label="All pages" title="All pages (G)">{svg('grid', '1.8')}<span class="sl">All pages</span></button>
      <button type="button" class="sbtn" id="show-fs" aria-label="Full screen" title="Full screen (F)">{svg('fs')}<span class="sl" id="show-fs-t">Full screen</span></button>
      <button type="button" class="sbtn" id="show-close" aria-label="Close and go back to editing" title="Close (Esc)">{svg('x')}<span class="sl">Close</span></button>
    </div>
  </div>
  <div class="show-stage" id="show-stage">
    <div class="show-deck" id="show-deck"></div>
    <button type="button" class="show-nav prev" id="show-prev" aria-label="Previous page">{svg('prev', '2.2')}</button>
    <button type="button" class="show-nav next" id="show-next" aria-label="Next page">{svg('next', '2.2')}</button>
    <div class="show-end" id="show-end" hidden>
      <p class="se-eyebrow">End of presentation</p>
      <h2 id="show-end-h"></h2>
      <p>Save it as a file, or go back and fix something first.</p>
      <div class="se-btns">
        <button type="button" class="sbtn sbtn-primary" data-end="pdf">Download PDF</button>
        <button type="button" class="sbtn" data-end="pptx">Download PowerPoint</button>
        <button type="button" class="sbtn" data-end="restart">Start again</button>
        <button type="button" class="sbtn" data-end="close">Back to editing</button>
      </div>
    </div>
    <div class="show-busy" id="show-busy">Preparing the pages…</div>
  </div>
  <div class="show-grid" id="show-gridview" hidden></div>
  <div class="show-foot" id="show-foot">
    <div class="show-progress" aria-hidden="true"><span id="show-prog"></span></div>
    <p class="show-help" id="show-help"></p>
  </div>
  <p class="sr" id="show-live" aria-live="polite"></p>
</div>
"""
rep('<div class="modal" id="modal" hidden></div>', '<div class="modal" id="modal" hidden></div>\n' + MARKUP.rstrip('\n'))

# ---------- script ----------
JS = r"""
/* ---------- View / Present ---------- */
// A snapshot of the presentation as the PDF will print it: top sheet, project sheets, summary pages.
// Empty frames and placeholder text are left out, like the PDF. All pages share one deck scaled to fit the screen.
const SH = { open: false, tok: 0, pages: [], els: [], cur: 0, grid: false, urls: [], inert: [], ovf: '', idleT: 0, wheelT: 0, fsByUs: false, wasFs: false, px: -1, py: -1, sw: null };
const fsEl = () => document.fullscreenElement || document.webkitFullscreenElement || null;
const fsOk = () => !!(document.fullscreenEnabled || document.webkitFullscreenEnabled);
function enterFs() {
  const el = $('#show');
  try { const p = el.requestFullscreen ? el.requestFullscreen({ navigationUI: 'hide' }) : el.webkitRequestFullscreen ? el.webkitRequestFullscreen() : null; if (p && p.catch) p.catch(() => {}); } catch (e) { /* stays in the window */ }
}
async function exitFs() {
  if (!fsEl()) return; SH.fsByUs = true;
  try { await (document.exitFullscreen ? document.exitFullscreen() : document.webkitExitFullscreen && document.webkitExitFullscreen()); } catch (e) { /* already out */ }
}
function toggleFs() { if (!fsOk()) return; if (fsEl()) exitFs(); else enterFs(); }
function onFsChange() {
  const on = fsEl() === $('#show');
  $('#show').classList.toggle('fs', on);
  $('#show-fs-t').textContent = on ? 'Exit full screen' : 'Full screen';
  $('#show-fs').setAttribute('aria-label', on ? 'Exit full screen' : 'Full screen');
  // Esc in full screen ends the show, as in PowerPoint; the Exit full screen button keeps the viewer open
  if (!on && SH.open && SH.wasFs && !SH.fsByUs && !SH.grid) closeShow();
  SH.wasFs = on; SH.fsByUs = false; fitShow(); wake();
}
function sheetPageHTML(sh) {
  const L = layoutSheet(sh); let h = '';
  FRAMES.forEach((f, i) => {
    const ph = sh.photos[i]; if (!ph) return;
    h += `<div class="frame" style="left:${f.x}cm;top:${f.y}cm;width:${f.w}cm;height:${f.h}cm"><img src="${esc(ph.src)}" alt="" draggable="false" style="object-position:${ph.x}% ${ph.y}%"></div>`;
  });
  if (L.eyebrow.length) h += `<div class="t t-eyebrow" style="left:${TX}cm;top:${EYE_TOP}cm;width:${TW}cm">${esc(L.eyebrow[0])}</div>`;
  if (L.name.lines.length) h += `<div class="t t-name" style="left:${TX}cm;top:${NAME_TOP}cm;width:${TW}cm;font-size:${L.name.pt}pt">${esc(L.name.lines.join('\n'))}</div>`;
  if (L.scope.length) h += `<div class="t t-scope" style="left:${TX}cm;top:${L.scopeTop.toFixed(3)}cm;width:${TW}cm">${esc(L.scope.join('\n'))}</div>`;
  L.details.forEach(d => {
    if (!d.lines.length) return;
    h += `<svg class="t-ico" style="left:${d.x}cm;top:${(d.top - 0.04).toFixed(2)}cm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[d.icon]}</svg>`
      + `<div class="t t-detv" style="left:${d.tx}cm;top:${d.top}cm;width:${d.tw}cm">${esc(d.lines.join('\n'))}</div>`;
  });
  return h;
}
async function buildShowPages() {
  const P = S.pres, sheets = P.sheets, cv = P.cover, out = [];
  if (cv && cv.include) {
    const design = cv.design || S.coverDesign;
    const px = Math.max(screen.width || 1280, screen.height || 800) * (window.devicePixelRatio || 1);
    const bg = await coverBg(design, coverPhoto(cv, sheets, design), clamp(Math.ceil(px / 29.7 * 2.54), 96, 220));
    const url = await new Promise(res => { try { bg.toBlob(b => res(b ? URL.createObjectURL(b) : bg.toDataURL('image/jpeg', 0.92)), 'image/jpeg', 0.92); } catch (e) { res(bg.toDataURL('image/jpeg', 0.92)); } });
    if (url.startsWith('blob:')) SH.urls.push(url);
    out.push({ label: `Top sheet · ${DESIGNS[design][0]}`, go: { cur: -1 }, html: `<img class="cover-bg" src="${url}" alt="" draggable="false">` + specHTML(coverLayout(design, cv, sheets)) });
  }
  sheets.forEach((sh, i) => out.push({ label: `${sh.no} · ${sh.name || 'Untitled'}`, go: { cur: i }, html: sheetPageHTML(sh) }));
  const sum = summaryOut() || [];
  sum.forEach((pg, j) => out.push({ label: sum.length > 1 ? `Project summary · page ${j + 1} of ${sum.length}` : 'Project summary', go: { cur: -2, page: j }, html: specHTML(pg) }));
  return out;
}
// a photo that fails to load is left out, as in the PDF
const dropBroken = root => root.querySelectorAll('img').forEach(img => img.addEventListener('error', () => { (img.closest('.frame') || img).remove(); }, { once: true }));
function fillPage(j) {
  const el = SH.els[j]; if (!el || el.dataset.ready) return;
  el.innerHTML = SH.pages[j].html; el.dataset.ready = '1'; dropBroken(el);
}
function fitShow() {
  if (!SH.open || SH.grid) return;
  const st = $('#show-stage'), w = st.clientWidth, h = st.clientHeight; if (!w || !h) return;
  const pad = $('#show').classList.contains('fs') ? 0 : w < 700 ? 8 : 20;
  const k = Math.max(0.05, Math.min((w - 2 * pad) / (29.7 * CM), (h - 2 * pad) / (21 * CM)));
  const d = $('#show-deck'); d.style.width = (29.7 * CM * k).toFixed(1) + 'px'; d.style.height = (21 * CM * k).toFixed(1) + 'px'; d.style.setProperty('--k', k.toFixed(5));
}
function fitGrid() { const f = $('#show-gridview .show-tf'); if (f && f.clientWidth) $('#show-gridview').style.setProperty('--k', (f.clientWidth / (29.7 * CM)).toFixed(5)); }
function showGo(i) {
  const n = SH.pages.length; if (!n) return;
  i = clamp(i, 0, n); SH.cur = i;   // index n is the closing card
  for (let j = i - 1; j <= i + 2; j++) fillPage(j);
  SH.els.forEach((el, j) => { el.classList.toggle('on', j === i); el.setAttribute('aria-hidden', j === i ? 'false' : 'true'); });
  const end = i === n;
  $('#show-end').hidden = !end; $('#show-deck').classList.toggle('gone', end);
  $('#show-count').textContent = end ? 'End' : `${i + 1} / ${n}`;
  $('#show-label').textContent = end ? `${n} page${n === 1 ? '' : 's'}` : SH.pages[i].label;
  $('#show-prog').style.width = (end ? 100 : (i + 1) / n * 100).toFixed(2) + '%';
  $('#show-prev').disabled = i === 0; $('#show-next').disabled = end;
  $('#show-live').textContent = end ? 'End of presentation' : `Page ${i + 1} of ${n}: ${SH.pages[i].label}`;
}
function wake() {
  const el = $('#show'); el.classList.remove('idle'); clearTimeout(SH.idleT);
  if (!SH.open || SH.grid) return;
  SH.idleT = setTimeout(() => {
    if (!SH.open || SH.grid || $('#show-bar').matches(':hover') || $('#show-foot').matches(':hover') || (document.activeElement && document.activeElement.matches('.show-bar button:focus-visible'))) return wake();
    el.classList.add('idle');
  }, 2600);
}
function gridHTML() {
  return SH.pages.map((p, i) => `<button type="button" class="show-thumb" data-go="${i}" aria-label="Page ${i + 1}: ${esc(p.label)}"><span class="show-tf" aria-hidden="true"><span class="sheet">${p.html.replace(/<img /g, '<img loading="lazy" ')}</span></span><span class="show-tc" aria-hidden="true"><b>${i + 1}</b><span>${esc(p.label)}</span></span></button>`).join('');
}
function setGrid(on) {
  if (!SH.pages.length) return;
  SH.grid = on; const g = $('#show-gridview');
  $('#show-stage').hidden = on; g.hidden = !on; $('#show-grid').setAttribute('aria-pressed', String(on)); $('#show').classList.toggle('gridding', on);
  if (on) {
    clearTimeout(SH.idleT); $('#show').classList.remove('idle');
    if (!g.innerHTML) { g.innerHTML = gridHTML(); dropBroken(g); }
    const cur = Math.min(SH.cur, SH.pages.length - 1);
    g.querySelectorAll('.show-thumb').forEach((t, i) => { t.classList.toggle('cur', i === cur); if (i === cur) t.setAttribute('aria-current', 'page'); else t.removeAttribute('aria-current'); });
    fitGrid();
    $('#show-count').textContent = `${SH.pages.length} page${SH.pages.length === 1 ? '' : 's'}`; $('#show-label').textContent = 'Choose a page to present from there';
    $('#show-live').textContent = 'All pages';
    const t = g.querySelectorAll('.show-thumb')[cur]; if (t) { t.focus({ preventScroll: true }); t.scrollIntoView({ block: 'center' }); }
  } else {
    fitShow(); showGo(SH.cur); $('#show').focus({ preventScroll: true }); wake();
  }
}
function showHelp() {
  const keys = ['← → or Space to move', 'Home / End', 'G all pages'];
  if (fsOk()) keys.push('F full screen');
  keys.push('Esc back to editing');
  $('#show-help').innerHTML = `<span class="h-key">${keys.join('  ·  ')}</span><span class="h-touch">Swipe, or tap the left or right side, to move</span>`;
}
async function openShow() {
  if (SH.open || !S.pres.sheets.length) return;
  const show = $('#show'), tok = ++SH.tok;
  Object.assign(SH, { open: true, grid: false, cur: 0, pages: [], els: [], wasFs: false, fsByUs: false, sw: null });
  SH.inert = [...document.body.children].filter(el => el !== show && el.id !== 'toast' && el.tagName !== 'SCRIPT' && !el.inert);
  SH.inert.forEach(el => { el.inert = true; });
  SH.ovf = document.documentElement.style.overflow; document.documentElement.style.overflow = 'hidden';
  $('#show-deck').innerHTML = ''; $('#show-deck').classList.remove('gone'); $('#show-end').hidden = true; $('#show-busy').hidden = false;
  $('#show-gridview').hidden = true; $('#show-gridview').innerHTML = ''; $('#show-stage').hidden = false; $('#show-grid').setAttribute('aria-pressed', 'false');
  $('#show-count').textContent = ''; $('#show-label').textContent = ''; $('#show-prog').style.width = '0';
  $('#show-prev').disabled = $('#show-next').disabled = true;
  $('#show-fs').hidden = !fsOk(); showHelp();
  show.hidden = false; show.classList.remove('idle', 'fs', 'gridding'); show.focus({ preventScroll: true });
  if (fsOk()) enterFs();   // inside the click, so the browser allows it; if refused the viewer fills the window
  try {
    await fontsReady;
    const pages = await buildShowPages();
    if (tok !== SH.tok || !SH.open) return;
    SH.pages = pages; const n = pages.length;
    $('#show-deck').innerHTML = pages.map((p, i) => `<div class="sheet show-page" role="group" aria-roledescription="page" aria-label="Page ${i + 1} of ${n}: ${esc(p.label)}" aria-hidden="true"></div>`).join('');
    SH.els = [...$('#show-deck').children];
    $('#show-end-h').textContent = `That's all ${n} page${n === 1 ? '' : 's'}`;
    $('#show-busy').hidden = true; fitShow(); showGo(0); wake();
  } catch (e) {
    if (tok === SH.tok && SH.open) { await closeShow(true); toast('The viewer could not open: ' + ((e && e.message) || e) + '. Try again.', 6000); }
  }
}
async function closeShow(stay) {
  if (!SH.open) return;
  SH.open = false; SH.tok++; clearTimeout(SH.idleT);
  await exitFs();
  const show = $('#show'); show.hidden = true; show.classList.remove('fs', 'idle', 'gridding');
  $('#show-deck').innerHTML = ''; $('#show-gridview').innerHTML = ''; SH.els = [];
  SH.urls.forEach(u => URL.revokeObjectURL(u)); SH.urls = [];
  SH.inert.forEach(el => { el.inert = false; }); SH.inert = [];
  document.documentElement.style.overflow = SH.ovf || '';
  const pg = SH.pages[SH.cur]; SH.pages = [];
  // land on the page you were looking at, ready to fix it
  if (!stay && pg && S.view === 'pres') {
    if (pg.go.cur === -1 ? S.pres.cover : pg.go.cur === -2 ? S.pres.summary : S.pres.sheets[pg.go.cur]) {
      S.pres.cur = pg.go.cur; if (pg.go.page != null) S.pres.summary.page = pg.go.page; renderPres();
    }
  }
  const b = $('#show-btn'); if (b) b.focus({ preventScroll: true });
}
function trapTab(e) {
  const f = [...$('#show').querySelectorAll('button:not([disabled])')].filter(b => !b.closest('[hidden]') && b.getClientRects().length);
  if (!f.length) { e.preventDefault(); return; }
  const i = f.indexOf(document.activeElement);
  if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); }
  else if (!e.shiftKey && (i === -1 || i === f.length - 1)) { e.preventDefault(); f[0].focus(); }
}
function gridKey(e) {
  const g = $('#show-gridview'), th = [...g.querySelectorAll('.show-thumb')]; if (!th.length) return false;
  const cols = Math.max(1, getComputedStyle(g).gridTemplateColumns.split(' ').filter(Boolean).length);
  const step = { ArrowRight: 1, ArrowLeft: -1, ArrowDown: cols, ArrowUp: -cols, Home: -1e6, End: 1e6 }[e.key];
  if (step == null) return false;
  let i = th.indexOf(document.activeElement); if (i < 0) i = Math.min(SH.cur, th.length - 1);
  th[clamp(i + step, 0, th.length - 1)].focus(); return true;
}
function showKey(e) {
  if (!SH.open) return;
  const k = e.key;
  if (k === 'Tab') { wake(); trapTab(e); return; }
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const onBtn = !!(e.target.closest && e.target.closest('button'));
  let done = true;
  if (k === 'Escape') { if (SH.grid) setGrid(false); else closeShow(); }
  else if (!SH.pages.length) done = false;
  else if (k === 'g' || k === 'G') setGrid(!SH.grid);
  else if (k === 'f' || k === 'F') toggleFs();
  else if (SH.grid) done = gridKey(e);
  else if ((k === ' ' || k === 'Enter') && onBtn) done = false;
  else if (k === ' ' && e.shiftKey) showGo(SH.cur - 1);
  else if (['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'Enter', 'n', 'N'].includes(k)) showGo(SH.cur + 1);
  else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace', 'p', 'P'].includes(k)) showGo(SH.cur - 1);
  else if (k === 'Home') showGo(0);
  else if (k === 'End') showGo(SH.pages.length - 1);
  else done = false;
  if (done) { e.preventDefault(); e.stopPropagation(); }
}
function bindShow() {
  const show = $('#show'), stage = $('#show-stage');
  const refocus = e => { if (e.detail) show.focus({ preventScroll: true }); };   // after a mouse click, Space moves pages again
  $('#show-btn').addEventListener('click', openShow);
  $('#show-close').addEventListener('click', () => closeShow());
  $('#show-grid').addEventListener('click', () => setGrid(!SH.grid));
  $('#show-fs').addEventListener('click', e => { toggleFs(); refocus(e); });
  $('#show-prev').addEventListener('click', e => { showGo(SH.cur - 1); refocus(e); });
  $('#show-next').addEventListener('click', e => { showGo(SH.cur + 1); refocus(e); });
  $('#show-end').addEventListener('click', async e => {
    const b = e.target.closest('[data-end]'); if (!b) return; const a = b.dataset.end;
    if (a === 'restart') { showGo(0); refocus(e); return; }
    if (a === 'close') { closeShow(); return; }
    await closeShow(true);   // out of full screen first, so the save prompt is visible
    if (a === 'pdf') downloadPdf(); else downloadPptx();
  });
  $('#show-gridview').addEventListener('click', e => { const t = e.target.closest('[data-go]'); if (t) { SH.cur = +t.dataset.go; setGrid(false); } });
  document.addEventListener('keydown', showKey, true);
  document.addEventListener('fullscreenchange', onFsChange); document.addEventListener('webkitfullscreenchange', onFsChange);
  show.addEventListener('pointermove', e => { if (Math.abs(e.clientX - SH.px) + Math.abs(e.clientY - SH.py) < 3) return; SH.px = e.clientX; SH.py = e.clientY; wake(); });
  // click or tap moves on; on touch, tapping the left side or swiping right goes back
  stage.addEventListener('pointerdown', e => { if (e.button || e.target.closest('button') || !SH.pages.length) return; SH.sw = { x: e.clientX, y: e.clientY }; if (e.pointerType !== 'mouse') wake(); });
  stage.addEventListener('pointercancel', () => { SH.sw = null; });
  stage.addEventListener('pointerup', e => {
    const s = SH.sw; SH.sw = null; if (!s || e.target.closest('button')) return;
    const dx = e.clientX - s.x, dy = e.clientY - s.y;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.2) { showGo(SH.cur + (dx < 0 ? 1 : -1)); return; }
    if (Math.abs(dx) + Math.abs(dy) > 12 || SH.cur >= SH.pages.length) return;
    const r = stage.getBoundingClientRect();
    showGo(SH.cur + (e.pointerType !== 'mouse' && e.clientX < r.left + r.width * 0.3 ? -1 : 1));
  });
  stage.addEventListener('wheel', e => {
    if (e.ctrlKey || SH.grid || !SH.pages.length) return;
    e.preventDefault(); const now = Date.now();
    if (now < SH.wheelT) { SH.wheelT = Math.max(SH.wheelT, now + 250); return; }   // one flick, however long its glide, turns one page
    const d = Math.abs(e.deltaY) >= Math.abs(e.deltaX) ? e.deltaY : e.deltaX; if (Math.abs(d) < 4) return;
    SH.wheelT = now + 500; showGo(SH.cur + (d > 0 ? 1 : -1));
  }, { passive: false });
  if (window.ResizeObserver) new ResizeObserver(() => { fitShow(); if (SH.grid) fitGrid(); }).observe(show);
  else window.addEventListener('resize', () => { fitShow(); if (SH.grid) fitGrid(); });
}
"""
rep("/* ---------- modal / global ---------- */", JS.strip('\n') + "\n\n/* ---------- modal / global ---------- */")
rep("""  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (!$('#modal').hidden) closeModal();""",
    """  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape' || SH.open) return;
    if (!$('#modal').hidden) closeModal();""")
rep("  bindLibrary(); bindPres(); bindGlobal(); bindView(); renderAll();",
    "  bindLibrary(); bindPres(); bindShow(); bindGlobal(); bindView(); renderAll();")
# the download buttons are bound as listeners; keep the event object out of the functions
rep("  $('#dl-pdf').addEventListener('click', downloadPdf);\n  $('#dl-pptx').addEventListener('click', downloadPptx);",
    "  $('#dl-pdf').addEventListener('click', () => downloadPdf());\n  $('#dl-pptx').addEventListener('click', () => downloadPptx());")
open(P, 'w').write(s)
print('patched', len(s))
