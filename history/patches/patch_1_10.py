"""v1.10.0: Create MSRA Log next to PQP details and file. A full page per project to create, edit, view, save as (Excel / PDF)
and print the Method Statement Log in the Oxypro template (The Borough), in Open Sans. Logs are kept in the db collection
mslogs (doc id = project no) with a small index in mslogmeta. The MSRA code lives in src/msra/ and is inlined by build.py."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('Version 1.9.2 (27 Oct 2026)', 'Version 1.10.0 (27 Oct 2026)')
rep("const APP_VERSION = '1.9.2';", "const APP_VERSION = '1.10.0';")
# styles, page, file input
rep("\n</style>\n\n<header class=\"top\">", "\n/*__MSRA_CSS__*/\n</style>\n\n<header class=\"top\">")
rep("""<footer class="foot">""", """<section id="view-msra" hidden aria-label="MSRA Log">
  <div class="band-in">
    <div class="ms-bar">
      <button type="button" class="btn btn-ghost" data-ms-act="back"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>Library</button>
      <div class="ms-title"><h2>MSRA Log</h2><span id="ms-proj"></span></div>
      <div class="ms-actions" id="ms-actions"></div>
    </div>
    <div id="ms-body"></div>
  </div>
</section>

<footer class="foot">""")
rep("""<input type="file" id="file-xlsx" accept=".xlsx,.xls,.csv" hidden>""", """<input type="file" id="file-xlsx" accept=".xlsx,.xls,.csv" hidden>
<input type="file" id="file-msl" accept=".xlsx,.xlsm,.xls" hidden>""")
# state, button, action
rep("  delConfirm: null, pmConfirm: null, busy: null, fileTarget: null, imp: null\n};", "  delConfirm: null, pmConfirm: null, busy: null, fileTarget: null, imp: null, msMeta: new Map()\n};")
rep("""        <button type="button" class="btn" data-act="pqp" title="Open the PQP in PQP Maker, or save it as a PQP file">PQP details and file</button>
      </div>""", """        <button type="button" class="btn" data-act="pqp" title="Open the PQP in PQP Maker, or save it as a PQP file">PQP details and file</button>
        ${msButtonHTML(p)}
      </div>""")
rep("""    case 'pqp': if (p) openPqp(p.no); return;""", """    case 'pqp': if (p) openPqp(p.no); return;
    case 'msra': if (p) openMsra(p.no); return;""")
# code, boot
rep("/* ---------- boot ---------- */", "/*__MSRA_JS__*/\n\n/* ---------- boot ---------- */")
rep("  bindLibrary(); bindPres(); bindShow(); bindGlobal(); bindView(); renderAll();", "  bindLibrary(); bindPres(); bindShow(); bindGlobal(); bindView(); bindMsra(); renderAll();")
rep("""  DB.doc('settings/columns').onSnapshot(snap => {""", """  DB.collection('mslogmeta').onSnapshot(snap => {
    const m = new Map(); snap.docs.forEach(d => { if (d.exists) m.set(d.id, d.data()); });
    S.msMeta = m; if (S.view === 'library') renderDetail();
  }, () => {});
  DB.doc('settings/columns').onSnapshot(snap => {""")
open(P, 'w').write(s)
print('patched', len(s))
