"""v1.9.2: Save PQP file ends in .pqp.json: claude.ai saves only allowlisted types (json yes, pqp no); PQP Maker opens .json."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:90]); s = s.replace(old, new)
rep('Version 1.9.1 (27 Oct 2026)', 'Version 1.9.2 (27 Oct 2026)')
rep("const APP_VERSION = '1.9.1';", "const APP_VERSION = '1.9.2';")
rep("const pqpFileName = p => safeName([pqpData(p).pr.P02 || p.no, p.name || 'Untitled project', 'Rev 00'].filter(Boolean).join(' - ')) + '.pqp';",
    "// claude.ai saves only allowlisted file types: json is one, pqp is not. A .pqp file is JSON and PQP Maker's Open takes .json too.\nconst pqpFileName = p => safeName([pqpData(p).pr.P02 || p.no, p.name || 'Untitled project', 'Rev 00'].filter(Boolean).join(' - ')) + '.pqp.json';")
open(P, 'w').write(s)
print('patched', len(s))
