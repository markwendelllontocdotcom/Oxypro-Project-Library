/* ---------- MSRA Log: PDF for printing (jsPDF + AutoTable), A4 landscape ---------- */
const MS_RGB = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
const MS_PG = { w: 841.89, h: 595.28, l: 20, r: 20, t: 22, b: 26 };
function msPdfFit(doc, text, maxW, size, min, bold) {
  doc.setFont('OpenSans', bold ? 'bold' : 'normal');
  let s = size; doc.setFontSize(s);
  while (s > min && doc.getTextWidth(text) > maxW) { s -= 0.25; doc.setFontSize(s); }
  return s;
}
function msPdfHead(doc, log, d, c, logo) {
  const L = MS_PG.l, R = MS_PG.w - MS_PG.r, y0 = MS_PG.t;
  doc.setTextColor(0, 0, 0);
  // legends, top right
  const lx = R - 236, cw = 34, rh = 10.5;
  doc.setLineWidth(0.5); doc.setDrawColor(0, 0, 0);
  doc.setFillColor(255, 255, 255); doc.rect(lx, y0, 236, rh, 'S');
  doc.setFont('OpenSans', 'bold'); doc.setFontSize(7.5); doc.text('LEGENDS', lx + 118, y0 + 7.3, { align: 'center' });
  MS_LEGEND.forEach(([k, t], i) => {
    const y = y0 + rh * (i + 1);
    doc.setFillColor(...MS_RGB(MS_FILL[k])); doc.rect(lx, y, cw, rh, 'FD');
    doc.rect(lx + cw, y, 236 - cw, rh, 'S');
    doc.setFont('OpenSans', 'bold'); doc.setFontSize(7.5); doc.text(k, lx + cw / 2, y + 7.3, { align: 'center' });
    doc.setFont('OpenSans', 'normal'); doc.setFontSize(7); doc.text(t, lx + cw + 4, y + 7.2);
  });
  // logo between the block and the legends
  const lw = 128, lh = lw * 132 / 448;
  if (logo) doc.addImage(logo, 'PNG', lx - 22 - lw, y0 + 4, lw, lh);
  // title and project block
  const bx = L + 78, room = lx - 22 - lw - 12 - bx;
  doc.setFont('OpenSans', 'bold'); msPdfFit(doc, `${d.name} METHOD STATEMENT SUBMITTAL LOG`, lx - 22 - lw - 12 - L, 11, 8, true);
  doc.text(`${d.name} METHOD STATEMENT SUBMITTAL LOG`, L, y0 + 9);
  let y = y0 + 24;
  for (const r of log.block) {
    doc.setFont('OpenSans', 'bold'); doc.setFontSize(7.5); doc.text(r.label, L, y);
    const v = ': ' + r.value, s = msPdfFit(doc, v, room, 7.5, 6, true);
    const lines = doc.splitTextToSize(v, room).slice(0, 2);
    doc.setFontSize(s); doc.text(lines, bx, y);
    y += 10.5 * lines.length;
  }
  // date and the code counter
  const sy = Math.max(y0 + rh * 7 + 8, y - 4), sw = [50, 36, 36, 36, 36, 36, 36, 50], sx0 = R - sw.reduce((a, b) => a + b, 0);
  let x = sx0;
  const cells = [['CODE', 'Total']].concat(MS_COUNTED.map(k => [k, String(c[k])])).concat([['TOTAL', String(c.sub)]]);
  cells.forEach(([h, v], i) => {
    const k = MS_COUNTED[i - 1];
    if (k) doc.setFillColor(...MS_RGB(MS_FILL[k])); else doc.setFillColor(255, 255, 255);
    doc.rect(x, sy, sw[i], 11, 'FD'); doc.setFillColor(255, 255, 255); doc.rect(x, sy + 11, sw[i], 11, 'FD');
    doc.setFont('OpenSans', 'bold'); doc.setFontSize(7.5); doc.text(h, x + sw[i] / 2, sy + 7.8, { align: 'center' }); doc.text(v, x + sw[i] / 2, sy + 18.8, { align: 'center' });
    x += sw[i];
  });
  doc.setFont('OpenSans', 'bold'); doc.setFontSize(7.5); doc.text(`Date:  ${msFmtLong(msFromDay(msToday()))}`, L, sy + 18.8);
  return sy + 22 + 6;
}
const MS_PDF_COLS = [22, 46, 190, 86, 20, 40, 46, 44, 44, 36, 30, 34];
function msPdfLog(doc, log, d, logo, first) {
  const items = msItemsOf(log, d.code), c = msCounts(items);
  if (!first) doc.addPage();
  const startY = msPdfHead(doc, log, d, c, logo);
  const W = MS_PG.w - MS_PG.l - MS_PG.r, cols = MS_PDF_COLS.concat([W - MS_PDF_COLS.reduce((a, b) => a + b, 0)]);
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
  const head = [[{ content: 'No.', rowSpan: 2 }, { content: 'Unifier Ref. Number', rowSpan: 2 }, { content: 'Method Statement Title', rowSpan: 2 }, { content: 'Method Statement Reference No.', rowSpan: 2 }, { content: 'Rev.', rowSpan: 2 }, { content: 'Discipline', rowSpan: 2 }, { content: 'Planned Submission Date', rowSpan: 2 }, { content: 'Method Statement Status', colSpan: 4 }, { content: 'Final Status', rowSpan: 2 }, { content: 'Remark', rowSpan: 2 }],
    ['Submitted Date', 'Return Date', 'Review Period (in days)', 'Status']];
  doc.autoTable({
    head, body, startY, margin: { left: MS_PG.l, right: MS_PG.r, top: MS_PG.t, bottom: MS_PG.b }, theme: 'grid', showHead: 'everyPage', rowPageBreak: 'avoid',
    styles: { font: 'OpenSans', fontSize: 6.8, cellPadding: { top: 3, bottom: 3, left: 2.5, right: 2.5 }, lineColor: [0, 0, 0], lineWidth: 0.4, textColor: [0, 0, 0], valign: 'middle', halign: 'center', overflow: 'linebreak', minCellHeight: 17 },
    headStyles: { fillColor: MS_RGB('#F8CBAD'), fontStyle: 'bold', fontSize: 6.8, halign: 'center', valign: 'middle', minCellHeight: 12 },
    columnStyles: Object.fromEntries(cols.map((w, i) => [i, { cellWidth: w, ...(i === 2 || i === 12 ? { halign: 'left' } : {}) }]))
  });
}
function msPdfSummary(doc, log, logo) {
  const L = MS_PG.l, R = MS_PG.w - MS_PG.r, y0 = MS_PG.t;
  const pv = (log.block.find(r => /^project$/i.test(r.label.trim())) || log.block[0] || { value: '' }).value;
  const lw = 120, lh = lw * 132 / 448;
  if (logo) doc.addImage(logo, 'PNG', R - lw, y0 - 4, lw, lh);
  doc.setTextColor(0, 0, 0);
  const t1 = `PROJECT : ${pv}`; msPdfFit(doc, t1, R - lw - 16 - L, 10, 7, true); doc.text(t1, L, y0 + 10);
  doc.setFontSize(9.5); doc.text('METHOD STATEMENT OVERALL SUMMARY', L, y0 + 24);
  doc.setFontSize(7.5); doc.text(`DATE:  ${msFmt(msFromDay(msToday()))}`, R, y0 + lh + 6, { align: 'right' });
  let y = y0 + lh + 14;
  const W = R - L, cw = [24, 160, 62, 54, 54, 54, 54, 54, 54, 96]; cw.push(W - cw.reduce((a, b) => a + b, 0));
  for (const [title, st] of [['OVERALL', ''], ['INSTALLATION METHOD STATEMENTS', 'I'], ['TESTING & COMMISSIONING METHOD STATEMENTS', 'T']]) {
    const tot = msCounts(log.items.filter(it => !st || it.s === st));
    const rows = MS_DISC.map((d, i) => { const c = msCounts(msItemsOf(log, d.code, st)); return [String(i + 1), d.sum, String(c.total)].concat(MS_COUNTED.map(k => String(c[k]))).concat([String(st ? c.toSubSection : c.toSubOverall), '']); });
    const fill = MS_COUNTED.map(k => MS_RGB(MS_FILL[k]));
    doc.autoTable({
      startY: y, margin: { left: L, right: MS_PG.r }, theme: 'grid',
      head: [[{ content: title, colSpan: 11, styles: { fillColor: MS_RGB('#1F4E78'), textColor: [255, 255, 255], fontSize: 7.5 } }],
        ['SN', 'Method Statements', 'Total MS'].map(h => ({ content: h })).concat(MS_COUNTED.map((k, j) => ({ content: k === 'UR' ? 'Under Review' : `${k}' Status`, styles: { fillColor: fill[j] } }))).concat([{ content: 'To Be Submitted (including resubmissions)' }, { content: 'Remarks' }])],
      body: rows.concat([[{ content: 'TOTAL', colSpan: 2, styles: { fontStyle: 'bold', fillColor: MS_RGB('#D9E1F2') } }, { content: String(tot.total), styles: { fontStyle: 'bold', fillColor: MS_RGB('#D9E1F2') } }]
        .concat(MS_COUNTED.map((k, j) => ({ content: String(tot[k]), styles: { fontStyle: 'bold', fillColor: fill[j] } })))
        .concat([{ content: String(st ? tot.toSubSection : tot.toSubOverall), styles: { fontStyle: 'bold', fillColor: MS_RGB('#D9E1F2') } }, { content: '', styles: { fillColor: MS_RGB('#D9E1F2') } }])]),
      styles: { font: 'OpenSans', fontSize: 7, cellPadding: 2.4, lineColor: [0, 0, 0], lineWidth: 0.4, textColor: [0, 0, 0], halign: 'center', valign: 'middle' },
      headStyles: { fillColor: MS_RGB('#F8CBAD'), fontStyle: 'bold', fontSize: 7 },
      columnStyles: Object.fromEntries(cw.map((w, i) => [i, { cellWidth: w, ...(i === 1 ? { halign: 'left' } : {}) }]))
    });
    y = doc.lastAutoTable.finalY + 12;
  }
}
function msBuildPdf(jsPDF, log, proj, fonts, logo, rev) {
  const doc = new jsPDF({ orientation: 'landscape', unit: 'pt', format: 'a4', compress: true });
  doc.addFileToVFS('OpenSans-Regular.ttf', fonts.r); doc.addFont('OpenSans-Regular.ttf', 'OpenSans', 'normal');
  doc.addFileToVFS('OpenSans-Bold.ttf', fonts.b); doc.addFont('OpenSans-Bold.ttf', 'OpenSans', 'bold');
  doc.setFont('OpenSans', 'normal');
  doc.setProperties({ title: `${proj.no} ${proj.name || ''} - Method Statement Log`.trim(), creator: 'Oxypro Project Library', subject: 'Method Statement Submittal Log' });
  msPdfSummary(doc, log, logo);
  for (const d of MS_DISC) if (msItemsOf(log, d.code).length) msPdfLog(doc, log, d, logo, false);
  const n = doc.getNumberOfPages(), foot = `${proj.no}${proj.name ? ' · ' + proj.name : ''} · Method Statement Submittal Log · Rev ${rev || '00'}`;
  for (let i = 1; i <= n; i++) {
    doc.setPage(i); doc.setFont('OpenSans', 'normal'); doc.setFontSize(6.5); doc.setTextColor(110, 110, 110);
    doc.text(foot, MS_PG.l, MS_PG.h - 12); doc.text(`Page ${i} of ${n}`, MS_PG.w - MS_PG.r, MS_PG.h - 12, { align: 'right' });
  }
  return doc;
}
async function msSavePdf(print) {
  await loadScript(LIBS.jspdf); await loadScript(MS_LIBS.autotable);
  const doc = msBuildPdf(window.jspdf.jsPDF, MSV.log, msProj(), MS_FONT_B64, MS_LOGO, MSV.log.rev);
  const ok = await saveFile(msFileBase() + (print ? ' - Print' : '') + '.pdf', doc.output('blob'));
  if (ok && print) toast('Open the PDF and print it: A4 landscape, actual size.', 7000);
}
