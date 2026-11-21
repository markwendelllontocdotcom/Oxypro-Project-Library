/* ---------- WIR Log and MIR Log: the Excel file ----------
   The file is the user's standard workbook itself, filled in: every sheet, style, formula, drop-down list, print setting and
   hidden sheet (Instructions, the Transmittal Sheet's helper sheet, MS Master List) stays as in the standard. Filled in are the
   project bar and block, the three party logos, and the rows of the seven discipline logs. */
const RL_LIBS = { jszip: 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js' };
const rlXml = s => String(s == null ? '' : s).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F￾￿]/g, '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const rlInline = (ref, s, text) => text === '' || text == null ? `<c r="${ref}" s="${s}"/>` : `<c r="${ref}" s="${s}" t="inlineStr"><is><t xml:space="preserve">${rlXml(text)}</t></is></c>`;
const rlSerial = iso => { const d = msDay(iso); return d == null ? null : d + 25569; };   // Excel's day number
// the height of a log row: 30 points as in the standard, more when the description or the remark needs more lines
function rlRowHeight(it) {
  const lines = (t, per) => String(t || '').split('\n').reduce((a, l) => a + Math.max(1, Math.ceil(l.length / per)), 0);
  const n = Math.max(lines(it.desc, 78), lines(it.rem, 36), lines(it.loc, 20), lines(it.ref, 21));
  return n <= 2 ? 30 : n * 15;
}
// st: the standard's own cell formats of a log row, read from its row 12 (they differ between the WIR and the MIR workbook)
function rlRowXml(r, sn, code, it, st) {
  const c = [];
  c.push(`<c r="A${r}" s="${st.A}"><v>${sn}</v></c>`, rlInline('B' + r, st.B, code));
  const num = (col, v) => v == null ? `<c r="${col}${r}" s="${st[col]}"/>` : `<c r="${col}${r}" s="${st[col]}"><v>${v}</v></c>`;
  const txt = (col, v) => rlInline(col + r, st[col], v);
  if (it) {
    c.push(txt('C', it.ref));
    c.push(/^\d{1,6}$/.test(it.rev.trim()) ? num('D', +it.rev.trim()) : txt('D', it.rev.trim()));
    c.push(txt('E', it.lvl), txt('F', it.loc), txt('G', it.desc));
    c.push(num('H', rlSerial(it.plan)), num('I', rlSerial(it.sub)), num('J', rlSerial(it.ret)));
  } else 'CDEFGHIJ'.split('').forEach(col => c.push(num(col, null)));
  const rv = it ? msReview(it) : '', f = `IF(OR($I${r}="",$J${r}=""),"",$J${r}-$I${r})`;
  c.push(rv === '' ? `<c r="K${r}" s="${st.K}" t="str"><f>${f}</f><v></v></c>` : `<c r="K${r}" s="${st.K}"><f>${f}</f><v>${rv}</v></c>`);
  c.push(txt('L', it ? it.st : ''), txt('M', it ? it.fin : ''), txt('N', it ? it.rem : ''));
  return `<row r="${r}" spans="1:14" ht="${it ? rlRowHeight(it) : 30}" customHeight="1">${c.join('')}</row>`;
}
// Excel's column width (characters) in pixels at 100 %, and the standard's widths of G to K and row height of rows 3 to 5
const RL_PX = { G: msXPx(70.7109375), H: msXPx(15.7109375), row: 20.1 * 4 / 3 };
// where a logo goes: centred in its box of rows 3 to 5 (Client the left half of G, Consultant the right half, Main Contractor H:I)
function rlLogoAnchor(role, w, h) {
  const box = role === 'client' ? { col: 6, x0: 0, bw: RL_PX.G / 2 } : role === 'consultant' ? { col: 6, x0: RL_PX.G / 2, bw: RL_PX.G / 2 } : { col: 7, x0: 0, bw: RL_PX.H * 2 };
  const bh = RL_PX.row * 3, pad = 8, k = Math.min(1, (box.bw - 2 * pad) / w, (bh - 2 * pad) / h), W = w * k, H = h * k;
  let x = box.x0 + (box.bw - W) / 2, y = (bh - H) / 2, col = box.col, row = 2;
  if (col === 7 && x >= RL_PX.H) { x -= RL_PX.H; col = 8; }
  while (row < 4 && y >= RL_PX.row) { y -= RL_PX.row; row++; }
  const e = v => Math.round(v * 9525);
  return { from: `<xdr:from><xdr:col>${col}</xdr:col><xdr:colOff>${e(x)}</xdr:colOff><xdr:row>${row}</xdr:row><xdr:rowOff>${e(y)}</xdr:rowOff></xdr:from>`, cx: e(W), cy: e(H) };
}
const RL_IMG_ROLE = { 'image2.png': 'contractor', 'image3.png': 'client', 'image4.png': 'consultant' };   // image1.png is Oxypro's own logo
/* model: { kind, title, block: {client, consultant, mepConsultant, mainContractor, mepContractor}, sheets: {MEC: [items], ...},
            logos: {client, consultant, contractor: {b64, w, h} | null} } -> the workbook as a Uint8Array */
async function rlFillTemplate(JSZip, tplB64, model) {
  const zip = await JSZip.loadAsync(tplB64, { base64: true });
  const read = n => zip.file(n).async('string'), once = (t, a, b, what) => { const i = t.indexOf(a); if (i < 0 || t.indexOf(a, i + a.length) >= 0) throw new Error('The standard file is not as expected (' + what + ').'); return t.slice(0, i) + b + t.slice(i + a.length); };
  // the project: one shared text for the bar of every sheet, one for the Summary
  let ss = await read('xl/sharedStrings.xml');
  ss = once(ss, '<si><t>PROJECT NAME HERE</t></si>', `<si><t xml:space="preserve">${rlXml(model.title)}</t></si>`, 'project name');
  ss = once(ss, '<si><t xml:space="preserve">PROJECT : </t></si>', `<si><t xml:space="preserve">PROJECT : ${rlXml(model.title)}</t></si>`, 'summary project');
  zip.file('xl/sharedStrings.xml', ss);
  let wbx = await read('xl/workbook.xml');
  // Excel works every formula out again when it opens the file; the values written here are for viewers that do not
  const setV = (t, ref, v) => t.replace(new RegExp(`(<c r="${ref}"[^>]*>(?:<f[^>]*>[^<]*</f>|<f[^>]*/>))<v>[^<]*</v>`), `$1<v>${v}</v>`);
  const today = msToday() + 25569, sum = [];
  const vals = RL_BLOCK.map(([k]) => ': ' + (model.block[k] || ''));
  for (let i = 0; i < 8; i++) {                      // sheet2..sheet8 the logs, sheet9 the Transmittal Sheet
    const name = `xl/worksheets/sheet${i + 2}.xml`; let t = await read(name);
    const cut = t.indexOf('<row r="9"'); if (cut < 0) throw new Error('The standard file is not as expected (sheet head).');
    let head = t.slice(0, cut);
    vals.forEach((v, j) => { const r = j + 2; head = head.replace(new RegExp(`<c r="C${r}" s="(\\d+)" t="s"><v>\\d+</v></c>`), (m, s) => rlInline('C' + r, s, v)); });
    t = head + t.slice(cut);
    if (i < 7) {
      const code = RL_CODES[i], items = model.sheets[code] || [], n = Math.max(RL_TPL_ROWS, items.length), last = 11 + n;
      const a = t.indexOf('<row r="12"'), b = t.indexOf('</sheetData>'); if (a < 0 || b < a) throw new Error('The standard file is not as expected (log rows).');
      const st = {}; t.slice(a, t.indexOf('</row>', a)).replace(/<c r="([A-N])12" s="(\d+)"/g, (m, col, sid) => { st[col] = sid; return m; });
      if (Object.keys(st).length !== 14) throw new Error('The standard file is not as expected (log row formats).');
      const rows = []; for (let k = 0; k < n; k++) rows.push(rlRowXml(12 + k, k + 1, code, items[k] || null, st));
      t = t.slice(0, a) + rows.join('') + t.slice(b);
      t = t.replace(/<dimension ref="A1:R\d+"\/>/, `<dimension ref="A1:R${last}"/>`);
      // the lists and colours of the standard reach at least to the last row
      t = t.replace(/sqref="(H12:H|L12:M)(\d+)"/g, (m, p, e) => `sqref="${p}${Math.max(+e, last)}"`);
      const cn = rlCounts(items), row = [cn.A, cn.B, cn.C, cn.D, cn.E, cn.UR, cn.sub]; sum.push(row);
      'HIJKLMN'.split('').forEach((col, k) => { t = setV(t, col + '10', row[k]); });
      const used = 11 + items.length;
      wbx = wbx.replace(new RegExp(`(<definedName name="_xlnm\\.Print_Area" localSheetId="${i + 1}">${code}!\\$A\\$1:\\$N\\$)(\\d+)`), (m, p, e) => p + Math.max(+e, used));
    }
    t = setV(t, 'B10', today);
    zip.file(name, t);
  }
  {                                                  // the Summary: one row per log, then the totals
    let t = setV(await read('xl/worksheets/sheet1.xml'), 'B3', today);
    const tot = [0, 0, 0, 0, 0, 0, 0, 0];
    sum.forEach((r, i) => { const v = [r[6], r[0], r[1], r[2], r[3], r[4], r[5], r[2] + r[3]]; 'CDEFGHIJ'.split('').forEach((col, k) => { t = setV(t, col + (6 + i), v[k]); tot[k] += v[k]; }); });
    'CDEFGHIJ'.split('').forEach((col, k) => { t = setV(t, col + '13', tot[k]); });
    zip.file('xl/worksheets/sheet1.xml', t);
  }
  zip.file('xl/workbook.xml', wbx);
  // the party logos: the standard's three pictures replaced by the project's (left out when the library has none)
  const L = model.logos || {};
  for (const [img, role] of Object.entries(RL_IMG_ROLE)) if (L[role]) zip.file('xl/media/' + img, L[role].b64, { base64: true });
  for (let i = 2; i <= 9; i++) {
    const rels = await read(`xl/drawings/_rels/drawing${i}.xml.rels`), map = {};
    rels.replace(/<Relationship [^>]*>/g, m => { const id = (m.match(/Id="([^"]+)"/) || [])[1], tg = (m.match(/Target="[^"]*\/([^"/]+)"/) || [])[1]; if (id && tg) map[id] = tg; return m; });
    let d = await read(`xl/drawings/drawing${i}.xml`);
    d = d.replace(/<xdr:oneCellAnchor>[\s\S]*?<\/xdr:oneCellAnchor>/g, an => {
      const role = RL_IMG_ROLE[map[(an.match(/r:embed="([^"]+)"/) || [])[1]]]; if (!role) return an;
      const lg = L[role]; if (!lg) return '';
      const p = rlLogoAnchor(role, lg.w, lg.h);
      return an.replace(/<xdr:from>[\s\S]*?<\/xdr:from><xdr:ext cx="\d+" cy="\d+"\/>/, `${p.from}<xdr:ext cx="${p.cx}" cy="${p.cy}"/>`).replace(/<a:xfrm>[\s\S]*?<\/a:xfrm>/, `<a:xfrm><a:off x="0" y="0"/><a:ext cx="${p.cx}" cy="${p.cy}"/></a:xfrm>`);
    });
    zip.file(`xl/drawings/drawing${i}.xml`, d);
  }
  return zip.generateAsync({ type: 'uint8array', compression: 'DEFLATE', compressionOptions: { level: 6 }, mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
}
