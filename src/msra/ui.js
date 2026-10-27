/* ---------- MSRA Log page ---------- */
const MS_LOGO = 'data:image/png;base64,__MSRA_LOGO__';
const MS_FONT_B64 = { r: '__OPENSANS_R__', b: '__OPENSANS_B__' };
const MSV = { no: null, log: null, base: '', dirty: false, tab: 'SUM', mode: 'view', state: 'idle', err: '', remote: null, unsub: null, rm: null, mslFilter: 'all', busy: '', menu: false };
const msProj = () => S.projects.get(MSV.no) || { no: MSV.no, name: '' };
const msName = () => { const p = msProj(); return `${p.no} ${p.name || ''}`.trim(); };
const msFileBase = () => { const p = msProj(); return safeName([p.code || p.no, p.name || 'Untitled project', 'Method Statement Log', 'Rev ' + ((MSV.log && MSV.log.rev) || '00')].join(' - ')); };
const msFontsReady = (() => { let pr = null; return () => pr || (pr = (async () => {
  try { for (const [w, k] of [['400', 'r'], ['700', 'b']]) { const f = new FontFace('Open Sans', b64ToBuf(MS_FONT_B64[k]), { weight: w }); await f.load(); document.fonts.add(f); } } catch (e) { /* the page falls back to the system font */ }
})()); })();

function msButtonHTML(p) {
  const has = S.msMeta && S.msMeta.has(p.no);
  return `<button type="button" class="btn" data-act="msra" title="${has ? 'Open this project\'s Method Statement Log' : 'Create the Method Statement Log for this project'}">${has ? 'Open MSRA Log' : 'Create MSRA Log'}</button>`;
}
function msSetDirty() { if (!MSV.dirty) { MSV.dirty = true; msRenderActions(); } }
function msCloseSub() { if (MSV.unsub) { try { MSV.unsub(); } catch (e) { /* gone */ } MSV.unsub = null; } }

function openMsra(no) {
  const p = S.projects.get(no); if (!p) return;
  msCloseSub();
  Object.assign(MSV, { no, log: null, base: '', dirty: false, tab: 'SUM', mode: 'view', state: 'loading', err: '', remote: null, rm: null, mslFilter: 'all', busy: '', menu: false });
  S.view = 'msra'; S.detailOpen = false;
  $('#view-library').hidden = true; $('#view-msra').hidden = false; renderSelbar(); renderDetail();
  window.scrollTo(0, 0);
  msFontsReady().then(() => { if (S.view === 'msra') msRenderBody(); });
  renderMs();
  if (!DB) { MSV.state = 'new'; renderMs(); return; }
  let first = true;
  MSV.unsub = DB.collection('mslogs').doc(no).onSnapshot(snap => {
    if (MSV.no !== no || S.view !== 'msra') return;
    const x = snap.exists ? snap.data() : null;
    if (first) { first = false; if (x) msLoad(x); else MSV.state = 'new'; renderMs(); return; }
    if (!x) { if (MSV.state === 'ready' && !MSV.dirty) { MSV.state = 'new'; MSV.log = null; renderMs(); toast('This MSRA Log was deleted by another editor.'); } return; }
    if (x.updatedAt && ((MSV.log && x.updatedAt === MSV.log.updatedAt) || x.updatedAt === MSV.savingAt)) return;    // our own save
    if (!MSV.log || !MSV.dirty) { msLoad(x); renderMs(); if (MSV.log) toast('The MSRA Log was updated by another editor.'); }
    else { MSV.remote = x; msRenderBody(); }
  }, err => { if (MSV.no !== no) return; MSV.state = 'error'; MSV.err = (err && err.code) || ''; renderMs(); });
}
function msLoad(x) { MSV.log = msClean(x, msProj()); MSV.base = JSON.stringify(MSV.log); MSV.dirty = false; MSV.remote = null; MSV.state = 'ready'; }
function closeMsra(force) {
  if (!force && MSV.dirty) return msAskLeave();
  msCloseSub(); MSV.no = null; MSV.log = null; MSV.dirty = false;
  S.view = 'library'; $('#view-msra').hidden = true; $('#view-library').hidden = false;
  renderAll(); window.scrollTo(0, 0);
}
function msAskLeave() {
  const w = canWrite();
  openModal(`<div class="dialog dialog-sm">
    <div class="dialog-head"><h2>Unsaved changes</h2></div>
    <div class="dialog-body"><p style="margin:0">${w ? 'Save the changes to this MSRA Log before going back to the library?' : 'Your changes to this MSRA Log are not saved in the library (only editors can save). Download it with Save as first if you need it.'}</p></div>
    <div class="dialog-foot"><button type="button" class="btn" data-close>Stay here</button><button type="button" class="btn${w ? '' : ' btn-primary'}" id="ms-leave-discard">Discard changes</button>${w ? '<button type="button" class="btn btn-primary" id="ms-leave-save">Save and go back</button>' : ''}</div>
  </div>`);
  $('#ms-leave-discard').addEventListener('click', () => { closeModal(); closeMsra(true); });
  if (w) $('#ms-leave-save').addEventListener('click', async () => { closeModal(); if (await msSave()) closeMsra(true); });
}

/* ---------- rendering ---------- */
function renderMs() {
  const p = msProj();
  $('#ms-proj').textContent = `${p.no}${p.name ? ' · ' + p.name : ''}`;
  msRenderActions(); msRenderBody();
}
function msRenderActions() {
  const el = $('#ms-actions'); if (!el) return;
  if (MSV.state !== 'ready') { el.innerHTML = ''; return; }
  const w = canWrite(), e = MSV.mode === 'edit';
  el.innerHTML = `<div class="seg" role="group" aria-label="Mode"><button type="button" aria-pressed="${!e}" data-ms-act="mode-view">View</button><button type="button" aria-pressed="${e}" data-ms-act="mode-edit">Edit</button></div>
    <button type="button" class="btn" data-ms-act="msl-up" title="Upload the planner's Material Submittal Log (Excel)">${MSV.log.msl ? 'Replace MSL' : 'Upload MSL'}</button>
    <div class="viewmenu ms-saveas"><button type="button" class="btn" data-ms-act="saveas" aria-haspopup="menu" aria-expanded="${MSV.menu}">Save as<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></button>
      <div class="menu" role="menu" ${MSV.menu ? '' : 'hidden'}>
        <button type="button" class="menu-item" role="menuitem" data-ms-act="save-xlsx"><span>Excel workbook (.xlsx)<small>Summary, the seven discipline logs and the master list, as in the template</small></span></button>
        <button type="button" class="menu-item" role="menuitem" data-ms-act="save-pdf"><span>PDF (.pdf)<small>Summary and each discipline log, A4 landscape</small></span></button>
      </div></div>
    <button type="button" class="btn" data-ms-act="print" title="Makes a print-ready PDF (A4 landscape) to open and print">Print</button>
    ${w ? `<button type="button" class="btn${MSV.dirty ? ' btn-primary' : ''}" data-ms-act="save"${MSV.dirty && !MSV.busy ? '' : ' disabled'}>${MSV.busy === 'save' ? 'Saving…' : MSV.dirty ? 'Save to library' : 'Saved'}</button>` : ''}`;
}
function msRenderBody() {
  const el = $('#ms-body'); if (!el) return;
  const same = MSV.shown === MSV.tab + MSV.mode, keep = same && el.querySelector('.ms-scroll'), sx = keep ? keep.scrollLeft : 0, sy = keep ? keep.scrollTop : 0;
  MSV.shown = MSV.tab + MSV.mode;
  if (MSV.state === 'loading') { el.innerHTML = '<div class="ms-empty"><p>Loading the MSRA Log…</p></div>'; return; }
  if (MSV.state === 'error') { el.innerHTML = `<div class="ms-empty"><h3>The MSRA Log could not be loaded</h3><p>${esc(MSV.err === 'revoked' ? 'Your access to the library changed. Reload the page.' : 'Check your connection and open it again.')}</p></div>`; return; }
  if (MSV.state === 'new') { el.innerHTML = msStartHTML(); return; }
  const log = MSV.log, n = c => msItemsOf(log, c).length;
  const tabs = [['SUM', 'Summary', log.items.length]].concat(MS_DISC.map(d => [d.code, d.code, n(d.code)])).concat([['MSL', 'MSL Ref', log.msl ? log.msl.items.length : '']]);
  el.innerHTML = `${msNoticeHTML()}
    <div class="ms-tabs" role="tablist" aria-label="Log sheets">${tabs.map(([k, l, c]) => `<button type="button" role="tab" aria-selected="${MSV.tab === k}" data-ms-tab="${k}" title="${esc(k === 'SUM' ? 'Overall summary' : k === 'MSL' ? 'Material Submittal Log (planner)' : MS_DNAME[k])}">${esc(l)}${c !== '' ? `<span class="n">${c}</span>` : ''}</button>`).join('')}</div>
    <div class="ms-panel ${MSV.mode === 'edit' ? 'editing' : ''}" role="tabpanel">${MSV.tab === 'SUM' ? msSummaryHTML() : MSV.tab === 'MSL' ? msMslHTML() : msSheetHTML(MSV.tab)}</div>`;
  const sc = el.querySelector('.ms-scroll'); if (sc && keep) { sc.scrollLeft = sx; sc.scrollTop = sy; }
  msFitHead();
  el.querySelectorAll('textarea.ms-c').forEach(msGrow);
}
function msNoticeHTML() {
  if (MSV.remote) return `<div class="ms-notice"><span>Another editor saved this log${MSV.remote.updatedAt ? ' at ' + esc(new Date(MSV.remote.updatedAt).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })) : ''}. Saving now replaces their version with yours.</span><button type="button" class="btn btn-sm" data-ms-act="load-remote">Load their version</button></div>`;
  if (!canWrite() && MSV.dirty) return `<div class="ms-notice"><span>Only the library's editors can save. Use Save as to keep your changes in a file.</span></div>`;
  return '';
}
function msStartHTML() {
  const p = msProj(), w = canWrite();
  const card = (how, title, text, tag) => `<button type="button" class="ms-start-card" data-ms-act="start" data-how="${how}"${tag ? ' data-rec="1"' : ''}><span class="ms-sc-t">${esc(title)}${tag ? `<span class="tag tag-rec">${esc(tag)}</span>` : ''}</span><span class="ms-sc-d">${esc(text)}</span></button>`;
  const ni = MS_STD.items.filter(x => x[1] === 'I').length, nt = MS_STD.items.length - ni;
  return `<div class="ms-start">
    <h3>Create the Method Statement Log for ${esc(msName())}</h3>
    <p class="hint">The log follows the Oxypro template (The Borough): Summary, seven discipline logs (HVAC, Plumbing, Electrical, ELV, Fire Fighting, LPG, MEP General) and the master list. The project block is filled from the library and you can edit it.</p>
    <div class="ms-start-cards">
      ${card('std', `Standard list (${MS_STD.items.length} method statements)`, `Starts at item no. 1 with the ${ni} installation and ${nt} testing & commissioning method statements of the standard. Add or remove method statements afterwards.`, 'Recommended')}
      ${card('msl', 'Standard list and the project\'s MSL', 'Upload the planner\'s Material Submittal Log (Excel). Its materials are linked to the method statements; you see which method statements no material needs and which materials no method statement covers.')}
      ${card('empty', 'Empty log', 'Starts with no method statements. Add them discipline by discipline.')}
    </div>
    ${w ? '' : '<p class="hint">Only the library\'s editors can save the log to the library. You can still make it and download it with Save as.</p>'}
  </div>`;
}

/* the sheet header: title, project block, logo, legends, date and the code counter */
function msHeadHTML(title, c) {
  const log = MSV.log, e = MSV.mode === 'edit';
  const block = log.block.map((r, i) => e
    ? `<tr><td><input class="ms-in" data-bl="${i}" data-f="label" value="${esc(r.label)}" aria-label="Label of row ${i + 1}" maxlength="60"></td><td class="ms-colon">:</td><td><input class="ms-in" data-bl="${i}" data-f="value" value="${esc(r.value)}" aria-label="${esc(r.label || 'Value of row ' + (i + 1))}" maxlength="400"></td><td class="ms-bl-tools"><button type="button" class="ms-x" data-ms-act="bl-rm" data-i="${i}" aria-label="Remove ${esc(r.label || 'this row')}" title="Remove row"${log.block.length < 2 ? ' disabled' : ''}>${MS_ICON.x}</button></td></tr>`
    : `<tr><th>${esc(r.label)}</th><td>: ${esc(r.value)}</td></tr>`).join('');
  return `<div class="ms-head">
    <div class="ms-h-left">
      <div class="ms-h-title">${esc(title)}</div>
      <table class="ms-block">${block}</table>
      ${e ? `<div class="ms-bl-add">${log.block.length < MS_BLOCK_MAX ? '<button type="button" class="btn btn-ghost btn-sm" data-ms-act="bl-add">+ Add row</button>' : ''}<button type="button" class="btn btn-ghost btn-sm" data-ms-act="bl-reset" title="Fill the block again from the library's project details">Refill from the library</button><label class="ms-rev">Log revision <input class="ms-in" data-ms-rev value="${esc(log.rev)}" maxlength="10" aria-label="Log revision"></label></div>` : ''}
      <div class="ms-date"><b>Date:</b> ${esc(msFmtLong(msFromDay(msToday())))}</div>
    </div>
    <div class="ms-h-logo"><img src="${MS_LOGO}" alt="Oxypro Electromechanical Works LLC"></div>
    <div class="ms-h-right">
      <table class="ms-legend"><tr><th colspan="2">LEGENDS</th></tr>${MS_LEGEND.map(([k, t]) => `<tr><td class="st-${msCls(k)}">${k}</td><td>${t}</td></tr>`).join('')}</table>
      ${c ? `<table class="ms-strip"><tr><th>CODE</th>${MS_COUNTED.map(k => `<td class="st-${msCls(k)}">${k}</td>`).join('')}<th>TOTAL</th></tr><tr><th>Total</th>${MS_COUNTED.map(k => `<td data-cnt="${k}">${c[k]}</td>`).join('')}<td data-cnt="sub">${c.sub}</td></tr></table>` : ''}
    </div>
  </div>`;
}
const msCls = k => k === 'n/a' ? 'na' : k;
const MS_ICON = {
  x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  up: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 15l6-6 6 6"/></svg>',
  down: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>',
  link: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/></svg>'
};
const MS_COLS = [['No.', 50], ['Unifier Ref. Number', 90], ['Method Statement Title', 400], ['Method Statement Reference No.', 190], ['Rev.', 46], ['Discipline', 76], ['Planned Submission Date', 112], ['Submitted Date', 108], ['Return Date', 108], ['Review Period (in days)', 82], ['Status', 74], ['Final Status', 82], ['Remark', 210]];
function msDateCls(it) {
  const pd = msDay(it.plan); if (pd == null || it.sub) return '';
  const t0 = msToday(); return pd < t0 ? ' ms-od' : pd - t0 <= 7 ? ' ms-soon' : '';
}
function msSelect(k, it) { return `<select class="ms-c ms-stsel st-${msCls(it[k]) || 'none'}" data-k="${k}" aria-label="${k === 'st' ? 'Status' : 'Final status'}"><option value=""></option>${MS_STATUS.map(s => `<option${it[k] === s ? ' selected' : ''}>${s}</option>`).join('')}</select>`; }
function msRowHTML(it, no, idx, list) {
  const e = MSV.mode === 'edit', rv = msReview(it), hasMsl = !!MSV.log.msl;
  if (!e) {
    return `<tr data-id="${it.id}"><td class="c f1">${no}</td><td class="c f2">${esc(it.b)}</td><td class="f3">${esc(it.t)}</td><td class="c">${esc(it.ref)}</td><td class="c">${esc(it.rev)}</td><td class="c">${it.d}</td>
      <td class="c${msDateCls(it)}">${msFmt(it.plan)}</td><td class="c">${msFmt(it.sub)}</td><td class="c">${msFmt(it.ret)}</td><td class="c">${rv}</td>
      <td class="c st-${msCls(it.st) || 'none'}">${esc(it.st)}</td><td class="c st-${msCls(it.fin) || 'none'}">${esc(it.fin)}</td><td>${esc(it.rem)}</td></tr>`;
  }
  const rm = MSV.rm === it.id;
  const nm = it.m.length;
  return `<tr data-id="${it.id}"><td class="c f1">${no}</td>
    <td class="f2"><input class="ms-c c" data-k="b" value="${esc(it.b)}" aria-label="Unifier ref. number" maxlength="80"></td>
    <td class="f3"><textarea class="ms-c" data-k="t" rows="1" aria-label="Method statement title" maxlength="400" placeholder="Method statement title">${esc(it.t)}</textarea></td>
    <td><input class="ms-c c" data-k="ref" value="${esc(it.ref)}" aria-label="Method statement reference no." maxlength="120"></td>
    <td><input class="ms-c c" data-k="rev" value="${esc(it.rev)}" aria-label="Revision" maxlength="10"></td>
    <td class="c">${it.d}</td>
    <td class="${msDateCls(it).trim()}"><input type="date" class="ms-c${it.plan ? '' : ' is-empty'}" data-k="plan" value="${it.plan}" aria-label="Planned submission date"></td>
    <td><input type="date" class="ms-c${it.sub ? '' : ' is-empty'}" data-k="sub" value="${it.sub}" aria-label="Submitted date"></td>
    <td><input type="date" class="ms-c${it.ret ? '' : ' is-empty'}" data-k="ret" value="${it.ret}" aria-label="Return date"></td>
    <td class="c" data-rv>${rv}</td>
    <td class="c">${msSelect('st', it)}</td><td class="c">${msSelect('fin', it)}</td>
    <td><textarea class="ms-c" data-k="rem" rows="1" aria-label="Remark" maxlength="400">${esc(it.rem)}</textarea></td>
    <td class="ms-tools">${rm
      ? `<span class="ms-rmq">Remove?</span><button type="button" class="btn btn-sm btn-danger-solid" data-ms-act="rm-yes">Remove</button><button type="button" class="btn btn-sm" data-ms-act="rm-no">Keep</button>`
      : `<button type="button" class="ms-ib" data-ms-act="up" title="Move up" aria-label="Move up"${idx === 0 ? ' disabled' : ''}>${MS_ICON.up}</button><button type="button" class="ms-ib" data-ms-act="down" title="Move down" aria-label="Move down"${idx === list.length - 1 ? ' disabled' : ''}>${MS_ICON.down}</button>${hasMsl ? `<button type="button" class="ms-ib ms-mat${nm ? '' : ' none'}" data-ms-act="mats" title="Related materials from the MSL" aria-label="Related materials (${nm})">${MS_ICON.link}<span>${nm}</span></button>` : ''}<button type="button" class="ms-ib ms-rm" data-ms-act="rm" title="Remove this method statement" aria-label="Remove">${MS_ICON.x}</button>`}</td></tr>`;
}
function msSheetHTML(code) {
  const log = MSV.log, e = MSV.mode === 'edit', all = msItemsOf(log, code), c = msCounts(all);
  let no = 0;
  const cols = MS_COLS.concat(e ? [['', MSV.log.msl ? 150 : 118]] : []);
  const section = st => {
    const list = all.filter(it => it.s === st);
    const rows = list.map((it, i) => msRowHTML(it, ++no, i, list)).join('');
    return `<tr class="ms-ban-s"><td colspan="13">${MS_STAGE[st]}</td>${e ? '<td class="ms-tools"></td>' : ''}</tr>${rows}
      ${!list.length && !e ? '<tr class="ms-none"><td colspan="13">No method statements in this section</td></tr>' : ''}
      ${e ? `<tr class="ms-addrow"><td colspan="13"><button type="button" class="btn btn-ghost btn-sm" data-ms-act="add" data-st="${st}">+ Add ${st === 'I' ? 'installation' : 'testing & commissioning'} method statement</button></td><td class="ms-tools"></td></tr>` : ''}`;
  };
  return `<div class="ms-scroll"><div class="ms-paper">
    ${msHeadHTML(`${MS_DNAME[code]} METHOD STATEMENT SUBMITTAL LOG`, c)}
    <table class="ms-log" data-code="${code}"><colgroup>${cols.map(([, w]) => `<col style="width:${w}px">`).join('')}</colgroup>
      <thead><tr>${MS_COLS.map(([l], i) => i >= 7 && i <= 10 ? (i === 7 ? '<th colspan="4" class="ms-grp">Method Statement Status</th>' : '') : `<th rowspan="2"${i < 3 ? ` class="f${i + 1}"` : ''}>${esc(l)}</th>`).join('')}${e ? '<th rowspan="2" class="ms-tools-h">Edit</th>' : ''}</tr>
        <tr>${MS_COLS.slice(7, 11).map(([l]) => `<th>${esc(l)}</th>`).join('')}</tr></thead>
      <tbody><tr class="ms-ban-d"><td colspan="13">${esc(MS_DNAME[code])}</td>${e ? '<td class="ms-tools"></td>' : ''}</tr>${section('I')}${section('T')}</tbody>
    </table></div></div>`;
}
function msSumTable(head, rows, tot, section) {
  const cell = v => `<td class="c">${v}</td>`;
  return `<table class="ms-sum"><thead><tr class="ms-sum-ban"><th colspan="10">${esc(head)}</th></tr>
    <tr><th>SN</th><th>Method Statements</th><th>Total MS</th>${MS_COUNTED.map(k => `<th class="st-${msCls(k)}">${k === 'UR' ? 'Under Review' : k + '\' Status'}</th>`).join('')}<th>To Be Submitted (including resubmissions)</th><th>Remarks</th></tr></thead>
    <tbody>${rows.map((r, i) => `<tr><td class="c">${i + 1}</td><td><button type="button" class="ms-link" data-ms-tab="${r.code}">${esc(r.label)}</button></td>${cell(r.c.total)}${MS_COUNTED.map(k => cell(r.c[k])).join('')}${cell(section ? r.c.toSubSection : r.c.toSubOverall)}<td></td></tr>`).join('')}
    <tr class="ms-sum-tot"><td colspan="2" class="c">TOTAL</td>${cell(tot.total)}${MS_COUNTED.map(k => `<td class="c st-${msCls(k)}">${tot[k]}</td>`).join('')}${cell(section ? tot.toSubSection : tot.toSubOverall)}<td></td></tr></tbody></table>`;
}
function msSummaryHTML() {
  const log = MSV.log, w = canWrite();
  const block = (st) => { const rows = MS_DISC.map(d => ({ code: d.code, label: d.sum, c: msCounts(msItemsOf(log, d.code, st)) })); return { rows, tot: msCounts(log.items.filter(it => !st || it.s === st)) }; };
  const o = block(''), I = block('I'), T = block('T');
  const pv = (log.block.find(r => /^project$/i.test(r.label.trim())) || log.block[0] || { value: '' }).value;
  const od = o.tot.overdue, soon = o.tot.soon;
  return `<div class="ms-scroll ms-scroll-sum"><div class="ms-paper ms-paper-sum">
    <div class="ms-sum-head"><div><div class="ms-h-title">PROJECT : ${esc(pv)}</div><div class="ms-h-sub">METHOD STATEMENT OVERALL SUMMARY</div></div><div class="ms-sum-logo"><img src="${MS_LOGO}" alt="Oxypro"><div class="ms-date"><b>DATE:</b> ${esc(msFmt(msFromDay(msToday())))}</div></div></div>
    ${msSumTable('OVERALL', o.rows, o.tot, false)}
    ${msSumTable('INSTALLATION METHOD STATEMENTS', I.rows, I.tot, true)}
    ${msSumTable('TESTING & COMMISSIONING METHOD STATEMENTS', T.rows, T.tot, true)}
  </div></div>
  <div class="ms-facts">
    <p>${o.tot.total} method statements: ${I.tot.total} installation and ${T.tot.total} testing & commissioning. ${o.tot.sub} with a final status, ${o.tot.A + o.tot.B} approved (A or B).${od ? ` <b class="ms-red">${od} overdue</b> (planned date passed, not submitted).` : ''}${soon ? ` ${soon} due within 7 days.` : ''} ${o.tot.planned < o.tot.total ? `${o.tot.total - o.tot.planned} without a planned submission date.` : ''}</p>
    <p class="hint">${log.updatedAt ? `Saved in the library ${esc(new Date(log.updatedAt).toLocaleString([], { day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: '2-digit' }))}.` : 'Not saved in the library yet.'} ${log.msl ? `MSL: ${esc(log.msl.file)} (${log.msl.items.length} materials).` : 'No MSL uploaded.'}</p>
    ${w && log.updatedAt ? (MSV.rm === 'LOG' ? `<div class="confirm"><span>Delete the MSRA Log of ${esc(msName())} from the library? This cannot be undone. Download it first with Save as if you may need it.</span><div class="btns"><button type="button" class="btn btn-sm btn-danger-solid" data-ms-act="del-yes">Delete log</button><button type="button" class="btn btn-sm" data-ms-act="rm-no">Cancel</button></div></div>` : '<div><button type="button" class="btn btn-sm btn-ghost btn-danger" data-ms-act="del">Delete this log</button></div>') : ''}
  </div>`;
}
/* the MSL Ref sheet */
function msLinkCount() { const m = new Map(); for (const it of MSV.log.items) for (const k of it.m) m.set(k, (m.get(k) || 0) + 1); return m; }
function msMslHTML() {
  const log = MSV.log, msl = log.msl, e = MSV.mode === 'edit';
  if (!msl) return `<div class="ms-empty"><h3>No Material Submittal Log yet</h3><p>Upload the planner's Material Submittal Log (Excel). The materials are linked to the method statements, so you can see which method statements no material needs, which materials no method statement covers, and fill planned dates from the material dates if you want.</p><div class="btns"><button type="button" class="btn btn-primary" data-ms-act="msl-up">Upload MSL</button></div></div>`;
  const cnt = msLinkCount(), unc = msl.items.filter(r => !cnt.get(r.k)).length;
  const list = msl.items.filter(r => MSV.mslFilter === 'all' || (MSV.mslFilter === 'unc' ? !cnt.get(r.k) : r.d === MSV.mslFilter));
  const titles = new Map(); { const no = {}; for (const d of MS_CODES) { let n = 0; for (const s of ['I', 'T']) for (const it of msItemsOf(log, d, s)) no[it.id] = d + ' ' + (++n); } for (const it of log.items) for (const k of it.m) { if (!titles.has(k)) titles.set(k, []); titles.get(k).push(no[it.id]); } }
  const noMat = log.items.filter(it => !it.m.length).length;
  return `<div class="ms-msl-top">
      <div><p style="margin:0"><b>Source:</b> ${esc(msl.file)}${msl.sheet ? ` (${esc(msl.sheet)})` : ''}, uploaded ${esc(msFmt(msl.uploaded))}. ${msl.items.length} materials, ${msl.items.filter(r => r.date).length} with a planned submission date.</p>
      <p class="hint">${unc ? `<b class="ms-red">${unc} material${unc === 1 ? '' : 's'} not covered</b> by any method statement. ` : 'Every material is covered by a method statement. '}${noMat ? `${noMat} method statement${noMat === 1 ? ' has' : 's have'} no related material.` : ''} Planned submission dates are typed in the logs; you can fill the empty ones from the material dates.</p></div>
      <div class="ms-lags"><label>Installation: days after the first related material <input class="ms-in ms-num" type="number" min="0" max="365" data-lag="lagI" value="${msl.lagI}"${e ? '' : ' disabled'}></label>
        <label>T&C: days after the last related material <input class="ms-in ms-num" type="number" min="0" max="365" data-lag="lagT" value="${msl.lagT}"${e ? '' : ' disabled'}></label>
        <div class="btns"><button type="button" class="btn btn-sm" data-ms-act="fill"${e ? '' : ' disabled title="Switch to Edit first"'}>Fill empty planned dates</button>${e ? '<button type="button" class="btn btn-sm btn-ghost btn-danger" data-ms-act="msl-rm">Remove MSL</button>' : ''}</div></div>
    </div>
    <div class="fgroup ms-msl-f" role="group" aria-label="Show">${[['all', `All ${msl.items.length}`], ['unc', `Not covered ${unc}`]].concat(MS_CODES.filter(d => msl.items.some(r => r.d === d)).map(d => [d, d])).map(([k, l]) => `<button type="button" class="chip" data-ms-f="${k}" aria-pressed="${MSV.mslFilter === k}">${esc(l)}</button>`).join('')}</div>
    <div class="ms-scroll"><table class="ms-msl"><thead><tr><th>MSL Ref</th><th>Discipline</th><th>Planner SN</th><th>Material Item Description (as per Planner's Log)</th><th>Lead Type</th><th>Planned Submission Date (Planner)</th><th>No. of Linked MOS</th><th>Linked Method Statements</th><th>Remarks</th>${e ? '<th></th>' : ''}</tr></thead>
    <tbody>${list.map(r => { const n = cnt.get(r.k) || 0; return `<tr data-k="${esc(r.k)}"${n ? '' : ' class="ms-unc"'}><td class="c">${esc(r.k)}</td><td class="c">${r.d}</td><td class="c">${esc(r.sn)}</td><td>${esc(r.desc)}</td><td class="c">${esc(r.lead)}</td>
      <td class="c">${e ? `<input type="date" class="ms-c${r.date ? '' : ' is-empty'}" data-mk="date" value="${r.date}" aria-label="Planned submission date of ${esc(r.k)}">` : msFmt(r.date)}</td><td class="c${n ? '' : ' ms-zero'}">${n}</td><td>${esc((titles.get(r.k) || []).join(', '))}</td><td>${esc(r.rem)}</td>
      ${e ? `<td class="ms-tools"><button type="button" class="btn btn-sm" data-ms-act="mat-link">Link</button>${n ? '' : '<button type="button" class="btn btn-sm" data-ms-act="mat-add">Add MOS</button>'}</td>` : ''}</tr>`; }).join('') || `<tr class="ms-none"><td colspan="${e ? 10 : 9}">No materials to show</td></tr>`}</tbody></table></div>`;
}
// the title, project block and legends stay in view when the log scrolls sideways
function msFitHead() { const sc = document.querySelector('#ms-body .ms-scroll'); if (sc) sc.style.setProperty('--msw', sc.clientWidth + 'px'); }
function msGrow(t) { t.style.height = 'auto'; t.style.height = Math.min(t.scrollHeight + 2, 400) + 'px'; }

/* ---------- edits ---------- */
const msFind = id => MSV.log.items.find(it => it.id === id);
function msRefreshCounts() {
  const tab = MSV.tab; if (!MS_CODES.includes(tab)) return;
  const c = msCounts(msItemsOf(MSV.log, tab));
  document.querySelectorAll('#ms-body [data-cnt]').forEach(td => { td.textContent = c[td.dataset.cnt]; });
}
function msOnInput(e) {
  const t = e.target, log = MSV.log; if (!log) return;
  if (t.matches('textarea.ms-c')) msGrow(t);
  if (t.type === 'date') t.classList.toggle('is-empty', !t.value);
  if (t.dataset.bl != null) { const r = log.block[+t.dataset.bl]; if (r) { r[t.dataset.f] = t.value; msSetDirty(); } return; }
  if (t.hasAttribute('data-ms-rev')) { log.rev = t.value.trim().slice(0, 10); msSetDirty(); return; }
  if (t.dataset.lag && log.msl) { log.msl[t.dataset.lag] = Math.max(0, Math.min(365, parseInt(t.value, 10) || 0)); msSetDirty(); return; }
  if (t.dataset.mk === 'date') { const k = t.closest('tr').dataset.k, r = log.msl && log.msl.items.find(x => x.k === k); if (r) { r.date = msIso(t.value); msSetDirty(); } return; }
  const k = t.dataset.k, tr = t.closest('tr[data-id]'); if (!k || !tr) return;
  const it = msFind(tr.dataset.id); if (!it) return;
  if (k === 'st' || k === 'fin') { it[k] = msStatus(t.value); t.className = `ms-c ms-stsel st-${msCls(it[k]) || 'none'}`; msRefreshCounts(); }
  else if (k === 'plan' || k === 'sub' || k === 'ret') {
    it[k] = msIso(t.value);
    const rv = tr.querySelector('[data-rv]'); if (rv) rv.textContent = msReview(it);
    const pc = tr.querySelector('[data-k="plan"]'); if (pc) pc.parentElement.className = msDateCls(it).trim();
  } else it[k] = t.value;
  msSetDirty();
}
function msOnChange(e) {
  const t = e.target;
  if (t.dataset.k === 't') { const it = msFind(t.closest('tr').dataset.id); const v = t.value.trim(); if (it && v && /[A-Z]/.test(v) && v === v.toUpperCase()) { it.t = msTitleCase(v); t.value = it.t; msGrow(t); } }
  if (t.dataset.lag) t.value = MSV.log.msl[t.dataset.lag];
}
// the logs show each discipline's installation items, then its T&C items, in list order: a new item goes after the last of its kind
function msAddItem(code, st, title, m) {
  const it = msBlankItem(code, st, title || '', m || []);
  const log = MSV.log, i = log.items.map(o => o.d === code && o.s === st).lastIndexOf(true);
  if (i >= 0) log.items.splice(i + 1, 0, it); else log.items.push(it);
  msSetDirty(); return it;
}
function msMove(id, dir) {
  const log = MSV.log, it = msFind(id); if (!it) return;
  const same = log.items.map((o, i) => [o, i]).filter(([o]) => o.d === it.d && o.s === it.s);
  const p = same.findIndex(([o]) => o === it), q = p + dir; if (q < 0 || q >= same.length) return;
  const a = same[p][1], b = same[q][1]; [log.items[a], log.items[b]] = [log.items[b], log.items[a]];
  msSetDirty(); msRenderBody();
  const btn = document.querySelector(`#ms-body tr[data-id="${id}"] [data-ms-act="${dir < 0 ? 'up' : 'down'}"]`); if (btn && !btn.disabled) btn.focus();
}
async function msOnClick(e) {
  const tab = e.target.closest('[data-ms-tab]'); if (tab) { const was = tab.getAttribute('role') === 'tab'; MSV.tab = tab.dataset.msTab; MSV.rm = null; msRenderBody(); const sel = document.querySelector('#ms-body [role="tab"][aria-selected="true"]'); if (sel && was) sel.focus(); return; }
  const f = e.target.closest('[data-ms-f]'); if (f) { MSV.mslFilter = f.dataset.msF; msRenderBody(); return; }
  const b = e.target.closest('[data-ms-act]'); if (!b || b.disabled) return;
  const act = b.dataset.msAct, tr = b.closest('tr'), log = MSV.log;
  if (act !== 'saveas') { MSV.menu = false; const m = document.querySelector('.ms-saveas .menu'); if (m) m.hidden = true; }
  switch (act) {
    case 'back': return closeMsra();
    case 'start': return msStart(b.dataset.how);
    case 'mode-view': MSV.mode = 'view'; MSV.rm = null; msRenderActions(); return msRenderBody();
    case 'mode-edit': MSV.mode = 'edit'; msRenderActions(); return msRenderBody();
    case 'save': return msSave();
    case 'saveas': MSV.menu = !MSV.menu; { const m = document.querySelector('.ms-saveas .menu'); if (m) { m.hidden = !MSV.menu; b.setAttribute('aria-expanded', MSV.menu); if (MSV.menu) m.querySelector('.menu-item').focus(); } } return;
    case 'save-xlsx': return msRun(b, 'Preparing the Excel file…', msSaveXlsx);
    case 'save-pdf': return msRun(b, 'Preparing the PDF…', () => msSavePdf(false));
    case 'print': return msRun(b, 'Preparing the PDF…', () => msSavePdf(true));
    case 'msl-up': S.msFile = null; $('#file-msl').value = ''; return $('#file-msl').click();
    case 'msl-rm': return msConfirm('Remove the MSL?', 'The material list and every material link are removed from this log. Planned dates stay as they are.', 'Remove MSL', () => { log.msl = null; log.items.forEach(it => { it.m = []; }); MSV.tab = 'MSL'; msSetDirty(); msRenderActions(); msRenderBody(); });
    case 'fill': return msFillDates();
    case 'load-remote': if (MSV.remote) { msLoad(MSV.remote); renderMs(); } return;
    case 'bl-add': if (log.block.length < MS_BLOCK_MAX) { log.block.push({ label: '', value: '' }); msSetDirty(); msRenderBody(); const ins = document.querySelectorAll('#ms-body [data-bl][data-f="label"]'); if (ins.length) ins[ins.length - 1].focus(); } return;
    case 'bl-rm': if (log.block.length > 1) { log.block.splice(+b.dataset.i, 1); msSetDirty(); msRenderBody(); } return;
    case 'bl-reset': log.block = msDefaultBlock(msProj()); msSetDirty(); msRenderBody(); toast('Project block filled from the library'); return;
    case 'add': { const it = msAddItem(MSV.tab, b.dataset.st); msRenderBody(); const ta = document.querySelector(`#ms-body tr[data-id="${it.id}"] textarea[data-k="t"]`); if (ta) { ta.focus(); ta.scrollIntoView({ block: 'nearest' }); } return; }
    case 'up': case 'down': return msMove(tr.dataset.id, act === 'up' ? -1 : 1);
    case 'rm': MSV.rm = tr.dataset.id; msRenderBody(); { const y = document.querySelector('#ms-body [data-ms-act="rm-yes"]'); if (y) y.focus(); } return;
    case 'rm-no': MSV.rm = null; return msRenderBody();
    case 'rm-yes': { const i = log.items.findIndex(it => it.id === MSV.rm); if (i >= 0) { const t = log.items[i].t; log.items.splice(i, 1); msSetDirty(); toast(`Removed: ${t || 'method statement'}`); } MSV.rm = null; return msRenderBody(); }
    case 'del': MSV.rm = 'LOG'; return msRenderBody();
    case 'del-yes': return msDelete();
    case 'mats': return msOpenMats(tr.dataset.id);
    case 'mat-link': return msOpenLink(tr.dataset.k);
    case 'mat-add': return msOpenAddFor(tr.dataset.k);
  }
}
async function msRun(btn, label, fn) {
  if (MSV.busy) return; MSV.busy = 'file'; const old = btn.innerHTML; btn.disabled = true;
  const top = document.querySelector('[data-ms-act="print"]'); toast(label, 60000);
  try { await fn(); } catch (err) { toast('The file could not be made: ' + ((err && err.message) || err), 7000); }
  finally { MSV.busy = ''; btn.disabled = false; btn.innerHTML = old; if (top) top.disabled = false; msRenderActions(); }
}

function msConfirm(title, text, yes, fn) {
  openModal(`<div class="dialog dialog-sm"><div class="dialog-head"><h2>${esc(title)}</h2></div><div class="dialog-body"><p style="margin:0">${esc(text)}</p></div>
    <div class="dialog-foot"><button type="button" class="btn" data-close>Cancel</button><button type="button" class="btn btn-danger-solid" id="ms-cf-yes">${esc(yes)}</button></div></div>`);
  $('#ms-cf-yes').addEventListener('click', () => { closeModal(); fn(); });
}

/* ---------- start, save, delete ---------- */
function msStart(how) {
  const p = msProj();
  MSV.log = msNewLog(p, how === 'empty' ? 'empty' : 'std');
  MSV.base = ''; MSV.dirty = true; MSV.state = 'ready'; MSV.tab = how === 'empty' ? 'MEC' : 'SUM'; MSV.mode = how === 'empty' ? 'edit' : 'view';
  renderMs();
  if (how === 'msl') { $('#file-msl').value = ''; $('#file-msl').click(); }
  toast(how === 'empty' ? 'Empty log started. Add method statements, then Save to library.' : `Log started with ${MSV.log.items.length} method statements. Save to library to keep it.`, 5000);
}
async function msSave() {
  if (!canWrite() || !MSV.log || MSV.busy) return false;
  const log = MSV.log, now = new Date().toISOString();
  const doc = JSON.parse(JSON.stringify({ ...log, no: MSV.no, updatedAt: now, createdAt: log.createdAt || now }));
  const size = new Blob([JSON.stringify(doc)]).size;
  if (size > 245000) { toast('The log is too large to save in the library (' + Math.round(size / 1024) + ' KB). Remove some materials or method statements.', 7000); return false; }
  MSV.busy = 'save'; MSV.savingAt = now; msRenderActions();
  try {
    await DB.collection('mslogs').doc(MSV.no).set(doc);
    log.updatedAt = now; log.createdAt = doc.createdAt;
    await DB.collection('mslogmeta').doc(MSV.no).set({ no: MSV.no, n: log.items.length, updatedAt: now });
    MSV.base = JSON.stringify(log); MSV.dirty = false; MSV.remote = null;
    toast('MSRA Log saved to the library');
    return true;
  } catch (e) { toast(writeError(e), 6000); return false; }
  finally { MSV.busy = ''; msRenderActions(); if (MSV.tab === 'SUM') msRenderBody(); else { const n = $('#ms-body .ms-notice'); if (n && !MSV.remote) n.remove(); } }
}
async function msDelete() {
  if (!canWrite()) return;
  try {
    await DB.collection('mslogs').doc(MSV.no).delete();
    await DB.collection('mslogmeta').doc(MSV.no).delete();
    toast(`The MSRA Log of ${msName()} was deleted`);
    MSV.dirty = false; closeMsra(true);
  } catch (e) { toast(writeError(e), 6000); }
}

/* ---------- MSL upload ---------- */
async function onMslFile(e) {
  const file = e.target.files && e.target.files[0]; if (!file || !MSV.log) return;
  if (file.size > 15e6) { toast('That file is too large (over 15 MB).'); return; }
  let parsed;
  try {
    await loadScript(LIBS.xlsx);
    const wb = XLSX.read(await file.arrayBuffer(), { type: 'array', cellDates: true });
    const hidden = new Set(((wb.Workbook && wb.Workbook.Sheets) || []).filter(s => s.Hidden).map(s => s.name));
    parsed = msParseMsl(wb.SheetNames.filter(n => !hidden.has(n)).map(n => ({ name: n, rows: XLSX.utils.sheet_to_json(wb.Sheets[n], { header: 1, raw: true, defval: '' }) })));
  } catch (err) { toast('The file could not be read: ' + ((err && err.message) || err), 6000); return; }
  if (!parsed.items.length) { toast('No materials found. The MSL needs a "Description" column (one sheet per discipline, or discipline rows such as ELECTRICAL and PLUMBING).', 8000); return; }
  msReviewMsl(file.name, parsed);
}
/* links: standard items get the materials matched to them; other items keep links whose keys still exist */
function msLinkPlan(items, mats) {
  const byStd = new Map(), keys = new Set(mats.map(r => r.k));
  let linked = 0;
  for (const r of mats) { const m = msMatch(r); if (m.idx.length) linked++; for (const i of m.idx) { if (!byStd.has(i)) byStd.set(i, []); byStd.get(i).push(r.k); } }
  const links = new Map(items.map(it => [it.id, it.x != null && MS_STD.items[it.x] ? (byStd.get(it.x) || []) : it.m.filter(k => keys.has(k))]));
  return { links, linked };
}
function msReviewMsl(fileName, parsed) {
  const log = MSV.log, mats = parsed.items;
  const { links, linked } = msLinkPlan(log.items, mats);
  const cover = new Set(); links.forEach(ks => ks.forEach(k => cover.add(k)));
  const unc = mats.filter(r => !cover.has(r.k));
  const unused = log.items.filter(it => !(links.get(it.id) || []).length);
  const dated = mats.filter(r => r.date).length;
  const by = {}; mats.forEach(r => { by[r.d] = (by[r.d] || 0) + 1; });
  openModal(`<div class="dialog">
    <div class="dialog-head"><h2>Use this Material Submittal Log?</h2><button type="button" class="btn btn-ghost btn-sm" data-close>Cancel</button></div>
    <div class="dialog-body">
      <p style="margin:0"><b>${esc(fileName)}</b>: ${mats.length} materials (${esc(Object.entries(by).map(([d, n]) => `${d} ${n}`).join(', '))}) from ${esc(joinAnd(parsed.sheets.map(s => `“${s}”`)))}. ${dated ? `${dated} have a planned submission date.` : 'No planned submission dates found.'}</p>
      <p style="margin:0">${linked} materials are linked to method statements of the standard${unc.length ? `; <b class="ms-red">${unc.length} are not covered</b> (you can add a method statement or link each one in MSL Ref)` : ''}.</p>
      ${unc.length ? `<div class="ms-unc-list">${unc.slice(0, 40).map(r => `<span class="tag">${esc(r.k)} ${esc(r.desc)}</span>`).join('')}${unc.length > 40 ? `<span class="tag">+${unc.length - 40} more</span>` : ''}</div>` : ''}
      ${unused.length ? `<label class="ms-check"><input type="checkbox" id="msl-rmunused"><span>Remove the ${unused.length} method statement${unused.length === 1 ? '' : 's'} that no material in this MSL needs<small>${esc(unused.slice(0, 8).map(it => it.t).join('; '))}${unused.length > 8 ? '; …' : ''}</small></span></label>` : ''}
      ${dated ? `<label class="ms-check"><input type="checkbox" id="msl-fill"><span>Fill empty planned submission dates from the material dates<small>Installation: ${log.msl ? log.msl.lagI : 14} days after the first related material; T&C: ${log.msl ? log.msl.lagT : 14} days after the last. Sundays move to Monday. Dates you typed stay.</small></span></label>` : ''}
      ${parsed.items.some(r => r.rem) ? `<p class="d-note" style="margin:0">${parsed.items.filter(r => /No SN|repeated/.test(r.rem || '')).length ? 'Materials without a planner SN got the next free number in their discipline. ' : ''}${parsed.items.filter(r => /Discipline not found/.test(r.rem || '')).length ? 'Materials whose discipline was not found are under MEP: check them in MSL Ref.' : ''}</p>` : ''}
    </div>
    <div class="dialog-foot"><button type="button" class="btn" data-close>Cancel</button><button type="button" class="btn btn-primary" id="msl-go">Use this MSL</button></div>
  </div>`);
  $('#msl-go').addEventListener('click', () => {
    const rmUnused = $('#msl-rmunused') && $('#msl-rmunused').checked, fill = $('#msl-fill') && $('#msl-fill').checked;
    log.msl = { file: fileName.slice(0, 200), sheet: parsed.sheets.join(', ').slice(0, 200), uploaded: msFromDay(msToday()), lagI: log.msl ? log.msl.lagI : 14, lagT: log.msl ? log.msl.lagT : 14, items: mats.map(r => ({ k: r.k, d: r.d, sn: r.sn, desc: r.desc.slice(0, 300), lead: r.lead.slice(0, 40), date: r.date, rem: (r.rem || '').slice(0, 200) })) };
    log.items.forEach(it => { it.m = links.get(it.id) || []; });
    if (rmUnused) log.items = log.items.filter(it => it.m.length);
    let filled = 0; if (fill) filled = msFill();
    msSetDirty(); closeModal(); MSV.tab = 'MSL'; renderMs();
    toast(`MSL linked: ${mats.length} materials${rmUnused ? `, ${unused.length} method statements removed` : ''}${fill ? `, ${filled} planned dates filled` : ''}.`, 6000);
  });
}
function msFill() {
  const log = MSV.log, msl = log.msl; if (!msl) return 0;
  const dates = new Map(msl.items.filter(r => r.date).map(r => [r.k, msDay(r.date)]));
  let n = 0;
  for (const it of log.items) {
    if (it.plan) continue;
    const ds = it.m.map(k => dates.get(k)).filter(v => v != null); if (!ds.length) continue;
    let d = it.s === 'T' ? Math.max(...ds) + msl.lagT : Math.min(...ds) + msl.lagI;
    if (new Date(d * 86400000).getUTCDay() === 0) d += 1;
    it.plan = msFromDay(d); n++;
  }
  return n;
}
function msFillDates() {
  const n = msFill();
  if (n) { msSetDirty(); msRenderBody(); toast(`${n} planned submission date${n === 1 ? '' : 's'} filled from the MSL`); }
  else toast('No empty planned date could be filled: the related materials have no dates, or every planned date is typed already.', 6000);
}

/* ---------- material links ---------- */
function msMatList(selected, focusD) {
  const msl = MSV.log.msl, order = [focusD].concat(MS_CODES.filter(c => c !== focusD));
  return order.filter(d => msl.items.some(r => r.d === d)).map(d => `<fieldset class="ms-fs"><legend>${esc(MS_DNAME[d])}</legend>${msl.items.filter(r => r.d === d).map(r => `<label class="ms-check-row" data-q="${esc((r.k + ' ' + r.desc).toLowerCase())}"><input type="checkbox" value="${esc(r.k)}"${selected.has(r.k) ? ' checked' : ''}> <b>${esc(r.k)}</b> ${esc(r.desc)}</label>`).join('')}</fieldset>`).join('');
}
function msFilterBox(id) { return `<input class="inp" type="search" id="${id}" placeholder="Filter…" autocomplete="off">`; }
function msBindFilter(id, sel) { $('#' + id).addEventListener('input', ev => { const q = ev.target.value.trim().toLowerCase(); document.querySelectorAll(sel).forEach(l => { l.hidden = !!q && !l.dataset.q.includes(q); }); }); }
function msOpenMats(id) {
  const it = msFind(id); if (!it || !MSV.log.msl) return;
  openModal(`<div class="dialog">
    <div class="dialog-head"><h2>Related materials</h2><button type="button" class="btn btn-ghost btn-sm" data-close>Cancel</button></div>
    <div class="dialog-body"><p style="margin:0"><b>${esc(it.d)}</b> · ${esc(it.t || 'Untitled method statement')}</p>${msFilterBox('ms-mf')}<div class="ms-checks" id="ms-mats">${msMatList(new Set(it.m), it.d)}</div></div>
    <div class="dialog-foot"><button type="button" class="btn" data-close>Cancel</button><button type="button" class="btn btn-primary" id="ms-mats-ok">Done</button></div></div>`);
  msBindFilter('ms-mf', '#ms-mats .ms-check-row');
  $('#ms-mats-ok').addEventListener('click', () => { it.m = [...document.querySelectorAll('#ms-mats input:checked')].map(c => c.value); msSetDirty(); closeModal(); msRenderBody(); });
}
function msOpenLink(k) {
  const log = MSV.log, r = log.msl && log.msl.items.find(x => x.k === k); if (!r) return;
  const order = [r.d].concat(MS_CODES.filter(c => c !== r.d));
  const groups = order.filter(d => msItemsOf(log, d).length).map(d => { let n = 0; return `<fieldset class="ms-fs"><legend>${esc(MS_DNAME[d])}</legend>${['I', 'T'].map(s => msItemsOf(log, d, s).map(it => `<label class="ms-check-row" data-q="${esc((d + ' ' + it.t).toLowerCase())}"><input type="checkbox" value="${it.id}"${it.m.includes(k) ? ' checked' : ''}> <b>${++n}</b> ${esc(it.t || 'Untitled')} <small>${s === 'I' ? 'Installation' : 'T&C'}</small></label>`).join('')).join('')}</fieldset>`; }).join('');
  openModal(`<div class="dialog">
    <div class="dialog-head"><h2>Link ${esc(k)}</h2><button type="button" class="btn btn-ghost btn-sm" data-close>Cancel</button></div>
    <div class="dialog-body"><p style="margin:0">${esc(r.desc)}: tick the method statements that cover this material.</p>${msFilterBox('ms-lf')}<div class="ms-checks" id="ms-link">${groups || '<p class="hint">The log has no method statements yet.</p>'}</div></div>
    <div class="dialog-foot"><button type="button" class="btn" data-close>Cancel</button><button type="button" class="btn btn-primary" id="ms-link-ok">Done</button></div></div>`);
  msBindFilter('ms-lf', '#ms-link .ms-check-row');
  $('#ms-link-ok').addEventListener('click', () => {
    const on = new Set([...document.querySelectorAll('#ms-link input:checked')].map(c => c.value));
    for (const it of log.items) { const has = it.m.includes(k); if (on.has(it.id) && !has) it.m.push(k); else if (!on.has(it.id) && has) it.m = it.m.filter(x => x !== k); }
    msSetDirty(); closeModal(); msRenderBody();
  });
}
function msOpenAddFor(k) {
  const log = MSV.log, r = log.msl && log.msl.items.find(x => x.k === k); if (!r) return;
  const name = msTitleCase(r.desc.replace(/\(\s*by client\s*\)/i, '').trim());
  openModal(`<div class="dialog dialog-sm">
    <div class="dialog-head"><h2>Add a method statement</h2><button type="button" class="btn btn-ghost btn-sm" data-close>Cancel</button></div>
    <div class="dialog-body"><p style="margin:0">For <b>${esc(k)}</b> ${esc(r.desc)}</p>
      <label class="field"><span class="flabel">Discipline log</span><select class="sel" id="ms-a-d">${MS_DISC.map(d => `<option value="${d.code}"${d.code === r.d ? ' selected' : ''}>${esc(d.code + ' · ' + d.name)}</option>`).join('')}</select></label>
      <label class="field"><span class="flabel">Installation method statement</span><input class="inp" id="ms-a-i" value="${esc('Installation of ' + name)}" maxlength="400"></label>
      <label class="ms-check"><input type="checkbox" id="ms-a-tc"><span>Also add a testing & commissioning method statement</span></label>
      <label class="field"><span class="flabel">T&C method statement</span><input class="inp" id="ms-a-t" value="${esc('Testing & Commissioning of ' + name)}" maxlength="400"></label>
    </div>
    <div class="dialog-foot"><button type="button" class="btn" data-close>Cancel</button><button type="button" class="btn btn-primary" id="ms-a-ok">Add</button></div></div>`);
  $('#ms-a-ok').addEventListener('click', () => {
    const d = $('#ms-a-d').value, ti = $('#ms-a-i').value.trim(), tt = $('#ms-a-t').value.trim();
    if (ti) msAddItem(d, 'I', ti, [k]);
    if ($('#ms-a-tc').checked && tt) msAddItem(d, 'T', tt, [k]);
    closeModal(); msRenderBody(); toast(`Added to the ${d} log`);
  });
}

function bindMsra() {
  const v = $('#view-msra');
  v.addEventListener('click', msOnClick);
  v.addEventListener('input', msOnInput);
  v.addEventListener('change', msOnChange);
  v.addEventListener('keydown', e => {
    if (e.key === 'Escape' && MSV.menu) { e.stopPropagation(); MSV.menu = false; const m = document.querySelector('.ms-saveas .menu'); if (m) m.hidden = true; const b = document.querySelector('[data-ms-act="saveas"]'); if (b) { b.setAttribute('aria-expanded', 'false'); b.focus(); } return; }
    const tab = e.target.closest('[role="tab"]');
    if (tab && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')) {
      const all = [...document.querySelectorAll('#ms-body [role="tab"]')], i = all.indexOf(tab), n = all[(i + (e.key === 'ArrowRight' ? 1 : -1) + all.length) % all.length];
      e.preventDefault(); n.click(); const s = document.querySelector(`#ms-body [data-ms-tab="${n.dataset.msTab}"]`); if (s) s.focus();
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's' && S.view === 'msra') { e.preventDefault(); if (MSV.dirty && canWrite()) msSave(); }
  });
  document.addEventListener('click', e => { if (MSV.menu && !e.target.closest('.ms-saveas')) { MSV.menu = false; const m = document.querySelector('.ms-saveas .menu'); if (m) m.hidden = true; } });
  $('#file-msl').addEventListener('change', onMslFile);
  window.addEventListener('resize', () => { if (S.view === 'msra') msFitHead(); });
}
