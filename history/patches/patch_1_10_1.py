"""v1.10.1: the PROJECT LIBRARY title in the header is a button back to the library home page (from the presentation,
the MSRA Log page or an open project panel); the MSRA Log still asks first when it has unsaved changes."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('Version 1.10.0 (27 Oct 2026)', 'Version 1.10.1 (27 Oct 2026)')
rep("const APP_VERSION = '1.10.0';", "const APP_VERSION = '1.10.1';")
rep("      <h1>Project Library</h1>", """      <h1><button type="button" class="home-link" id="home-link" title="Go to the project library home page">Project Library</button></h1>""")
rep(".app-title h1{margin:0;font:600 27px/1 var(--f-cond);letter-spacing:.03em;text-transform:uppercase;color:var(--fg)}",
    """.app-title h1{margin:0;font:600 27px/1 var(--f-cond);letter-spacing:.03em;text-transform:uppercase;color:var(--fg)}
.home-link{margin:0;padding:0;border:0;border-radius:2px;background:none;font:inherit;letter-spacing:inherit;text-transform:inherit;color:inherit;cursor:pointer;text-align:left}
.home-link:hover{color:var(--red-text)}""")
rep("""function bindGlobal() {""", """/* the PROJECT LIBRARY title: back to the library list from anywhere */
function goHome() {
  if (SH.open) return;
  if (S.view === 'msra') { closeMsra(); if (S.view !== 'library') return; }   // asks first when the log has unsaved changes
  else if (S.view === 'pres') closePres();
  if (S.detailOpen) { S.detailOpen = false; renderDetail(); }
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
function bindGlobal() {
  $('#home-link').addEventListener('click', goHome);""")
open(P, 'w').write(s)
print('patched', len(s))
