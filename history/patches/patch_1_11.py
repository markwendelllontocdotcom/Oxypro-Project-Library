"""v1.11.0: GitHub edition. The same page can run outside Claude as a static website: build.py makes site/ with a
local runtime (window.claude from runtime.js): the projects and photos are a snapshot (read-only), files download
normally, MSRA Logs are saved in the browser and Print opens the PDF for printing. The Claude edition is unchanged
apart from the version."""
import os
H = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(H, 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('Version 1.10.2 (27 Oct 2026)', 'Version 1.11.0 (27 Oct 2026)')
rep("const APP_VERSION = '1.10.2';", """const APP_VERSION = '1.11.0';
/* which edition runs: Claude (shared database) or the GitHub edition (static website, see runtime.js) */
const GH = window.__OPL_EDITION === 'github';
const SNAP_DATE = String(window.__OPL_SNAPSHOT || '');
const CLAUDE_URL = 'https://claude.ai/artifact/T3U712ufURSuMQTfsGDkMy';""")
rep("const blobUrl = id => '/_blob/' + encodeURIComponent(id);", "const blobUrl = id => GH ? 'photos/' + encodeURIComponent(id) + '.jpg' : '/_blob/' + encodeURIComponent(id);")
rep("""<div class="tagline"><div class="band-in tagline-in">The complete solution for building services</div></div>""",
    """<div class="tagline"><div class="band-in tagline-in">The complete solution for building services</div></div>
<div class="edition" id="edition" hidden><div class="band-in edition-in"></div></div>""")
rep(""".tagline-in{font:600 13px/1.25 var(--f-cond);letter-spacing:.16em;text-transform:uppercase;padding-block:7px}""",
    """.tagline-in{font:600 13px/1.25 var(--f-cond);letter-spacing:.16em;text-transform:uppercase;padding-block:7px}
.edition{background:var(--info-soft);color:var(--fg-2);border-bottom:1px solid var(--line)}
.edition-in{display:flex;flex-wrap:wrap;align-items:center;gap:4px 14px;padding-block:8px;font-size:13.5px}
.edition-in b{color:var(--info)}
.edition-in a{color:var(--info);font-weight:600}""")
# About: the edition line and the data bullets
rep("""<div class="about-ver">Version ${APP_VERSION} · 27 Oct 2026${n ? ` · ${n} projects` : ''}</div>""",
    """<div class="about-ver">Version ${APP_VERSION} · 27 Oct 2026${GH ? ` · GitHub edition, projects as of ${esc(SNAP_DATE)}` : ''}${n ? ` · ${n} projects` : ''}</div>""")
rep("""          <li>Projects, photos and MSRA Logs are kept in this shared library in Claude. Everyone with the link sees the same, up-to-date list.</li>
          <li>Only the library's owner and editors can add or change projects, photos and MSRA Logs${w ? ' (you can)' : ' (you can view, make presentations and download files)'}.</li>
          <li>Files you make (PDF, PowerPoint, Excel, PQP files) are downloaded to your device. Printing is done from the downloaded PDF, as Claude cannot open the print window.</li>""",
    """${GH ? `<li>This is the GitHub edition: the projects and photos are a copy of the library as of ${esc(SNAP_DATE)} and cannot be changed here. The live library, where editors add and change projects, is <a href="${CLAUDE_URL}" target="_blank" rel="noopener">in Claude</a>.</li>
          <li>MSRA Logs you save here stay in this browser on this device only. Use Save as to keep them as Excel or PDF files, or to pass them on.</li>
          <li>Files you make (PDF, PowerPoint, Excel, PQP files) are downloaded to your device; Print opens the PDF for printing.</li>` : `<li>Projects, photos and MSRA Logs are kept in this shared library in Claude. Everyone with the link sees the same, up-to-date list.</li>
          <li>Only the library's owner and editors can add or change projects, photos and MSRA Logs${w ? ' (you can)' : ' (you can view, make presentations and download files)'}.</li>
          <li>Files you make (PDF, PowerPoint, Excel, PQP files) are downloaded to your device. Printing is done from the downloaded PDF, as Claude cannot open the print window.</li>`}""")
rep("""  ['1.10.2', '27 Oct 2026', 'This About page (About in the header and in the footer).'],""",
    """  ['1.11.0', '27 Oct 2026', 'GitHub edition: the library as a website outside Claude, with a copy of the projects and photos; MSRA Logs are saved in the browser.'],
  ['1.10.2', '27 Oct 2026', 'This About page (About in the header and in the footer).'],""")
# boot: show the edition bar and footer note
rep("""async function boot() {
  applyView(lsGet('viewTheme') || 'auto');""", """async function boot() {
  applyView(lsGet('viewTheme') || 'auto');
  if (GH) {
    const e = $('#edition'); e.hidden = false;
    e.firstElementChild.innerHTML = `<span><b>GitHub edition</b> · projects and photos as of ${esc(SNAP_DATE)} · read-only; MSRA Logs are saved in this browser</span><a href="${CLAUDE_URL}" target="_blank" rel="noopener">Open the live library in Claude</a>`;
    $('#version').textContent += ' · GitHub edition';
  }""")
open(P, 'w').write(s)

# MSRA Log: saving in the GitHub edition goes to this browser
U = os.path.join(H, 'src', 'msra', 'ui.js')
u = open(U).read()
def repu(old, new, count=1):
    global u
    n = u.count(old)
    assert n == count, (n, old[:90])
    u = u.replace(old, new)
repu("""const msProj = () =>""", """// who may save: editors in Claude; anyone in the GitHub edition (saved in their browser)
const msCanSave = () => GH || canWrite();
const MS_WHERE = GH ? 'this browser' : 'the library';
const msProj = () =>""")
repu("""function msAskLeave() {
  const w = canWrite();""", """function msAskLeave() {
  const w = msCanSave();""")
repu("""'Save the changes to this MSRA Log before going back to the library?'""", """`Save the changes to this MSRA Log in ${MS_WHERE} before going back to the library?`""")
repu("""  const w = canWrite(), e = MSV.mode === 'edit';
  el.innerHTML = `<div class="seg\"""", """  const w = msCanSave(), e = MSV.mode === 'edit';
  el.innerHTML = `<div class="seg\"""")
repu("""MSV.dirty ? 'Save to library' : 'Saved'}""", """MSV.dirty ? (GH ? 'Save in browser' : 'Save to library') : 'Saved'}""")
repu("""  if (!canWrite() && MSV.dirty) return""", """  if (!msCanSave() && MSV.dirty) return""")
repu("""  const p = msProj(), w = canWrite();
  const card =""", """  const p = msProj(), w = msCanSave();
  const card =""")
repu("""    ${w ? '' : '<p class="hint">Only the library\\'s editors can save the log to the library. You can still make it and download it with Save as.</p>'}""",
     """    ${GH ? '<p class="hint">GitHub edition: the log is saved in this browser on this device. Use Save as for Excel or PDF files to keep or share.</p>' : w ? '' : '<p class="hint">Only the library\\'s editors can save the log to the library. You can still make it and download it with Save as.</p>'}""")
repu("""  const log = MSV.log, w = canWrite();
  const block = (st) =>""", """  const log = MSV.log, w = msCanSave();
  const block = (st) =>""")
repu("""${log.updatedAt ? `Saved in the library ${esc(""", """${log.updatedAt ? `Saved in ${MS_WHERE} ${esc(""")
repu("""'Not saved in the library yet.'""", """`Not saved in ${MS_WHERE} yet.`""")
repu("""Delete the MSRA Log of ${esc(msName())} from the library?""", """Delete the MSRA Log of ${esc(msName())} from ${MS_WHERE}?""")
repu("""  toast(how === 'empty' ? 'Empty log started. Add method statements, then Save to library.' : `Log started with ${MSV.log.items.length} method statements. Save to library to keep it.`, 5000);""",
     """  const sv = GH ? 'Save in browser' : 'Save to library';
  toast(how === 'empty' ? `Empty log started. Add method statements, then ${sv}.` : `Log started with ${MSV.log.items.length} method statements. ${sv} to keep it.`, 5000);""")
repu("""  if (!canWrite() || !MSV.log || MSV.busy) return false;""", """  if (!msCanSave() || !MSV.log || MSV.busy) return false;""")
repu("""    toast('MSRA Log saved to the library');""", """    toast(`MSRA Log saved in ${MS_WHERE}`);""")
repu("""async function msDelete() {
  if (!canWrite()) return;""", """async function msDelete() {
  if (!msCanSave()) return;""")
repu("""if (MSV.dirty && canWrite()) msSave();""", """if (MSV.dirty && msCanSave()) msSave();""")
repu("""toast(`The MSRA Log of ${msName()} was deleted`);""", """toast(`The MSRA Log of ${msName()} was deleted from ${MS_WHERE}`);""")
open(U, 'w').write(u)

# Print in the GitHub edition: open the PDF to print it
D = os.path.join(H, 'src', 'msra', 'pdf.js')
d = open(D).read()
old = """  const ok = await saveFile(msFileBase() + (print ? ' - Print' : '') + '.pdf', doc.output('blob'));
  if (ok && print) toast('Open the PDF and print it: A4 landscape, actual size.', 7000);"""
assert d.count(old) == 1
d = d.replace(old, """  const blob = doc.output('blob');
  if (print && GH) {   // a normal website may open the PDF in a new tab, where the browser prints it
    const url = URL.createObjectURL(blob), w = window.open(url, '_blank');
    setTimeout(() => URL.revokeObjectURL(url), 600000);
    if (w) { toast('The PDF opened in a new tab: print it from there (A4 landscape, actual size).', 7000); return; }
  }
  const ok = await saveFile(msFileBase() + (print ? ' - Print' : '') + '.pdf', blob);
  if (ok && print) toast('Open the PDF and print it: A4 landscape, actual size.', 7000);""")
open(D, 'w').write(d)
print('patched', len(s), len(u), len(d))
