/* ---------- MSRA Log: PDF for printing (jsPDF + AutoTable), A4 landscape ---------- */
const MS_RGB = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
const MS_PG = { w: 841.89, h: 595.28, l: 20, r: 20, t: 22, b: 26 };
function msPdfFit(doc, text, maxW, size, min, bold) {
  doc.setFont('Carlito', bold ? 'bold' : 'normal');
  let s = size; doc.setFontSize(s);
  while (s > min && doc.getTextWidth(text) > maxW) { s -= 0.25; doc.setFontSize(s); }
  return s;
}
/* the sheet's columns A to M in points: the Excel widths, scaled to the page width */
function msPdfCols() {
  const W = MS_PG.w - MS_PG.l - MS_PG.r, px = MS_LOG_W.slice(0, 13).map(msXPx), sum = px.reduce((a, b) => a + b, 0);
  return px.map(v => v * W / sum);
}
/* the sheet head as in the Excel file: project bar, block, logo boxes, legends, then date, the log's title and the code counter */
function msPdfHead(doc, log, d, c, logos) {
  const L = MS_PG.l, y0 = MS_PG.t, cols = msPdfCols(), X = [L]; cols.forEach(w => X.push(X[X.length - 1] + w));
  const rh = 11, gap = 3, y = r => y0 + (r < 8 ? (r - 1) * rh : 7 * rh + gap + (r - 9) * rh);   // top of sheet row r (1-7, 9-10)
  const head = msHeadRows(log, msProj());
  doc.setLineWidth(0.5); doc.setDrawColor(0, 0, 0); doc.setTextColor(0, 0, 0);
  const box = (c1, r1, c2, r2, fill) => { if (fill) doc.setFillColor(...MS_RGB(fill)); doc.rect(X[c1 - 1], y(r1), X[c2] - X[c1 - 1], y(r2) + rh - y(r1), fill ? 'FD' : 'S'); };
  const text = (t, c1, c2, r1, r2, o) => {
    const x1 = X[c1 - 1], x2 = X[c2], size = msPdfFit(doc, t, x2 - x1 - 6, o.size, o.min || 5, o.bold);
    const ty = o.bottom ? y(r2) + rh - 3 : (y(r1) + y(r2) + rh) / 2 + size * 0.34;
    doc.text(t, o.left ? x1 + 3 : (x1 + x2) / 2, ty, { align: o.left ? 'left' : 'center' });
  };
  // row 1: the project (white Arial, here Helvetica, on black) and LEGENDS
  box(1, 1, 10, 1, '#000000'); doc.setTextColor(255, 255, 255);
  doc.setFont('helvetica', 'bold'); let ts = 7.6; doc.setFontSize(ts); while (ts > 5 && doc.getTextWidth(head.title) > X[10] - X[0] - 10) { ts -= 0.25; doc.setFontSize(ts); }
  doc.text(head.title, (X[0] + X[10]) / 2, y(1) + rh / 2 + ts * 0.35, { align: 'center' }); doc.setTextColor(0, 0, 0);
  box(11, 1, 13, 1); text('LEGENDS', 11, 13, 1, 1, { size: 6.6, bold: true });
  // rows 2 to 7: the block
  for (let i = 0; i < 6; i++) {
    const r = 2 + i, b = head.rows[i]; box(1, r, 3, r);
    if (b) { text(b.label, 1, 2, r, r, { size: 6, min: 4.5, bold: true, left: true }); text(': ' + b.value, 3, 3, r, r, { size: 6, min: 4.5, bold: true, left: true }); }
  }
  // the logo boxes: names in row 2, logos in rows 3-5 (rows 6-7 blank)
  const spans = [[4, 4], [5, 6], [7, 8], [9, 10]];
  box(4, 2, 10, 7);
  MS_LOGO_BOX.forEach(([k, label], i) => {
    const [c1, c2] = spans[i]; text(label, c1, c2, 2, 2, { size: 6 });
    const lg = logos && logos[k]; if (!lg) return;
    const bw = X[c2] - X[c1 - 1] - 6, bh = 3 * rh - 4, s = Math.min(bw / lg.w, bh / lg.h), w = lg.w * s, h = lg.h * s;
    try { doc.addImage(lg.data, 'PNG', (X[c1 - 1] + X[c2] - w) / 2, y(3) + (3 * rh - h) / 2, w, h, 'mslogo-' + k, 'FAST'); } catch (e) { /* left out */ }
  });
  // the legends
  MS_LEGEND.forEach(([k, t], i) => { const r = 2 + i; box(11, r, 11, r, MS_FILL[k]); text(k, 11, 11, r, r, { size: 7.6, bold: true }); box(12, r, 13, r); text(t, 12, 13, r, r, { size: 6.5, left: true }); });
  // rows 9 and 10
  box(1, 9, 2, 10); text('Date:', 1, 1, 9, 10, { size: 6, bold: true, bottom: true }); text(msFmtLong(msFromDay(msToday())), 2, 2, 9, 10, { size: 6, min: 4.5, bold: true, bottom: true });
  box(3, 9, 5, 10); text(`${d.name} METHOD STATEMENT SUBMITTAL LOG`, 3, 5, 9, 10, { size: 7.6, min: 5.5, bold: true });
  [['CODE', 'Total', null]].concat(MS_COUNTED.map(k => [k, String(c[k]), MS_FILL[k]])).concat([['TOTAL', String(c.sub), null]]).forEach(([h, v, f], i) => {
    const col = 6 + i; box(col, 9, col, 9, f || '#FFFFFF'); box(col, 10, col, 10, '#FFFFFF');
    text(h, col, col, 9, 9, { size: 7.6, bold: true }); text(v, col, col, 10, 10, { size: 7.6, bold: true });
  });
  return y(10) + rh;
}
function msPdfLog(doc, log, d, logos, first) {
  const items = msItemsOf(log, d.code), c = msCounts(items);
  if (!first) doc.addPage();
  const startY = msPdfHead(doc, log, d, c, logos);
  const cols = msPdfCols();
  const ban = (text, fill) => [{ content: text, colSpan: 13, styles: { fillColor: MS_RGB(fill), fontStyle: 'bold', halign: 'center', fontSize: 7.5, cellPadding: 3.5 } }];
  const st = v => v ? { content: v, styles: { fillColor: MS_RGB(MS_FILL[v]), fontStyle: 'bold', halign: 'center' } } : '';
  const body = [ban(d.name, '#D9D9D9')];
  let no = 0;
  const t0 = msToday();
  for (const s of ['I', 'T']) {
    body.push(ban(MS_STAGE[s], '#FCE4D6'));
    for (const it of items.filter(x => x.s === s)) {
      const pd = msDay(it.plan), od = pd != null && !it.sub ? (pd < t0 ? ['#FFC7CE', '#9C0006'] : pd - t0 <= 7 ? ['#FFEB9C', '#9C5700'] : null) : null;
      body.push([String(++no), it.b, it.t, it.ref, it.rev, it.d,
        od ? { content: msFmt(it.plan), styles: { fillColor: MS_RGB(od[0]), textColor: MS_RGB(od[1]) } } : msFmt(it.plan),
        { content: msFmt(it.sub), styles: { textColor: [0, 0, 255] } }, { content: msFmt(it.ret), styles: { textColor: [0, 0, 255] } }, String(msReview(it)), st(it.st), st(it.fin), it.rem]);
    }
  }
  const head = [[{ content: 'SN', rowSpan: 2 }, { content: 'Unifier Ref. Number', rowSpan: 2 }, { content: 'Method Statement Title', rowSpan: 2 }, { content: 'Method Statement Reference No.', rowSpan: 2 }, { content: 'Rev.', rowSpan: 2 }, { content: 'Discipline', rowSpan: 2 }, { content: 'Planned Submission Date', rowSpan: 2 }, { content: 'Method Statement Status', colSpan: 4 }, { content: 'Final Status', rowSpan: 2 }, { content: 'Remark', rowSpan: 2 }],
    ['Submitted Date', 'Return Date', 'Review Period (in days)', 'Status']];
  doc.autoTable({
    head, body, startY, margin: { left: MS_PG.l, right: MS_PG.r, top: MS_PG.t, bottom: MS_PG.b }, theme: 'grid', showHead: 'everyPage', rowPageBreak: 'avoid',
    styles: { font: 'Carlito', fontSize: 6.8, cellPadding: { top: 3, bottom: 3, left: 2.5, right: 2.5 }, lineColor: [0, 0, 0], lineWidth: 0.4, textColor: [0, 0, 0], valign: 'middle', halign: 'center', overflow: 'linebreak', minCellHeight: 17 },
    headStyles: { fillColor: MS_RGB('#F8CBAD'), fontStyle: 'bold', fontSize: 6.8, halign: 'center', valign: 'middle', minCellHeight: 12 },
    columnStyles: Object.fromEntries(cols.map((w, i) => [i, { cellWidth: w, ...(i === 2 || i === 12 ? { halign: 'left' } : {}) }]))
  });
}
function msPdfSummary(doc, log, logo) {
  const L = MS_PG.l, R = MS_PG.w - MS_PG.r, y0 = MS_PG.t;
  const pv = msProjTitle(log);
  const lw = 120, lh = lw * 132 / 448;
  if (logo) doc.addImage(logo, 'PNG', R - lw, y0 - 4, lw, lh);
  doc.setTextColor(0, 0, 0);
  const t1 = `PROJECT : ${pv}`; msPdfFit(doc, t1, R - lw - 16 - L, 10, 7, true); doc.text(t1, L, y0 + 10);
  doc.setFontSize(9.5); doc.text('METHOD STATEMENT OVERALL SUMMARY', L, y0 + 24);
  doc.setFontSize(7.5); doc.text(`DATE:  ${msFmtSlash(msFromDay(msToday()))}`, L, y0 + 36);
  let y = y0 + lh + 14;
  const W = R - L, cw = [24, 160, 62, 54, 54, 54, 54, 54, 54, 96]; cw.push(W - cw.reduce((a, b) => a + b, 0));
  for (const [title, st] of [['OVERALL', ''], ['INSTALLATION METHOD STATEMENTS', 'I'], ['TESTING & COMMISSIONING METHOD STATEMENTS', 'T']]) {
    const tot = msCounts(log.items.filter(it => !st || it.s === st));
    const rows = MS_DISC.map((d, i) => { const c = msCounts(msItemsOf(log, d.code, st)); return [String(i + 1), d.sum, String(c.total)].concat(MS_COUNTED.map(k => String(c[k]))).concat([String(st ? c.toSubSection : c.toSubOverall), '']); });
    const fill = MS_COUNTED.map(k => MS_RGB(MS_FILL[k]));
    doc.autoTable({
      startY: y, margin: { left: L, right: MS_PG.r }, theme: 'grid',
      head: [[{ content: title, colSpan: 11, styles: { fillColor: MS_RGB('#1F4E78'), textColor: [255, 255, 255], fontSize: 7.5 } }],
        ['SN', 'Method Statements', 'Total MS'].map(h => ({ content: h })).concat(MS_COUNTED.map((k, j) => ({ content: k === 'UR' ? 'Under Review' : `${k}' Status`, styles: { fillColor: fill[j] } }))).concat([{ content: 'To Be Submitted\n(including resubmissions)' }, { content: 'Remarks' }])],
      body: rows.concat([[{ content: 'TOTAL', colSpan: 2, styles: { fontStyle: 'bold', fillColor: MS_RGB('#D9E1F2') } }, { content: String(tot.total), styles: { fontStyle: 'bold', fillColor: MS_RGB('#D9E1F2') } }]
        .concat(MS_COUNTED.map((k, j) => ({ content: String(tot[k]), styles: { fontStyle: 'bold', fillColor: fill[j] } })))
        .concat([{ content: String(st ? tot.toSubSection : tot.toSubOverall), styles: { fontStyle: 'bold', fillColor: MS_RGB('#D9E1F2') } }, { content: '', styles: { fillColor: MS_RGB('#D9E1F2') } }])]),
      styles: { font: 'Carlito', fontSize: 7, cellPadding: 2.4, lineColor: [0, 0, 0], lineWidth: 0.4, textColor: [0, 0, 0], halign: 'center', valign: 'middle' },
      headStyles: { fillColor: MS_RGB('#F8CBAD'), fontStyle: 'bold', fontSize: 7 },
      columnStyles: Object.fromEntries(cw.map((w, i) => [i, { cellWidth: w, ...(i === 1 ? { halign: 'left' } : {}) }]))
    });
    y = doc.lastAutoTable.finalY + 12;
  }
}
function msBuildPdf(jsPDF, log, proj, fonts, logo, rev, company) {
  const doc = new jsPDF({ orientation: 'landscape', unit: 'pt', format: 'a4', compress: true });
  doc.addFileToVFS('Carlito-Regular.ttf', fonts.r); doc.addFont('Carlito-Regular.ttf', 'Carlito', 'normal');
  doc.addFileToVFS('Carlito-Bold.ttf', fonts.b); doc.addFont('Carlito-Bold.ttf', 'Carlito', 'bold');
  doc.setFont('Carlito', 'normal');
  doc.setProperties({ title: `${proj.no} ${proj.name || ''} - Method Statement Log`.trim(), creator: 'Oxypro Project Library', subject: 'Method Statement Submittal Log' });
  msPdfSummary(doc, log, logo);
  const logos = { oxy: { data: logo, w: 448, h: 132 } };
  for (const k of ['client', 'consultant', 'contractor']) if (company && company[k]) logos[k] = { ...company[k], id: k };
  for (const d of MS_DISC) if (msItemsOf(log, d.code).length) msPdfLog(doc, log, d, logos, false);
  const n = doc.getNumberOfPages(), foot = `${proj.no}${proj.name ? ' · ' + proj.name : ''} · Method Statement Submittal Log · Rev ${rev || '00'}`;
  for (let i = 1; i <= n; i++) {
    doc.setPage(i); doc.setFont('Carlito', 'normal'); doc.setFontSize(6.5); doc.setTextColor(110, 110, 110);
    doc.text(foot, MS_PG.l, MS_PG.h - 12); doc.text(`Page ${i} of ${n}`, MS_PG.w - MS_PG.r, MS_PG.h - 12, { align: 'right' });
  }
  return doc;
}
async function msSavePdf(print) {
  await loadScript(LIBS.jspdf); await loadScript(MS_LIBS.autotable);
  const doc = msBuildPdf(window.jspdf.jsPDF, MSV.log, msProj(), msPdfFonts(), MS_LOGO, MSV.log.rev, await msLogos(msProj()));
  const blob = doc.output('blob');
  if (print && GH) {   // a normal website may open the PDF in a new tab, where the browser prints it
    const url = URL.createObjectURL(blob), w = window.open(url, '_blank');
    setTimeout(() => URL.revokeObjectURL(url), 600000);
    if (w) { toast('The PDF opened in a new tab: print it from there (A4 landscape, actual size).', 7000); return; }
  }
  const ok = await saveFile(msFileBase() + (print ? ' - Print' : '') + '.pdf', blob);
  if (ok && print) toast('Open the PDF and print it: A4 landscape, actual size.', 7000);
}
