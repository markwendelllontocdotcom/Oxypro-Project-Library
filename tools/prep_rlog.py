"""WIR Log and MIR Log: the user's standard workbooks ("07. Project Logs", 16 Nov 2026) prepared as the templates the Library fills.
Nothing of the format changes. Only: the calculation chain is left out (Excel rebuilds it; rows are added to the logs),
the workbook is set to recalculate when opened, and the note of the folder it was last saved in is removed.
Usage: python3 tools/prep_rlog.py <WIR Log - Standard.xlsx> <MIR Log - Standard.xlsx>
Writes build/rlog/wir.xlsx and build/rlog/mir.xlsx."""
import sys, os, re, zipfile
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ---- MIR Log without Level and Delivery / Storage Location (user, 21 Nov 2026: "remove the column E and F in MIR form as those
# are not applicable in MIR"): columns E and F are taken out of the seven logs and the Transmittal Sheet, and every cell,
# formula, merge, list, colour rule, print area and picture to the right moves two columns left, as Excel does on Delete.
SHIFT = {'MEC', 'PLU', 'ELE', 'ELV', 'FF', 'LPG', 'MEP', 'Transmittal Sheet'}
def c2n(c):
    n = 0
    for ch in c: n = n * 26 + ord(ch) - 64
    return n
def n2c(n):
    s = ''
    while n: n, r = divmod(n - 1, 26); s = chr(65 + r) + s
    return s
def mapcol(c, end=False):
    """a column letter after the deletion; inside the deleted pair a range start goes to the next column and a range end to the one before"""
    n = c2n(c)
    if n in (5, 6): return n2c(4 if end else 5), True
    return n2c(n - 2 if n > 6 else n), False
REF = re.compile(r"(?<![A-Za-z0-9_.$'])(\$?)([A-Z]{1,2})(\$?)(\d+)(?::(\$?)([A-Z]{1,2})(\$?)(\d+))?(?![A-Za-z0-9_(!])|(?<![A-Za-z0-9_.$'])(\$?)([A-Z]{1,2}):(\$?)([A-Z]{1,2})(?![A-Za-z0-9_(!$])")
QUAL = re.compile(r"((?:'[^']+'|[A-Za-z_][A-Za-z0-9_]*)!)")
def shift_refs(text, own, soft=False):
    """moves the references of a formula (or a list of ranges) that point at a sheet that lost the columns"""
    out = []
    for qi, part in enumerate(re.split(r'("(?:[^"]|"")*")', text)):          # not inside quoted text
        if qi % 2: out.append(part); continue
        bits = QUAL.split(part); res = []
        def f(m):
            if m.group(2):
                a, da = mapcol(m.group(2)); t = m.group(1) + a + m.group(3) + m.group(4)
                if m.group(6):
                    b, db = mapcol(m.group(6), True); assert c2n(b) >= c2n(a), text[:200]
                    t += ':' + m.group(5) + b + m.group(7) + m.group(8)
                else: assert soft or not da, ('reference to a removed column', text[:200])
                return t
            a, da = mapcol(m.group(10)); b, db = mapcol(m.group(12), True); assert c2n(b) >= c2n(a), text[:200]
            return m.group(9) + a + ':' + m.group(11) + b
        for bi, bit in enumerate(bits):
            if bi % 2: res.append(bit); continue
            if bi == 0:
                if own: bit = REF.sub(f, bit)
            else:
                # a sheet name covers only the reference right after it; the rest of the text is the formula's own sheet again
                q = bits[bi - 1][:-1].strip("'") in SHIFT; m = REF.match(bit)
                first, rest = (bit[:m.end()], bit[m.end():]) if m else ('', bit)
                if q and first: first = REF.sub(f, first)
                if own: rest = REF.sub(f, rest)
                bit = first + rest
            res.append(bit)
        out.append(''.join(res))
    return ''.join(out)
def drop_cols_sheet(t):
    """a log sheet or the Transmittal Sheet: cells of E and F out, the rest two columns left"""
    def cell(m):
        col, row = m.group(2), m.group(3); n = c2n(col)
        if n in (5, 6): return ''
        return m.group(1) + n2c(n - 2 if n > 6 else n) + row + m.group(4)
    a = t.index('<sheetData>'); b = t.index('</sheetData>')
    body = re.sub(r'(<c r=")([A-Z]+)(\d+)("[^>]*?(?:/>|>.*?</c>))', cell, t[a:b], flags=re.S)
    body = body.replace(' spans="1:14"', ' spans="1:12"')
    body = re.sub(r'(<f[^>]*?) ref="([^"]+)"', lambda m: m.group(1) + ' ref="' + shift_refs(m.group(2), True) + '"', body)
    body = re.sub(r'(<f[^>]*>)([^<]+)(</f>)', lambda m: m.group(1) + shift_refs(m.group(2), True) + m.group(3), body)
    head, tail = t[:a], t[b:]
    head = re.sub(r'<cols>.*?</cols>', '<cols><col min="1" max="1" width="5.7109375" customWidth="1"/><col min="2" max="2" width="12.7109375" customWidth="1"/>'
                  '<col min="3" max="3" width="28.7109375" customWidth="1"/><col min="4" max="4" width="10.7109375" customWidth="1"/><col min="5" max="5" width="70.7109375" customWidth="1"/>'
                  '<col min="6" max="11" width="15.7109375" customWidth="1"/><col min="12" max="12" width="34.28515625" customWidth="1"/><col min="13" max="13" width="13.7109375" customWidth="1"/>'
                  '<col min="14" max="14" width="9.140625" customWidth="1"/><col min="15" max="15" width="68.5703125" hidden="1" customWidth="1" outlineLevel="1" collapsed="1"/>'
                  '<col min="16" max="16" width="9.140625" customWidth="1" collapsed="1"/></cols>', head, flags=re.S)
    fix = lambda m: m.group(1) + ' '.join(shift_refs(x, True) for x in m.group(2).split(' ')) + '"'
    head = re.sub(r'((?:dimension ref|topLeftCell|activeCell|sqref)=")([^"]+)"', lambda m: m.group(1) + ' '.join(shift_refs(x, True, True) for x in m.group(2).split(' ')) + '"', head)
    merges = []
    def merge(m):
        r = shift_refs(m.group(1), True); a1, b1 = (r.split(':') + [None])[:2]
        return '' if b1 is None or a1 == b1 else '<mergeCell ref="%s"/>' % r
    tail = re.sub(r'<mergeCell ref="([^"]+)"/>', merge, tail)
    tail = re.sub(r'<mergeCells count="\d+">', lambda m: '<mergeCells count="%d">' % tail.count('<mergeCell ref='), tail)
    tail = re.sub(r'((?:autoFilter ref|sqref)=")([^"]+)"', fix, tail)
    tail = re.sub(r'(<formula>)([^<]+)(</formula>)', lambda m: m.group(1) + shift_refs(m.group(2), True) + m.group(3), tail)
    return head + body + tail
def drop_cols(name, d):
    if re.fullmatch(r'xl/worksheets/sheet[2-9]\.xml', name): return drop_cols_sheet(d.decode()).encode()
    if name in ('xl/worksheets/sheet1.xml', 'xl/worksheets/sheet11.xml'):                # Summary and the helper sheet: their formulas point at the logs
        return re.sub(r'(<f[^>]*>)([^<]+)(</f>)', lambda m: m.group(1) + shift_refs(m.group(2), False) + m.group(3), d.decode()).encode()
    if name == 'xl/workbook.xml':
        return re.sub(r'(<definedName [^>]*>)([^<]+)(</definedName>)', lambda m: m.group(1) + shift_refs(m.group(2), False) + m.group(3), d.decode()).encode()
    if re.fullmatch(r'xl/drawings/drawing[2-9]\.xml', name):
        return re.sub(r'<xdr:col>(\d+)</xdr:col>', lambda m: '<xdr:col>%d</xdr:col>' % (int(m.group(1)) - 2 if int(m.group(1)) >= 6 else int(m.group(1))), d.decode()).encode()
    return d
def prep(src, kind):
    zin = zipfile.ZipFile(src); out = os.path.join(here, 'build', 'rlog', kind + '.xlsx')
    zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9)
    for it in zin.infolist():
        if it.filename == 'xl/calcChain.xml': continue
        d = zin.read(it.filename)
        if it.filename == '[Content_Types].xml':
            t = d.decode(); n = len(t); t = re.sub(r'<Override PartName="/xl/calcChain.xml"[^>]*/>', '', t); assert len(t) < n; d = t.encode()
        if it.filename == 'xl/_rels/workbook.xml.rels':
            t = d.decode(); n = len(t); t = re.sub(r'<Relationship [^>]*calcChain[^>]*/>', '', t); assert len(t) < n; d = t.encode()
        if it.filename == 'xl/workbook.xml':
            t = d.decode()
            t, a = re.subn(r'<mc:AlternateContent[^>]*>.*?</mc:AlternateContent>', '', t, flags=re.S); assert a == 1
            t, b = re.subn(r'<calcPr calcId="(\d+)"/>', r'<calcPr calcId="\1" fullCalcOnLoad="1"/>', t); assert b == 1
            d = t.encode()
        if kind == 'mir': d = drop_cols(it.filename, d)
        zi = zipfile.ZipInfo(it.filename, date_time=(2026, 11, 16, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = it.external_attr
        zout.writestr(zi, d, compresslevel=9)
    zout.close(); print(out, os.path.getsize(out) // 1024, 'KB')
prep(sys.argv[1], 'wir'); prep(sys.argv[2], 'mir')
