"""WIR Log and MIR Log: the user's standard workbooks ("07. Project Logs", 16 Nov 2026) prepared as the templates the Library fills.
Nothing of the format changes. Only: the calculation chain is left out (Excel rebuilds it; rows are added to the logs),
the workbook is set to recalculate when opened, and the note of the folder it was last saved in is removed.
Usage: python3 tools/prep_rlog.py <WIR Log - Standard.xlsx> <MIR Log - Standard.xlsx>
Writes build/rlog/wir.xlsx and build/rlog/mir.xlsx."""
import sys, os, re, zipfile
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
        zi = zipfile.ZipInfo(it.filename, date_time=(2026, 11, 16, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = it.external_attr
        zout.writestr(zi, d, compresslevel=9)
    zout.close(); print(out, os.path.getsize(out) // 1024, 'KB')
prep(sys.argv[1], 'wir'); prep(sys.argv[2], 'mir')
