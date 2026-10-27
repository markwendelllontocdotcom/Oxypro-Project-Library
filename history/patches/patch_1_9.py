"""v1.9.0: PQP details and file asks which library photo becomes the PQP cover photo (main photo by default).
Save PQP file carries it; Open in PQP Maker copies it to the clipboard and PQP Maker asks to paste it."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('Version 1.8.1 (27 Oct 2026)', 'Version 1.9.0 (27 Oct 2026)')
rep("const APP_VERSION = '1.8.1';", "const APP_VERSION = '1.9.0';")

# photo helpers take the chosen slot
rep("""async function pqpPhoto(p) {
  const ph = photosOf(p)[0]; if (!ph) return null;
  const img = await loadImg(blobUrl(ph.id)), k = Math.min(1, 2000 / Math.max(img.naturalWidth, img.naturalHeight));
  const c = document.createElement('canvas'); c.width = Math.round(img.naturalWidth * k); c.height = Math.round(img.naturalHeight * k);
  const g = c.getContext('2d'); g.fillStyle = '#FFFFFF'; g.fillRect(0, 0, c.width, c.height); g.imageSmoothingQuality = 'high'; g.drawImage(img, 0, 0, c.width, c.height);
  return { name: `${safeName(p.name || p.no)} - Cover Photo.jpg`, type: 'image/jpeg', dataUrl: c.toDataURL('image/jpeg', 0.86), w: c.width, h: c.height };
}""", """async function pqpCanvas(p, slot) {
  const ph = photosOf(p)[slot]; if (!ph) return null;
  const img = await loadImg(blobUrl(ph.id)), k = Math.min(1, 2000 / Math.max(img.naturalWidth, img.naturalHeight));
  const c = document.createElement('canvas'); c.width = Math.round(img.naturalWidth * k); c.height = Math.round(img.naturalHeight * k);
  const g = c.getContext('2d'); g.fillStyle = '#FFFFFF'; g.fillRect(0, 0, c.width, c.height); g.imageSmoothingQuality = 'high'; g.drawImage(img, 0, 0, c.width, c.height);
  return c;
}
async function pqpPhoto(p, slot = 0) {
  const c = await pqpCanvas(p, slot); if (!c) return null;
  return { name: `${safeName(p.name || p.no)} - Cover Photo.jpg`, type: 'image/jpeg', dataUrl: c.toDataURL('image/jpeg', 0.86), w: c.width, h: c.height };
}
// the clipboard takes PNG only
const PQP_PNG = new Map();
function pqpPng(p, slot) {
  const key = pqpKey(p) + '|' + slot;
  if (!PQP_PNG.has(key)) {
    if (PQP_PNG.size > 6) PQP_PNG.clear();
    const pr = pqpCanvas(p, slot).then(c => new Promise((res, rej) => { if (!c) return rej(new Error('no photo')); c.toBlob(b => b ? res(b) : rej(new Error('no image')), 'image/png'); }));
    pr.catch(() => PQP_PNG.delete(key)); PQP_PNG.set(key, pr);
  }
  return PQP_PNG.get(key);
}""")
# the link says whether a photo waits on the clipboard
rep("""async function pqpLink(p) {
  const { pr } = pqpData(p);
  const raw = new TextEncoder().encode(JSON.stringify({ format: 'pqp-maker-project', version: 1, app: 'Oxypro Project Library ' + APP_VERSION, source: { library: p.no }, project: pr }));""",
    """async function pqpLink(p, withPhoto) {
  const { pr } = pqpData(p);
  const raw = new TextEncoder().encode(JSON.stringify({ format: 'pqp-maker-project', version: 1, app: 'Oxypro Project Library ' + APP_VERSION, source: { library: p.no, ...(withPhoto ? { photo: 'clipboard' } : {}) }, project: pr }));""")
rep("""function pqpLinkFor(p) {
  const key = pqpKey(p);
  if (PQP_READY.has(key)) return Promise.resolve(PQP_READY.get(key));
  return pqpLink(p).then(url => { if (PQP_READY.size > 50) PQP_READY.clear(); PQP_READY.set(key, url); return url; });
}""", """function pqpLinkFor(p, withPhoto = !!photosOf(p)[0]) {
  const key = pqpKey(p) + (withPhoto ? '|ph' : '');
  if (PQP_READY.has(key)) return Promise.resolve(PQP_READY.get(key));
  return pqpLink(p, withPhoto).then(url => { if (PQP_READY.size > 50) PQP_READY.clear(); PQP_READY.set(key, url); return url; });
}""")

# the dialog: cover photo question, then the two buttons
rep("""  const { rows, otherAu, otherCo } = pqpData(p), hasPhoto = !!photosOf(p)[0];
  const cell = v => esc(Array.isArray(v) ? v.join(', ') : String(v)).replace(/\\n/g, '<br>');""",
    """  const { rows, otherAu, otherCo } = pqpData(p), phs = photosOf(p);
  let slot = phs.findIndex(Boolean);   // the main photo when there is one
  const cell = v => esc(Array.isArray(v) ? v.join(', ') : String(v)).replace(/\\n/g, '<br>');
  const tiles = phs.map((x, i) => x ? `<button type="button" class="ptile" data-pqp-ph="${i}" aria-pressed="${i === slot}" aria-label="Use ${i === 0 ? 'the main photo' : SLOT_NAMES[i].toLowerCase()}"><img src="${esc(blobUrl(x.id))}" alt="" style="object-position:${+x.x || 50}% ${+x.y || 50}%"><span class="pt-cap">${i === 0 ? 'Main photo' : esc(SLOT_NAMES[i])}</span></button>` : '').join('')
    + `<button type="button" class="ptile" data-pqp-ph="-1" aria-pressed="${slot < 0}">No photo<small>PQP Maker shows the photo box</small></button>`;""")
rep("""      <p style="margin:0"><strong>Open in PQP Maker</strong> creates the PQP with these details in a new tab. <strong>Save PQP file</strong> keeps them, with the cover photo, as <strong>${esc(safeName(p.name || p.no))}.pqp</strong>: in PQP Maker choose <strong>Open</strong> and pick the file.</p>""",
    """      <div class="field"><span class="flabel">Cover photo for the PQP</span>
        <p class="d-note" style="margin:0">${slot >= 0 ? 'Use the main photo, or choose another photo of this project from the library.' : 'This project has no photos in the library yet.'}</p>
        <div class="ptiles pqp-ph" role="group" aria-label="Cover photo">${tiles}</div></div>
      <p style="margin:0" id="pqp-how"></p>""")
rep("""        <tr><td>Cover Photo</td><td>${hasPhoto ? 'The main library photo, in the saved file (add it in PQP Maker when you use Open in PQP Maker)' : 'None in the library: PQP Maker shows the photo box'}</td></tr>
""", "")
rep("""      const { pr } = pqpData(p);
      try { const ph = await pqpPhoto(p); if (ph) pr.R10 = ph; } catch (e) { /* no photo: PQP Maker shows the photo box */ }""",
    """      const { pr } = pqpData(p);
      if (slot >= 0) { try { const ph = await pqpPhoto(p, slot); if (ph) pr.R10 = ph; } catch (e) { /* no photo: PQP Maker shows the photo box */ } }""")
rep("""  pqpLinkFor(p).then(url => { const a = $('#pqp-open'); if (a) { a.href = url; a.removeAttribute('aria-disabled'); } }).catch(() => {});
  $('#pqp-open').addEventListener('click', e => { if (!e.currentTarget.getAttribute('href')) { e.preventDefault(); return; } toast(`PQP Maker opens in a new tab with ${p.no} ${p.name || ''}`.trim()); setTimeout(closeModal, 50); });
}""", """  const name = `${p.no} ${p.name || ''}`.trim(), file = `<strong>${esc(safeName(p.name || p.no))}.pqp</strong>`;
  const setPhoto = i => {
    slot = i;
    document.querySelectorAll('[data-pqp-ph]').forEach(b => b.setAttribute('aria-pressed', String(+b.dataset.pqpPh === i)));
    $('#pqp-how').innerHTML = slot >= 0
      ? `<strong>Open in PQP Maker</strong> creates the PQP with these details in a new tab and copies the cover photo: PQP Maker then asks you to paste it (Ctrl+V). <strong>Save PQP file</strong> keeps everything, cover photo included, as ${file}: in PQP Maker choose <strong>Open</strong> and pick the file.`
      : `<strong>Open in PQP Maker</strong> creates the PQP with these details in a new tab. <strong>Save PQP file</strong> keeps them as ${file}: in PQP Maker choose <strong>Open</strong> and pick the file.`;
    const a = $('#pqp-open'); a.removeAttribute('href'); a.setAttribute('aria-disabled', 'true');
    pqpLinkFor(p, slot >= 0).then(url => { if (slot !== i) return; const a2 = $('#pqp-open'); if (a2) { a2.href = url; a2.removeAttribute('aria-disabled'); } }).catch(() => {});
    if (slot >= 0) pqpPng(p, slot).catch(() => {});
  };
  setPhoto(slot);
  document.querySelector('.pqp-ph').addEventListener('click', e => { const b = e.target.closest('[data-pqp-ph]'); if (b) setPhoto(+b.dataset.pqpPh); });
  $('#pqp-open').addEventListener('click', e => {
    if (!e.currentTarget.getAttribute('href')) { e.preventDefault(); return; }
    if (slot < 0) { toast(`PQP Maker opens in a new tab with ${name}`); setTimeout(closeModal, 50); return; }
    // copy now, while the click still counts: the clipboard takes the photo as it is ready
    const fail = () => toast(`PQP Maker opens in a new tab with ${name}. The cover photo could not be copied: use Save PQP file, or add the photo in PQP Maker.`, 8000);
    try {
      navigator.clipboard.write([new ClipboardItem({ 'image/png': pqpPng(p, slot) })])
        .then(() => toast(`PQP Maker opens in a new tab with ${name}. The cover photo is copied: paste it there with Ctrl+V.`, 7000), fail);
    } catch (err) { fail(); }
    setTimeout(closeModal, 50);
  });
}""")
rep(".ptile.up{border-style:dashed;background:var(--surface)}",
    ".ptile.up{border-style:dashed;background:var(--surface)}\n.pqp-ph{grid-template-columns:repeat(auto-fill,minmax(104px,1fr))}\n.ptile .pt-cap{position:absolute;left:0;right:0;bottom:0;padding:2px 5px;background:rgba(0,0,0,.58);color:#FFFFFF;font:600 11px/1.3 var(--f-body);text-align:left}")
open(P, 'w').write(s)
print('patched', len(s))
