"""v1.9.1: Save PQP file names the file with the project number, name and revision (same as PQP Maker 1.6.2)."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:90]); s = s.replace(old, new)
rep('Version 1.9.0 (27 Oct 2026)', 'Version 1.9.1 (27 Oct 2026)')
rep("const APP_VERSION = '1.9.0';", "const APP_VERSION = '1.9.1';")
rep("const PQP_LEFT = [", """// "DXB-243 - The Borough - Rev 00.pqp": the number the PQP uses (project code, else the project no.), the name and the
// revision (a PQP from the Library starts at Rev 00), as PQP Maker names its project files
const pqpFileName = p => safeName([pqpData(p).pr.P02 || p.no, p.name || 'Untitled project', 'Rev 00'].filter(Boolean).join(' - ')) + '.pqp';
const PQP_LEFT = [""")
rep("      const ok = await saveFile(safeName(p.name || p.no) + '.pqp', new Blob(", "      const ok = await saveFile(pqpFileName(p), new Blob(")
rep("  const name = `${p.no} ${p.name || ''}`.trim(), file = `<strong>${esc(safeName(p.name || p.no))}.pqp</strong>`;",
    "  const name = `${p.no} ${p.name || ''}`.trim(), file = `<strong>${esc(pqpFileName(p))}</strong>`;")
open(P, 'w').write(s)
print('patched', len(s))
