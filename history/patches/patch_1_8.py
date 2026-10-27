"""v1.8.0: Send to PQP Maker opens PQP Maker with the PQP already created (no file to save and open).

claude.ai runs the page in a sandboxed frame without pop-ups; links are opened for the page by claude.ai itself,
and the desktop app hands them to the system browser. So Send to PQP Maker is a real link, and the link stays short
(text details only, about 1 KB): the cover photo travels only in the saved .pqp file.
"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('Version 1.7.0 (27 Oct 2026)', 'Version 1.8.0 (27 Oct 2026)')
rep("const APP_VERSION = '1.7.0';", "const APP_VERSION = '1.8.0';")

# codes go across only when the Library has them, so updating a PQP never clears codes typed there
rep("""  const co = pqpList(p.codes, PQP_CODES);
  if (!co.list.includes('Project Specifications')) co.list.unshift('Project Specifications');   // ticked in every new PQP
  put('Q07',""", """  const co = pqpList(p.codes, PQP_CODES);
  if (co.list.length) {
  if (!co.list.includes('Project Specifications')) co.list.unshift('Project Specifications');   // ticked in every new PQP
  put('Q07',""")
rep("""  if (co.other.length) pr.Q07other = co.other.join(', ');
  return { pr, rows,""", """  if (co.other.length) pr.Q07other = co.other.join(', ');
  }
  return { pr, rows,""")

LINK = r"""
// The project travels to PQP Maker in the address after # (never sent to a server): the .pqp JSON, deflate-raw, base64url
const b64u = u => { let t = ''; for (let i = 0; i < u.length; i += 0x8000) t += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(t).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); };
async function pqpLink(p) {
  const { pr } = pqpData(p);
  const raw = new TextEncoder().encode(JSON.stringify({ format: 'pqp-maker-project', version: 1, app: 'Oxypro Project Library ' + APP_VERSION, source: { library: p.no }, project: pr }));
  if (window.CompressionStream) {
    try {
      const z = new Uint8Array(await new Response(new Blob([raw]).stream().pipeThrough(new CompressionStream('deflate-raw'))).arrayBuffer());
      return PQP_URL + '#library=' + b64u(z);
    } catch (e) { /* plain JSON below */ }
  }
  return PQP_URL + '#library-json=' + b64u(raw);
}
const pqpKey = p => p.no + '|' + (p.updatedAt || '');
const PQP_READY = new Map();   // key -> link, filled as soon as a project is shown
function pqpLinkFor(p) {
  const key = pqpKey(p);
  if (PQP_READY.has(key)) return Promise.resolve(PQP_READY.get(key));
  return pqpLink(p).then(url => { if (PQP_READY.size > 50) PQP_READY.clear(); PQP_READY.set(key, url); return url; });
}
// the Send to PQP Maker link gets its address once it is ready (a link without an address is not opened)
function preparePqp(p) {
  pqpLinkFor(p).then(url => {
    const a = $('#pqp-send');
    if (a && a.dataset.no === p.no) { a.href = url; a.removeAttribute('aria-disabled'); }
  }).catch(() => {});
}
function pqpSendHTML(p) {
  const url = PQP_READY.get(pqpKey(p));
  return `<a class="btn" id="pqp-send" data-no="${esc(p.no)}" target="_blank" rel="noopener"${url ? ` href="${esc(url)}"` : ' aria-disabled="true"'} title="Opens PQP Maker in a new tab with this project's PQP created">Send to PQP Maker</a>`;
}
function onPqpSend(e, a) {
  const p = S.projects.get(a.dataset.no); if (!p) { e.preventDefault(); return; }
  if (!a.getAttribute('href')) { e.preventDefault(); toast('One moment: the project is being prepared. Click Send to PQP Maker again.'); preparePqp(p); return; }
  toast(`PQP Maker opens in a new tab with ${p.no} ${p.name || ''}`.trim());
}
document.addEventListener('click', e => { const a = e.target.closest && e.target.closest('#pqp-send'); if (a) onPqpSend(e, a); });
"""
rep("const PQP_LEFT = [", LINK.strip('\n') + "\nconst PQP_LEFT = [")

# the dialog: what goes across, the same link, and the file (which also carries the cover photo)
rep("""function openPqp(no) {
  const p = S.projects.get(no); if (!p) return;""", """function openPqp(no) {
  const p = S.projects.get(no); if (!p) return;""")
rep("""      <p style="margin:0">Saves <strong>${esc(safeName(p.name || p.no))}.pqp</strong>. In PQP Maker choose <strong>Open</strong> and pick the file: these details are filled in for you.</p>""",
    """      <p style="margin:0"><strong>Open in PQP Maker</strong> creates the PQP with these details in a new tab. <strong>Save PQP file</strong> keeps them, with the cover photo, as <strong>${esc(safeName(p.name || p.no))}.pqp</strong>: in PQP Maker choose <strong>Open</strong> and pick the file.</p>""")
rep("""        <tr><td>Cover Photo</td><td>${hasPhoto ? 'The main library photo' : 'None in the library: PQP Maker shows the photo box'}</td></tr>""",
    """        <tr><td>Cover Photo</td><td>${hasPhoto ? 'The main library photo, in the saved file (add it in PQP Maker when you use Open in PQP Maker)' : 'None in the library: PQP Maker shows the photo box'}</td></tr>""")
rep("""    <div class="dialog-foot"><a class="btn" href="${PQP_URL}" target="_blank" rel="noopener">Open PQP Maker</a><button type="button" class="btn btn-primary" id="pqp-go">Save PQP file</button></div>""",
    """    <div class="dialog-foot"><button type="button" class="btn" id="pqp-go">Save PQP file</button><a class="btn btn-primary" id="pqp-open" target="_blank" rel="noopener" aria-disabled="true">Open in PQP Maker</a></div>""")
rep("""      if (ok) closeModal(); else { btn.disabled = false; btn.textContent = 'Save PQP file'; }
    } catch (e) { const er = $('#pqp-err'); er.textContent = 'The file could not be made: ' + ((e && e.message) || e); er.hidden = false; btn.disabled = false; btn.textContent = 'Save PQP file'; }
  });
}""", """      if (ok) closeModal(); else { btn.disabled = false; btn.textContent = 'Save PQP file'; }
    } catch (e) { const er = $('#pqp-err'); er.textContent = 'The file could not be made: ' + ((e && e.message) || e); er.hidden = false; btn.disabled = false; btn.textContent = 'Save PQP file'; }
  });
  pqpLinkFor(p).then(url => { const a = $('#pqp-open'); if (a) { a.href = url; a.removeAttribute('aria-disabled'); } }).catch(() => {});
  $('#pqp-open').addEventListener('click', e => { if (!e.currentTarget.getAttribute('href')) e.preventDefault(); else setTimeout(closeModal, 50); });
}""")
rep("""        <button type="button" class="btn" data-act="pqp" title="Save a PQP Maker project file filled with this project's details">Send to PQP Maker</button>""",
    """        ${pqpSendHTML(p)}
        <button type="button" class="btn btn-ghost btn-sm" data-act="pqp">PQP details and file</button>""")
rep("""      ${w ? `<div class="d-section">${del || '<div><button type="button" class="btn btn-sm btn-ghost btn-danger" data-act="del">Delete project</button></div>'}</div>` : ''}
    </div>`;
}""", """      ${w ? `<div class="d-section">${del || '<div><button type="button" class="btn btn-sm btn-ghost btn-danger" data-act="del">Delete project</button></div>'}</div>` : ''}
    </div>`;
  if (!PQP_READY.has(pqpKey(p))) preparePqp(p);
}""")
rep(".d-actions{display:flex;flex-wrap:wrap;gap:8px}", ".d-actions{display:flex;flex-wrap:wrap;align-items:center;gap:8px}\na.btn[aria-disabled]{opacity:.6;cursor:progress}")
open(P, 'w').write(s)
print('patched', len(s))
