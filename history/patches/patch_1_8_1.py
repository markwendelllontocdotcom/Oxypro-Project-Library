"""v1.8.1: one PQP entry in the detail panel: "PQP details and file" (its dialog holds Open in PQP Maker and Save PQP file)."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:90]); s = s.replace(old, new)
rep('Version 1.8.0 (27 Oct 2026)', 'Version 1.8.1 (27 Oct 2026)')
rep("const APP_VERSION = '1.8.0';", "const APP_VERSION = '1.8.1';")
rep("""        ${pqpSendHTML(p)}
        <button type="button" class="btn btn-ghost btn-sm" data-act="pqp">PQP details and file</button>""",
    """        <button type="button" class="btn" data-act="pqp" title="Open the PQP in PQP Maker, or save it as a PQP file">PQP details and file</button>""")
rep("""  $('#pqp-open').addEventListener('click', e => { if (!e.currentTarget.getAttribute('href')) e.preventDefault(); else setTimeout(closeModal, 50); });""",
    """  $('#pqp-open').addEventListener('click', e => { if (!e.currentTarget.getAttribute('href')) { e.preventDefault(); return; } toast(`PQP Maker opens in a new tab with ${p.no} ${p.name || ''}`.trim()); setTimeout(closeModal, 50); });""")
open(P, 'w').write(s)
print('patched', len(s))
