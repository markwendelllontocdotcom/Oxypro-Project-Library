/* ---------- WIR, MIR, NCR and SOR Log pages (QA/QC menu), made the way the MSRA Log is ---------- */
const RLV = { kind: 'wir', no: null, log: null, dirty: false, tab: 'SUM', mode: 'view', state: 'idle', err: '', remote: null, unsub: null, rm: null, busy: '', day: '', parts: 0, savingAt: '', pg: 0 };
const rlK = () => RL_KIND[RLV.kind];
const rlProj = () => S.projects.get(RLV.no) || { no: RLV.no, name: '' };
const rlName = () => { const p = rlProj(); return `${p.no} ${p.name || ''}`.trim(); };
const rlFileBase = () => { const p = rlProj(); return safeName([p.code || p.no, p.name || 'Untitled project', rlK().file, 'Rev ' + ((RLV.log && RLV.log.rev) || '00')].join(' - ')); };
const rlCol = s => RLV.kind + s;   // wirlogs, wirlogparts, wirlogmeta and the same for mir, ncr and sor
const rlNc = () => rlIsNc(RLV.kind);
const rlAllow = () => (RLV.log && RLV.log.allow != null ? RLV.log.allow : RL_NC_ALLOW);
const rlCnt = list => rlCounts(list, RLV.kind, rlAllow());
const rlNLogs = () => rlNc() ? 'eight' : 'seven';

function rlMenuItemsHTML(p) {
  return RL_KINDS.map(k => {
    const K = RL_KIND[k], has = S.rlMeta && S.rlMeta[k] && S.rlMeta[k].has(p.no);
    return `<button type="button" class="menu-item" role="menuitem" data-act="${k}log"><span><b>${has ? 'Open' : 'Create'} ${K.name}</b><small>${has ? 'This project\'s' : 'Standard'} ${esc(K.long)} log${has ? '' : ' for this project'}</small></span></button>`;
  }).join('');
}
function rlSetDirty() { if (!RLV.dirty) { RLV.dirty = true; rlRenderActions(); } }
function rlCloseSub() { if (RLV.unsub) { try { RLV.unsub(); } catch (e) { /* gone */ } RLV.unsub = null; } }

// a saved log: the head in <kind>logs/<project no.>, the rows in parts <kind>logparts/<project no.>_<n>
async function rlFetch(x, no) {
  const n = Math.max(0, Math.min(200, +x.parts || 0)), items = [];
  for (let tries = 0; ; tries++) {
    items.length = 0; let ok = true;
    for (let i = 0; i < n; i++) {
      const s = await DB.collection(rlCol('logparts')).doc(no + '_' + i).get(), d = s.exists ? s.data() : null;
      if (!d || d.at !== x.updatedAt) { ok = false; break; }
      items.push(...(d.items || []));
    }
    if (ok || tries >= 3) break;
    await new Promise(r => setTimeout(r, 700));     // another editor is in the middle of saving
  }
  return { ...x, items };
}
function openRlog(kind, no) {
  const p = S.projects.get(no); if (!p || !RL_KIND[kind]) return;
  rlCloseSub();
  Object.assign(RLV, { kind, no, log: null, dirty: false, tab: 'SUM', mode: 'view', state: 'loading', err: '', remote: null, rm: null, busy: '', day: msFromDay(msToday()), parts: 0, savingAt: '', pg: 0 });
  S.view = 'rlog'; S.detailOpen = false;
  $('#view-library').hidden = true; $('#view-rlog').hidden = false; renderSelbar(); renderDetail();
  window.scrollTo(0, 0);
  renderRl();
  if (!DB) { RLV.state = 'new'; renderRl(); return; }
  let first = true;
  const mine = () => RLV.no === no && RLV.kind === kind && S.view === 'rlog';
  RLV.unsub = DB.collection(rlCol('logs')).doc(no).onSnapshot(async snap => {
    if (!mine()) return;
    const x = snap.exists ? snap.data() : null;
    if (first) {
      first = false;
      if (!x) { RLV.state = 'new'; return renderRl(); }
      try { const full = await rlFetch(x, no); if (!mine()) return; rlLoad(full); } catch (e) { if (!mine()) return; RLV.state = 'error'; RLV.err = (e && e.code) || ''; }
      return renderRl();
    }
    if (!x) { if (RLV.state === 'ready' && !RLV.dirty) { RLV.state = 'new'; RLV.log = null; renderRl(); toast(`This ${rlK().name} was deleted by another editor.`); } return; }
    if (x.updatedAt && ((RLV.log && x.updatedAt === RLV.log.updatedAt) || x.updatedAt === RLV.savingAt)) return;    // our own save
    let full; try { full = await rlFetch(x, no); } catch (e) { return; }
    if (!mine()) return;
    if (!RLV.log || !RLV.dirty) { rlLoad(full); renderRl(); toast(`The ${rlK().name} was updated by another editor.`); }
    else { RLV.remote = full; rlRenderBody(); }
  }, err => { if (!mine()) return; RLV.state = 'error'; RLV.err = (err && err.code) || ''; renderRl(); });
}
function rlLoad(x) { RLV.log = rlClean(RLV.kind, x, rlProj()); RLV.parts = +x.parts || 0; RLV.dirty = false; RLV.remote = null; RLV.state = 'ready'; }
function closeRlog(force) {
  if (!force && RLV.dirty) return rlAskLeave();
  rlCloseSub(); RLV.no = null; RLV.log = null; RLV.dirty = false;
  S.view = 'library'; $('#view-rlog').hidden = true; $('#view-library').hidden = false;
  renderAll(); window.scrollTo(0, 0);
}
function rlAskLeave() {
  const w = msCanSave(), n = rlK().name;
  openModal(`<div class="dialog dialog-sm">
    <div class="dialog-head"><h2>Unsaved changes</h2></div>
    <div class="dialog-body"><p style="margin:0">${w ? `Save the changes to this ${n} in ${MS_WHERE} before going back to the library?` : `Your changes to this ${n} are not saved in the library (only editors can save). Download it with Save as Excel first if you need it.`}</p></div>
    <div class="dialog-foot"><button type="button" class="btn" data-close>Stay here</button><button type="button" class="btn${w ? '' : ' btn-primary'}" id="rl-leave-discard">Discard changes</button>${w ? '<button type="button" class="btn btn-primary" id="rl-leave-save">Save and go back</button>' : ''}</div>
  </div>`);
  $('#rl-leave-discard').addEventListener('click', () => { closeModal(); closeRlog(true); });
  if (w) $('#rl-leave-save').addEventListener('click', async () => { closeModal(); if (await rlSave()) closeRlog(true); });
}

/* ---------- rendering ---------- */
function renderRl() {
  const p = rlProj();
  $('#rl-title').textContent = rlK().name;
  $('#view-rlog').setAttribute('aria-label', rlK().name);
  $('#rl-proj').textContent = `${p.no}${p.name ? ' · ' + p.name : ''}`;
  rlRenderActions(); rlRenderBody();
}
function rlRenderActions() {
  const el = $('#rl-actions'); if (!el) return;
  if (RLV.state !== 'ready') { el.innerHTML = ''; return; }
  const w = msCanSave(), e = RLV.mode === 'edit';
  el.innerHTML = `<div class="seg" role="group" aria-label="Mode"><button type="button" aria-pressed="${!e}" data-rl-act="mode-view">View</button><button type="button" aria-pressed="${e}" data-rl-act="mode-edit">Edit</button></div>
    <button type="button" class="btn" data-rl-act="save-xlsx" title="The standard ${rlK().name} workbook with this log filled in: Summary, the ${rlNLogs()} discipline logs, the Transmittal Sheet and the hidden guide sheets">Save as Excel</button>
    ${w ? `<button type="button" class="btn${RLV.dirty ? ' btn-primary' : ''}" data-rl-act="save"${RLV.dirty && !RLV.busy ? '' : ' disabled'}>${RLV.busy === 'save' ? 'Saving…' : RLV.dirty ? (GH ? 'Save in browser' : 'Save to library') : 'Saved'}</button>` : ''}`;
}
function rlRenderBody() {
  const el = $('#rl-body'); if (!el) return;
  const same = RLV.shown === RLV.kind + RLV.tab + RLV.mode, keep = same && el.querySelector('.ms-scroll'), sx = keep ? keep.scrollLeft : 0, sy = keep ? keep.scrollTop : 0;
  RLV.shown = RLV.kind + RLV.tab + RLV.mode;
  const K = rlK();
  if (RLV.state === 'loading') { el.innerHTML = `<div class="ms-empty"><p>Loading the ${K.name}…</p></div>`; return; }
  if (RLV.state === 'error') { el.innerHTML = `<div class="ms-empty"><h3>The ${K.name} could not be loaded</h3><p>${esc(RLV.err === 'revoked' ? 'Your access to the library changed. Reload the page.' : 'Check your connection and open it again.')}</p></div>`; return; }
  if (RLV.state === 'new') { el.innerHTML = rlStartHTML(); return; }
  const log = RLV.log;
  const tabs = [['SUM', 'Summary', log.items.length]].concat(rlDiscs(RLV.kind).map(d => [d.code, d.code, rlItemsOf(log, d.code).length])).concat([['TRN', 'Transmittal', '']]);
  el.innerHTML = `${rlNoticeHTML()}
    <div class="ms-tabs" role="tablist" aria-label="Log sheets">${tabs.map(([k, l, c]) => `<button type="button" role="tab" aria-selected="${RLV.tab === k}" data-rl-tab="${k}" title="${esc(k === 'SUM' ? 'Summary' : k === 'TRN' ? 'Transmittal Sheet: the ' + K.items + (K.nc ? ' closed out on a day' : ' submitted on a day') : (rlDiscs(RLV.kind).find(d => d.code === k) || {}).head)}">${esc(l)}${c !== '' ? `<span class="n">${c}</span>` : ''}</button>`).join('')}</div>
    <div class="ms-panel ${RLV.mode === 'edit' ? 'editing' : ''}" role="tabpanel">${RLV.tab === 'SUM' ? rlSummaryHTML() : RLV.tab === 'TRN' ? rlTransHTML() : rlSheetHTML(RLV.tab)}</div>`;
  const sc = el.querySelector('.ms-scroll'); if (sc && keep) { sc.scrollLeft = sx; sc.scrollTop = sy; }
  el.querySelectorAll('textarea.ms-c').forEach(msGrow);
}
function rlNoticeHTML() {
  if (RLV.remote) return `<div class="ms-notice"><span>Another editor saved this log${RLV.remote.updatedAt ? ' at ' + esc(new Date(RLV.remote.updatedAt).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })) : ''}. Saving now replaces their version with yours.</span><button type="button" class="btn btn-sm" data-rl-act="load-remote">Load their version</button></div>`;
  if (!msCanSave() && RLV.dirty) return `<div class="ms-notice"><span>Only the library's editors can save. Use Save as Excel to keep your changes in a file.</span></div>`;
  return '';
}
function rlStartHTML() {
  const K = rlK(), w = msCanSave();
  return `<div class="ms-start">
    <h3>Create the ${esc(K.name)} for ${esc(rlName())}</h3>
    <p class="hint">The log follows the Oxypro standard ${esc(K.name)} workbook: Summary, ${rlNLogs()} discipline logs (HVAC, Plumbing, Electrical, ELV, Fire Fighting, LPG${K.nc ? ', MEP and HSE' : ' and MEP'}), the Transmittal Sheet and the hidden guide sheets. The project bar and block are filled from the library and you can edit them. Save as Excel gives the standard workbook with this log filled in.</p>
    <div class="ms-start-cards">
      <button type="button" class="ms-start-card" data-rl-act="start" data-rec="1"><span class="ms-sc-t">Start the ${esc(K.name)}<span class="tag tag-rec">Standard</span></span><span class="ms-sc-d">Starts empty. Add each ${esc(K.item)} to its discipline log as it is raised; the reference numbers follow ${esc(rlRefParts(rlDefaultPat(RLV.kind, rlProj()), 'MEC').pre)}${K.nc ? '001' : '0001'} and can be changed.</span></button>
    </div>
    ${GH ? '<p class="hint">GitHub edition: the log is saved in this browser on this device. Use Save as Excel to keep or share it.</p>' : w ? '' : '<p class="hint">Only the library\'s editors can save the log to the library. You can still make it and download it with Save as Excel.</p>'}
  </div>`;
}

/* the sheet, on the workbook's own columns A to N */
const RL_PAGE = 50;
// the WIR sheet has columns A to N; the MIR sheet has no Level and no Location (user, 21 Nov 2026), so A to L with a wider Reference No.
const rlLL = () => !!RL_LAY[RLV.kind].lvl;   // Level and Location columns
// the NCR and SOR sheets have A to N: description in E, then eight columns of dates, days and statuses
const rlW = () => rlNc() ? [45, 89, 205, 80, 500, 115, 115, 115, 115, 115, 115, 115, 115, 245] : rlLL() ? [45, 89, 150, 80, 80, 150, 500, 115, 115, 115, 115, 115, 115, 245] : [45, 89, 205, 80, 500, 115, 115, 115, 115, 115, 115, 245];
const rlNC = () => rlW().length;
const rlColsHTML = extra => `<colgroup>${rlW().concat(extra || []).map(w => `<col style="width:${w}px">`).join('')}</colgroup>`;
// the head of an NCR / SOR sheet, as rows 1 to 9 of the workbook
function rlNcHeadHTML(disc, title2, c, dateCell) {
  const log = RLV.log, e = RLV.mode === 'edit', p = rlProj(), names = msLogoNames(p), K = rlK();
  const proj = e ? `<input class="ms-in ms-in-proj" data-rl-bl="title" value="${esc(log.block.title)}" aria-label="Project" maxlength="400">` : esc(log.block.title);
  const legend = i => { const [k, t] = K.legend[i]; return `<td class="t-code st-${k}">${k}</td><td colspan="2" class="t-desc">${esc(t)}</td>`; };
  const block = i => {
    const [k, label] = RL_BLOCK[i];
    return `<td colspan="2" class="t-lab">${label}</td><td colspan="2" class="t-val">${e ? `<span class="t-ed">:<input class="ms-in" data-rl-bl="${k}" value="${esc(log.block[k])}" aria-label="${label}" maxlength="400"></span>` : ': ' + esc(log.block[k])}</td>`;
  };
  const logo = k => { const lg = names[k] && logoOf(names[k]); return lg ? `<img src="${esc(logoUrl(lg.id))}" alt="${esc(names[k])} logo">` : ''; };
  const rows = [
    `<tr><td colspan="14" class="t-proj">${proj}</td></tr>`,
    `<tr>${block(0)}<td class="t-ll l"><div class="rl-pair rl-pair-lab"><span>Client</span><span>Consultant</span></div></td><td colspan="3" class="t-ll">Main Contractor</td><td colspan="3" class="t-ll r">Subcontractor</td><td colspan="3" class="t-legh">LEGENDS</td></tr>`,
    `<tr>${block(1)}<td rowspan="3" class="t-logo l"><div class="rl-pair"><span>${logo('client')}</span><span>${logo('consultant')}</span></div></td><td colspan="3" rowspan="3" class="t-logo">${logo('contractor')}</td><td colspan="3" rowspan="3" class="t-logo r"><img src="${MS_LOGO}" alt="Oxypro Electromechanical Works LLC"></td>${legend(0)}</tr>`,
    `<tr>${block(2)}${legend(1)}</tr>`, `<tr>${block(3)}${legend(2)}</tr>`,
    `<tr>${block(4)}<td colspan="7" class="t-title rl-big">${esc(title2)}</td>${legend(3)}</tr>`,
    `<tr class="t-gap"><td colspan="14"></td></tr>`,
    `<tr><td class="t-date l rl-dt"></td><td class="t-date r rl-dt"></td><td colspan="6" rowspan="2" class="t-title">${esc(disc)}</td><th class="t-sh">STATUS</th>${RL_NC_STATUS.map(k => `<td class="t-sh st-${k}">${k}</td>`).join('')}<th class="t-sh">TOTAL</th></tr>`,
    `<tr><td class="t-date l rl-db">Date:</td><td class="t-date r rl-db">${dateCell}</td><th class="t-sh">QUANTITY</th>${RL_NC_STATUS.map(k => `<td class="t-sh" data-cnt="${k}">${c[k]}</td>`).join('')}<td class="t-sh" data-cnt="sub">${c.sub}</td></tr>`
  ];
  return `<table class="ms-top rl-top rl-nc" style="width:${rlW().reduce((a, b) => a + b, 0)}px">${rlColsHTML()}<tbody>${rows.join('')}</tbody></table>`;
}
function rlHeadHTML(disc, title2, c, dateCell) {
  if (rlNc()) return rlNcHeadHTML(disc, title2, c, dateCell);
  const log = RLV.log, e = RLV.mode === 'edit', p = rlProj(), names = msLogoNames(p);
  const proj = e ? `<input class="ms-in ms-in-proj" data-rl-bl="title" value="${esc(log.block.title)}" aria-label="Project" maxlength="400">` : esc(log.block.title);
  const legend = i => { const [k, t] = MS_LEGEND[i]; return `<td class="t-code st-${msCls(k)}">${k}</td><td colspan="2" class="t-desc">${t}</td>`; };
  const block = i => {
    const [k, label] = RL_BLOCK[i];
    return `<td colspan="2" class="t-lab">${label}</td><td colspan="${rlNC() - 10}" class="t-val">${e ? `<span class="t-ed">:<input class="ms-in" data-rl-bl="${k}" value="${esc(log.block[k])}" aria-label="${label}" maxlength="400"></span>` : ': ' + esc(log.block[k])}</td>`;
  };
  const logo = k => { const lg = names[k] && logoOf(names[k]); return lg ? `<img src="${esc(logoUrl(lg.id))}" alt="${esc(names[k])} logo">` : ''; };
  const rows = [
    `<tr><td colspan="${rlNC() - 3}" class="t-proj">${proj}</td><td colspan="3" class="t-legh">LEGENDS</td></tr>`,
    `<tr>${block(0)}<td class="t-ll l">Client | Consultant</td><td colspan="2" class="t-ll">Main Contractor</td><td colspan="2" class="t-ll r">Subcontractor</td>${legend(0)}</tr>`,
    `<tr>${block(1)}<td rowspan="3" class="t-logo l"><div class="rl-pair"><span>${logo('client')}</span><span>${logo('consultant')}</span></div></td><td colspan="2" rowspan="3" class="t-logo">${logo('contractor')}</td><td colspan="2" rowspan="3" class="t-logo r"><img src="${MS_LOGO}" alt="Oxypro Electromechanical Works LLC"></td>${legend(1)}</tr>`,
    `<tr>${block(2)}${legend(2)}</tr>`, `<tr>${block(3)}${legend(3)}</tr>`,
    `<tr>${block(4)}<td colspan="5" rowspan="2" class="t-title rl-big">${esc(title2)}</td>${legend(4)}</tr>`,
    `<tr><td colspan="2" class="t-lab"></td><td colspan="${rlNC() - 10}" class="t-val"></td>${legend(5)}</tr>`,
    `<tr class="t-gap"><td colspan="${rlNC()}"></td></tr>`,
    `<tr><td class="t-date l rl-dt"></td><td class="t-date r rl-dt"></td><td colspan="${rlNC() - 10}" rowspan="2" class="t-title">${esc(disc)}</td><td rowspan="2" class="t-title">${esc(title2)}</td>${MS_COUNTED.map(k => `<td class="t-sh st-${msCls(k)}">${k}</td>`).join('')}<th class="t-sh">TOTAL</th></tr>`,
    `<tr><td class="t-date l rl-db">Date:</td><td class="t-date r rl-db">${dateCell}</td>${MS_COUNTED.map(k => `<td class="t-sh" data-cnt="${k}">${c[k]}</td>`).join('')}<td class="t-sh" data-cnt="sub">${c.sub}</td></tr>`
  ];
  return `<table class="ms-top rl-top" style="width:${rlW().reduce((a, b) => a + b, 0)}px">${rlColsHTML()}<tbody>${rows.join('')}</tbody></table>`;
}
const RL_NC_HEAD = ['Received Date', 'Target\nClose-out Date', 'Close-out Date', 'Close-out\nElapsed Days', 'Consultant Response Date', 'Consultant\'s Response\nElapsed Days'];
const rlHeadCells = () => { const K = rlK(); if (K.nc) return ['SN', 'Discipline', 'Reference No.', 'Rev. No.', K.desc].concat(RL_NC_HEAD, ['Status', 'Final Status', 'Remark']); return ['SN', 'Discipline', 'Reference No.', 'Rev. No.'].concat(rlLL() ? ['Level', K.loc] : []).concat([K.desc, 'Planned Submission Date', 'Submitted Date', 'Returned Date', 'Review Period\n(in days)', 'Status', 'Final Status', 'Remark']); };
const rlTheadHTML = e => `<thead><tr>${rlHeadCells().map((l, i) => `<th${i < 3 ? ` class="rf${i + 1}"` : ''}>${esc(l).replace(/\n/g, '<br>')}</th>`).join('')}${e ? '<th class="ms-tools-h">Edit</th>' : ''}</tr></thead>`;
// NCR / SOR: the target date is red when it has passed and the report is still OPEN or to be RESUBMITted (the Summary's Overdue)
const rlNcOver = it => { const tg = msDay(rlTarget(it, rlAllow())); return tg != null && tg < msToday() && (it.fin === 'OPEN' || it.fin === 'RESUBMIT') ? ' ms-od' : ''; };
const rlNcSelect = (k, it) => `<select class="ms-c ms-stsel st-${it[k] || 'none'}" data-k="${k}" aria-label="${k === 'st' ? 'Status' : 'Final status'}"><option value=""></option>${RL_NC_STATUS.map(s => `<option${it[k] === s ? ' selected' : ''}>${s}</option>`).join('')}</select>`;
const rlRowTools = (it, idx, list, K) => RLV.rm === it.id
  ? `<span class="ms-rmq">Remove?</span><button type="button" class="btn btn-sm btn-danger-solid" data-rl-act="rm-yes">Remove</button><button type="button" class="btn btn-sm" data-rl-act="rm-no">Keep</button>`
  : `<button type="button" class="ms-ib" data-rl-act="up" title="Move up" aria-label="Move up"${idx === 0 ? ' disabled' : ''}>${MS_ICON.up}</button><button type="button" class="ms-ib" data-rl-act="down" title="Move down" aria-label="Move down"${idx === list.length - 1 ? ' disabled' : ''}>${MS_ICON.down}</button><button type="button" class="ms-ib" data-rl-act="dup" title="Add a copy below (next reference number)" aria-label="Add a copy below">+</button><button type="button" class="ms-ib ms-rm" data-rl-act="rm" title="Remove this ${K.item}" aria-label="Remove">${MS_ICON.x}</button>`;
function rlNcRowHTML(it, no, idx, list, ro) {
  const e = RLV.mode === 'edit' && !ro, K = rlK(), tg = msFmt(rlTarget(it, rlAllow())), el = rlElapsed(it), rd = rlRespDays(it);
  if (!e) {
    return `<tr data-id="${it.id}"><td class="c rf1">${no}</td><td class="c rf2">${it.d}</td><td class="c rf3">${esc(it.ref)}</td><td class="c">${esc(it.rev)}</td><td class="rl-desc">${esc(it.desc)}</td>
      <td class="c">${msFmt(it.rec)}</td><td class="c${rlNcOver(it)}">${tg}</td><td class="c">${msFmt(it.close)}</td><td class="c">${el}</td><td class="c">${msFmt(it.resp)}</td><td class="c">${rd}</td>
      <td class="c st-${it.st || 'none'}">${esc(it.st)}</td><td class="c st-${it.fin || 'none'}">${esc(it.fin)}</td><td>${esc(it.rem)}</td></tr>`;
  }
  const dt = (k, label) => `<td><input type="date" class="ms-c${it[k] ? '' : ' is-empty'}" data-k="${k}" value="${it[k]}" aria-label="${label}"></td>`;
  return `<tr data-id="${it.id}"><td class="c rf1">${no}</td><td class="c rf2">${it.d}</td>
    <td class="rf3"><input class="ms-c c" data-k="ref" value="${esc(it.ref)}" aria-label="Reference no." maxlength="120"></td>
    <td><input class="ms-c c" data-k="rev" value="${esc(it.rev)}" aria-label="Revision" maxlength="10"></td>
    <td><textarea class="ms-c" data-k="desc" rows="1" aria-label="${esc(K.desc)}" maxlength="600" placeholder="${esc(K.descPh)}">${esc(it.desc)}</textarea></td>
    ${dt('rec', 'Received date')}<td class="c${rlNcOver(it)}" data-tg>${tg}</td>${dt('close', 'Close-out date')}<td class="c" data-el>${el}</td>${dt('resp', 'Consultant response date')}<td class="c" data-rd>${rd}</td>
    <td class="c">${rlNcSelect('st', it)}</td><td class="c">${rlNcSelect('fin', it)}</td>
    <td><textarea class="ms-c" data-k="rem" rows="1" aria-label="Remark" maxlength="400">${esc(it.rem)}</textarea></td>
    <td class="ms-tools">${rlRowTools(it, idx, list, K)}</td></tr>`;
}
function rlRowHTML(it, no, idx, list, ro) {
  if (rlNc()) return rlNcRowHTML(it, no, idx, list, ro);
  const e = RLV.mode === 'edit' && !ro, rv = msReview(it), K = rlK();
  if (!e) {
    return `<tr data-id="${it.id}"><td class="c rf1">${no}</td><td class="c rf2">${it.d}</td><td class="c rf3">${esc(it.ref)}</td><td class="c">${esc(it.rev)}</td>${rlLL() ? `<td class="c">${esc(it.lvl)}</td>` : ''}${rlLL() ? `<td class="c">${esc(it.loc)}</td>` : ''}<td class="rl-desc">${esc(it.desc)}</td>
      <td class="c${msDateCls(it)}">${msFmt(it.plan)}</td><td class="c">${msFmt(it.sub)}</td><td class="c">${msFmt(it.ret)}</td><td class="c">${rv}</td>
      <td class="c st-${msCls(it.st) || 'none'}">${esc(it.st)}</td><td class="c st-${msCls(it.fin) || 'none'}">${esc(it.fin)}</td><td>${esc(it.rem)}</td></tr>`;
  }
  return `<tr data-id="${it.id}"><td class="c rf1">${no}</td><td class="c rf2">${it.d}</td>
    <td class="rf3"><input class="ms-c c" data-k="ref" value="${esc(it.ref)}" aria-label="Reference no." maxlength="120"></td>
    <td><input class="ms-c c" data-k="rev" value="${esc(it.rev)}" aria-label="Revision" maxlength="10"></td>
    ${rlLL() ? `<td><input class="ms-c c" data-k="lvl" value="${esc(it.lvl)}" aria-label="Level" maxlength="60"></td><td><textarea class="ms-c c" data-k="loc" rows="1" aria-label="${esc(K.loc.split('\n')[0])}" maxlength="200">${esc(it.loc)}</textarea></td>` : ''}
    <td><textarea class="ms-c" data-k="desc" rows="1" aria-label="${esc(K.desc)}" maxlength="600" placeholder="${esc(K.descPh)}">${esc(it.desc)}</textarea></td>
    <td class="${msDateCls(it).trim()}"><input type="date" class="ms-c${it.plan ? '' : ' is-empty'}" data-k="plan" value="${it.plan}" aria-label="Planned submission date"></td>
    <td><input type="date" class="ms-c${it.sub ? '' : ' is-empty'}" data-k="sub" value="${it.sub}" aria-label="Submitted date"></td>
    <td><input type="date" class="ms-c${it.ret ? '' : ' is-empty'}" data-k="ret" value="${it.ret}" aria-label="Returned date"></td>
    <td class="c" data-rv>${rv}</td>
    <td class="c">${msSelect('st', it)}</td><td class="c">${msSelect('fin', it)}</td>
    <td><textarea class="ms-c" data-k="rem" rows="1" aria-label="Remark" maxlength="400">${esc(it.rem)}</textarea></td>
    <td class="ms-tools">${rlRowTools(it, idx, list, K)}</td></tr>`;
}
function rlSheetHTML(code) {
  const log = RLV.log, e = RLV.mode === 'edit', list = rlItemsOf(log, code), c = rlCnt(list), K = rlK(), d = rlDiscs(RLV.kind).find(x => x.code === code);
  const full = list.length >= RL_MAX;
  // a long log is shown 50 rows at a time (the standard sheet has 50 rows ready)
  const pages = Math.max(1, Math.ceil(list.length / RL_PAGE)); RLV.pg = Math.max(0, Math.min(pages - 1, RLV.pg));
  const from = RLV.pg * RL_PAGE, shown = list.slice(from, from + RL_PAGE);
  const pager = pages > 1 ? `<div class="rl-pager" role="group" aria-label="Rows"><button type="button" class="btn btn-sm" data-rl-act="pg" data-pg="0"${RLV.pg ? '' : ' disabled'}>First</button><button type="button" class="btn btn-sm" data-rl-act="pg" data-pg="${RLV.pg - 1}"${RLV.pg ? '' : ' disabled'}>Previous</button><span>Rows ${from + 1} to ${from + shown.length} of ${list.length}</span><button type="button" class="btn btn-sm" data-rl-act="pg" data-pg="${RLV.pg + 1}"${RLV.pg < pages - 1 ? '' : ' disabled'}>Next</button><button type="button" class="btn btn-sm" data-rl-act="pg" data-pg="${pages - 1}"${RLV.pg < pages - 1 ? '' : ' disabled'}>Last</button></div>` : '';
  return `${pager}<div class="ms-scroll"><div class="ms-paper">
    ${rlHeadHTML(K.nc ? K.title + ' - ' + d.head : d.head, K.title + ' LOG', c, esc(msFmtLong(msFromDay(msToday()))))}
    ${e ? `<div class="ms-bl-add rl-tools"><label class="ms-rev rl-pat">Reference numbering <input class="ms-in" data-rl-pat value="${esc(log.pat)}" maxlength="80" aria-label="Reference numbering" title="{DISC} is the discipline code of the sheet and {NNNN} the running number"></label>${K.nc ? `<label class="ms-rev" title="Days from the Received Date to the Target Close-out Date (cell J3 of the Summary sheet)">Close-out allowance (days) <input class="ms-in" type="number" min="0" max="365" step="1" data-rl-allow value="${rlAllow()}" aria-label="Target close-out allowance in days"></label>` : ''}<label class="ms-rev">Log revision <input class="ms-in" data-rl-rev value="${esc(log.rev)}" maxlength="10" aria-label="Log revision"></label><button type="button" class="btn btn-ghost btn-sm" data-rl-act="bl-reset" title="Fill the project bar and the block again from the library's project details">Refill from the library</button></div>` : ''}
    <table class="ms-log rl-log" data-code="${code}">${rlColsHTML(e ? [132] : null)}${rlTheadHTML(e)}
      <tbody>${shown.map((it, i) => rlRowHTML(it, from + i + 1, from + i, list)).join('')}
      ${!list.length && !e ? `<tr class="ms-none"><td colspan="${rlNC()}">No ${K.items} in this log yet. Switch to Edit to add them.</td></tr>` : ''}
      ${e ? `<tr class="ms-addrow"><td colspan="${rlNC()}"><button type="button" class="btn btn-ghost btn-sm" data-rl-act="add"${full ? ' disabled' : ''}>+ Add ${K.item}</button>${full ? ` <span class="hint">The standard workbook reads up to ${RL_MAX} rows in a log.</span>` : ''}</td><td class="ms-tools"></td></tr>` : ''}</tbody>
    </table></div></div>`;
}
function rlSumFootHTML(K, w, log) {
  return `<p class="hint">${log.updatedAt ? `Saved in ${MS_WHERE} ${esc(new Date(log.updatedAt).toLocaleString([], { day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: '2-digit' }))}.` : `Not saved in ${MS_WHERE} yet.`}</p>
    ${w && log.updatedAt ? (RLV.rm === 'LOG' ? `<div class="confirm"><span>Delete the ${K.name} of ${esc(rlName())} from ${MS_WHERE}? This cannot be undone. Download it first with Save as Excel if you may need it.</span><div class="btns"><button type="button" class="btn btn-sm btn-danger-solid" data-rl-act="del-yes">Delete log</button><button type="button" class="btn btn-sm" data-rl-act="rm-no">Cancel</button></div></div>` : '<div><button type="button" class="btn btn-sm btn-ghost btn-danger" data-rl-act="del">Delete this log</button></div>') : ''}`;
}
// the Summary of an NCR / SOR log: Total Raised, the four statuses, Overdue, Closure % and the average days to close
function rlNcSummaryHTML() {
  const log = RLV.log, w = msCanSave(), K = rlK(), discs = rlDiscs(RLV.kind);
  const rows = discs.map(d => ({ code: d.code, label: `${K.short} - ${d.sum}`, c: rlCnt(rlItemsOf(log, d.code)) })), tot = rlCnt(log.items);
  const avgAll = rows.reduce((a, r) => a + r.c.avg, 0) / rows.length;     // as the workbook: the average of the eight averages
  const pct = v => (Math.round(v * 1000) / 10) + '%', one = v => String(Math.round(v * 10) / 10);
  const vals = (c, avg) => [c.sub, c.OPEN, c.CLOSED, c.RESUBMIT, c.UR, c.overdue, pct(c.closure), one(avg)];
  const cell = v => `<td class="c">${v}</td>`;
  const noFin = log.items.filter(it => !it.fin).length;
  return `<div class="ms-scroll ms-scroll-sum"><div class="ms-paper ms-paper-sum">
    <div class="ms-sum-head"><div><div class="ms-h-title">PROJECT : ${esc(log.block.title)}</div><div class="ms-h-sub">${esc(K.title)} SUMMARY</div><div class="ms-date"><b>DATE:</b> ${esc(msFmtSlash(msFromDay(msToday())))} &nbsp; <b>Target close-out allowance (days):</b> ${rlAllow()}</div></div><div class="ms-sum-logo"><img src="${MS_LOGO}" alt="Oxypro"></div></div>
    <table class="ms-sum rl-ncsum"><thead><tr><th>SN</th><th>${esc(K.long)}</th><th>Total Raised</th>${RL_NC_STATUS.map(k => `<th class="st-${k}">${k}</th>`).join('')}<th>Overdue</th><th>Closure %</th><th>Avg Days to Close</th><th>Remarks</th></tr></thead>
    <tbody>${rows.map((r, i) => `<tr><td class="c">${i + 1}</td><td><button type="button" class="ms-link" data-rl-tab="${r.code}">${esc(r.label)}</button></td>${vals(r.c, r.c.avg).map(cell).join('')}<td></td></tr>`).join('')}
    <tr class="ms-sum-tot"><td colspan="2" class="c">TOTAL</td>${vals(tot, avgAll).map((v, i) => `<td class="c${i >= 1 && i <= 4 ? ' st-' + RL_NC_STATUS[i - 1] : ''}">${v}</td>`).join('')}<td></td></tr></tbody></table>
    <p class="rl-sumnote">Overdue = OPEN or RESUBMIT ${K.items} past their Target Close-out Date. Closure % = CLOSED / Total Raised. Counts use each log's Final Status.</p>
  </div></div>
  <div class="ms-facts">
    <p>${log.items.length} ${log.items.length === 1 ? K.item : K.items} in the log. ${tot.CLOSED} closed, ${tot.OPEN + tot.RESUBMIT} open or to be resubmitted, ${tot.UR} under review.${noFin ? ` ${noFin} without a final status (not counted in the summary, as in the workbook).` : ''}${tot.overdue ? ` <b class="ms-red">${tot.overdue} overdue</b> (target close-out date passed).` : ''}</p>
    ${rlSumFootHTML(K, w, log)}
  </div>`;
}
function rlSummaryHTML() {
  if (rlNc()) return rlNcSummaryHTML();
  const log = RLV.log, w = msCanSave(), K = rlK();
  const rows = RL_DISC.map(d => ({ code: d.code, label: `${K.short} - ${d.sum}`, c: rlCnt(rlItemsOf(log, d.code)) })), tot = rlCnt(log.items);
  const cell = v => `<td class="c">${v}</td>`;
  const vals = c => [c.sub, c.A, c.B, c.C, c.D, c.E, c.UR, c.re];
  const noFin = log.items.filter(it => !it.fin || it.fin === 'n/a').length;
  return `<div class="ms-scroll ms-scroll-sum"><div class="ms-paper ms-paper-sum">
    <div class="ms-sum-head"><div><div class="ms-h-title">PROJECT : ${esc(log.block.title)}</div><div class="ms-h-sub">${esc(K.title)} SUMMARY</div><div class="ms-date"><b>DATE:</b> ${esc(msFmtSlash(msFromDay(msToday())))}</div></div><div class="ms-sum-logo"><img src="${MS_LOGO}" alt="Oxypro"></div></div>
    <table class="ms-sum"><thead><tr><th>SN</th><th>${esc(K.long)}</th><th>Total Submitted</th>${['A', 'B', 'C', 'D', 'E'].map(k => `<th class="st-${k}">${k}' Status</th>`).join('')}<th class="st-UR">Under Review</th><th>To Be Re-submitted<br>(C+D)</th><th>Remarks</th></tr></thead>
    <tbody>${rows.map((r, i) => `<tr><td class="c">${i + 1}</td><td><button type="button" class="ms-link" data-rl-tab="${r.code}">${esc(r.label)}</button></td>${vals(r.c).map(cell).join('')}<td></td></tr>`).join('')}
    <tr class="ms-sum-tot"><td colspan="2" class="c">TOTAL</td>${vals(tot).map((v, i) => `<td class="c${i >= 1 && i <= 6 ? ' st-' + ['A', 'B', 'C', 'D', 'E', 'UR'][i - 1] : ''}">${v}</td>`).join('')}<td></td></tr></tbody></table>
  </div></div>
  <div class="ms-facts">
    <p>${log.items.length} ${log.items.length === 1 ? K.item : K.items} in the log. ${tot.sub} with a final status, ${tot.A + tot.B} approved (A or B).${noFin ? ` ${noFin} without a final status (not counted in the summary, as in the workbook).` : ''}${tot.overdue ? ` <b class="ms-red">${tot.overdue} overdue</b> (planned date passed, not submitted).` : ''}${tot.soon ? ` ${tot.soon} due within 7 days.` : ''}</p>
    ${rlSumFootHTML(K, w, log)}
  </div>`;
}
// the Transmittal Sheet: the requests submitted (NCR / SOR: the reports closed out) on the chosen day, from every discipline log
// (the workbook lists the day typed in its date cell: B10, or B9 in the NCR and SOR workbooks)
function rlTransHTML() {
  const log = RLV.log, K = rlK(), list = rlOnDay(log, RLV.day), c = rlCnt(list), what = K.nc ? 'Close-out Date' : 'Submitted Date', cellB = K.nc ? 'B9' : 'B10';
  return `<div class="rl-daybar"><label>Transmittal date <input type="date" class="inp rl-day" data-rl-day value="${esc(RLV.day)}"></label><span class="hint">${list.length} ${list.length === 1 ? K.item : K.items} ${K.nc ? 'closed out' : 'submitted'} on this day</span></div>
    <div class="ms-scroll"><div class="ms-paper">
    ${rlHeadHTML(K.title, 'TRANSMITTAL SHEET', c, esc(msFmtLong(RLV.day)))}
    <table class="ms-log rl-log">${rlColsHTML()}${rlTheadHTML(false)}
      <tbody>${list.map((it, i) => rlRowHTML(it, i + 1, i, list, true)).join('') || `<tr class="ms-none"><td colspan="${rlNC()}">No ${K.items} with ${RLV.day ? 'a ' + what + ' of ' + esc(msFmtLong(RLV.day)) : 'that date'}. Choose another date above.</td></tr>`}</tbody>
    </table></div></div>
    <p class="hint rl-note">The Transmittal Sheet lists the ${K.items} whose ${what} is the chosen day${K.nc ? ' (' + RL_NC_TRN + ' at most, as in the workbook)' : ''}. In the Excel file the same sheet shows the day typed in its cell ${cellB} (today when the file opens).</p>`;
}

/* ---------- edits ---------- */
const rlFind = id => RLV.log.items.find(it => it.id === id);
function rlRefreshCounts() {
  if (!rlCodes(RLV.kind).includes(RLV.tab)) return;
  const c = rlCnt(rlItemsOf(RLV.log, RLV.tab));
  document.querySelectorAll('#rl-body [data-cnt]').forEach(td => { td.textContent = c[td.dataset.cnt]; });
}
function rlOnInput(e) {
  const t = e.target, log = RLV.log; if (!log) return;
  if (t.hasAttribute('data-rl-day')) { RLV.day = msIso(t.value); if (RLV.day || !t.value) rlRenderBody(); return; }
  if (t.matches('textarea.ms-c')) msGrow(t);
  if (t.type === 'date') t.classList.toggle('is-empty', !t.value);
  if (t.dataset.rlBl) { log.block[t.dataset.rlBl] = t.value; rlSetDirty(); return; }
  if (t.hasAttribute('data-rl-rev')) { log.rev = t.value.trim().slice(0, 10); rlSetDirty(); return; }
  if (t.hasAttribute('data-rl-pat')) { log.pat = t.value.trim().slice(0, 80); rlSetDirty(); return; }
  if (t.hasAttribute('data-rl-allow')) {           // the target dates of the rows on screen follow at once
    const a = parseInt(t.value, 10); if (!(a >= 0 && a <= 365)) return;
    log.allow = a; rlSetDirty();
    document.querySelectorAll('#rl-body tr[data-id]').forEach(tr => { const it = rlFind(tr.dataset.id), tg = tr.querySelector('[data-tg]'); if (it && tg) { tg.textContent = msFmt(rlTarget(it, a)); tg.className = 'c' + rlNcOver(it); } });
    return;
  }
  const k = t.dataset.k, tr = t.closest('tr[data-id]'); if (!k || !tr) return;
  const it = rlFind(tr.dataset.id); if (!it) return;
  if (rlNc()) {
    if (k === 'st' || k === 'fin') { it[k] = rlNcStatus(t.value); t.className = `ms-c ms-stsel st-${it[k] || 'none'}`; rlRefreshCounts(); }
    else if (k === 'rec' || k === 'close' || k === 'resp') it[k] = msIso(t.value);
    else it[k] = t.value;
    if (k !== 'ref' && k !== 'rev' && k !== 'desc' && k !== 'rem') {
      const set = (sel, v) => { const c = tr.querySelector(sel); if (c) c.textContent = v; };
      set('[data-tg]', msFmt(rlTarget(it, rlAllow()))); set('[data-el]', rlElapsed(it)); set('[data-rd]', rlRespDays(it));
      const tg = tr.querySelector('[data-tg]'); if (tg) tg.className = 'c' + rlNcOver(it);
    }
    return rlSetDirty();
  }
  if (k === 'st' || k === 'fin') { it[k] = msStatus(t.value); t.className = `ms-c ms-stsel st-${msCls(it[k]) || 'none'}`; rlRefreshCounts(); }
  else if (k === 'plan' || k === 'sub' || k === 'ret') {
    it[k] = msIso(t.value);
    const rv = tr.querySelector('[data-rv]'); if (rv) rv.textContent = msReview(it);
    const pc = tr.querySelector('[data-k="plan"]'); if (pc) pc.parentElement.className = msDateCls(it).trim();
  } else it[k] = t.value;
  rlSetDirty();
}
function rlAddItem(code, after) {
  const log = RLV.log, it = rlBlankItem(code, rlNextRef(log, code), RLV.kind);
  if (after) { Object.assign(it, rlNc() ? { desc: after.desc, rec: after.rec } : { lvl: after.lvl, loc: after.loc, desc: after.desc, plan: after.plan }); log.items.splice(log.items.indexOf(after) + 1, 0, it); }
  else { const i = log.items.map(o => o.d === code).lastIndexOf(true); if (i >= 0) log.items.splice(i + 1, 0, it); else log.items.push(it); }
  rlSetDirty(); return it;
}
function rlMove(id, dir) {
  const log = RLV.log, it = rlFind(id); if (!it) return;
  const same = log.items.map((o, i) => [o, i]).filter(([o]) => o.d === it.d);
  const p = same.findIndex(([o]) => o === it), q = p + dir; if (q < 0 || q >= same.length) return;
  const a = same[p][1], b = same[q][1]; [log.items[a], log.items[b]] = [log.items[b], log.items[a]];
  RLV.pg = Math.floor(q / RL_PAGE); rlSetDirty(); rlRenderBody();
  const btn = document.querySelector(`#rl-body tr[data-id="${id}"] [data-rl-act="${dir < 0 ? 'up' : 'down'}"]`); if (btn && !btn.disabled) btn.focus();
}
async function rlOnClick(e) {
  const tab = e.target.closest('[data-rl-tab]'); if (tab) { const was = tab.getAttribute('role') === 'tab'; RLV.tab = tab.dataset.rlTab; RLV.rm = null; RLV.pg = 0; rlRenderBody(); const sel = document.querySelector('#rl-body [role="tab"][aria-selected="true"]'); if (sel && was) sel.focus(); return; }
  const b = e.target.closest('[data-rl-act]'); if (!b || b.disabled) return;
  const act = b.dataset.rlAct, tr = b.closest('tr'), log = RLV.log, K = rlK();
  const focusRow = (it, sel) => { RLV.pg = Math.floor(rlItemsOf(log, it.d).indexOf(it) / RL_PAGE); rlRenderBody(); const x = document.querySelector(`#rl-body tr[data-id="${it.id}"] ${sel}`); if (x) { x.focus(); x.scrollIntoView({ block: 'nearest' }); } };
  switch (act) {
    case 'back': return closeRlog();
    case 'start': return rlStart();
    case 'mode-view': RLV.mode = 'view'; RLV.rm = null; rlRenderActions(); return rlRenderBody();
    case 'mode-edit': RLV.mode = 'edit'; if (RLV.tab === 'SUM') RLV.tab = 'MEC'; rlRenderActions(); return rlRenderBody();
    case 'pg': RLV.pg = +b.dataset.pg || 0; RLV.rm = null; rlRenderBody(); { const sc = document.querySelector('#rl-body .ms-scroll'); if (sc) sc.scrollTop = 0; } return;
    case 'save': return rlSave();
    case 'save-xlsx': return rlRun(b, 'Preparing the Excel file…', rlSaveXlsx);
    case 'load-remote': if (RLV.remote) { rlLoad(RLV.remote); renderRl(); } return;
    case 'bl-reset': log.block = rlDefaultBlock(rlProj()); rlSetDirty(); rlRenderBody(); toast('Project bar and block filled from the library'); return;
    case 'add': return focusRow(rlAddItem(RLV.tab), rlLL() ? '[data-k="lvl"]' : '[data-k="desc"]');
    case 'dup': { const src = rlFind(tr.dataset.id); if (src && rlItemsOf(log, src.d).length < RL_MAX) focusRow(rlAddItem(src.d, src), rlLL() ? '[data-k="lvl"]' : '[data-k="desc"]'); return; }
    case 'up': case 'down': return rlMove(tr.dataset.id, act === 'up' ? -1 : 1);
    case 'rm': RLV.rm = tr.dataset.id; rlRenderBody(); { const y = document.querySelector('#rl-body [data-rl-act="rm-yes"]'); if (y) y.focus(); } return;
    case 'rm-no': RLV.rm = null; return rlRenderBody();
    case 'rm-yes': { const i = log.items.findIndex(it => it.id === RLV.rm); if (i >= 0) { const t = log.items[i].ref; log.items.splice(i, 1); rlSetDirty(); toast(`Removed: ${t || K.item}`); } RLV.rm = null; return rlRenderBody(); }
    case 'del': RLV.rm = 'LOG'; return rlRenderBody();
    case 'del-yes': return rlDelete();
  }
}
async function rlRun(btn, label, fn) {
  if (RLV.busy) return; RLV.busy = 'file'; btn.disabled = true; toast(label, 60000);
  try { await fn(); } catch (err) { toast('The file could not be made: ' + ((err && err.message) || err), 7000); }
  finally { RLV.busy = ''; rlRenderActions(); }
}

/* ---------- start, save, delete ---------- */
function rlStart() {
  RLV.log = rlNewLog(RLV.kind, rlProj());
  RLV.parts = 0; RLV.dirty = true; RLV.state = 'ready'; RLV.tab = 'MEC'; RLV.mode = 'edit';
  renderRl();
  toast(`${rlK().name} started. Add the ${rlK().items}, then ${GH ? 'Save in browser' : 'Save to library'}.`, 5000);
}
async function rlSave() {
  if (!msCanSave() || !RLV.log || RLV.busy) return false;
  const log = RLV.log, no = RLV.no, now = new Date().toISOString(), K = rlK();
  // rows in parts small enough for one stored document each
  const parts = []; let cur = [], size = 0;
  for (const it of log.items) { const s = JSON.stringify(it).length * 1.1 + 2; if (cur.length && (cur.length >= RL_PART || size + s > 170000)) { parts.push(cur); cur = []; size = 0; } cur.push(it); size += s; }
  if (cur.length) parts.push(cur);
  if (parts.length > 200) { toast('The log is too large to save in the library.', 7000); return false; }
  RLV.busy = 'save'; RLV.savingAt = now; rlRenderActions();
  try {
    const P = DB.collection(rlCol('logparts'));
    for (let i = 0; i < parts.length; i++) await P.doc(no + '_' + i).set(JSON.parse(JSON.stringify({ no, i, at: now, items: parts[i] })));
    await DB.collection(rlCol('logs')).doc(no).set(JSON.parse(JSON.stringify({ no, kind: RLV.kind, v: 1, rev: log.rev, pat: log.pat, block: log.block, ...(rlNc() ? { allow: rlAllow() } : {}), parts: parts.length, n: log.items.length, updatedAt: now, createdAt: log.createdAt || now })));
    for (let i = parts.length; i < RLV.parts; i++) { try { await P.doc(no + '_' + i).delete(); } catch (e) { /* an unused part left behind */ } }
    log.updatedAt = now; log.createdAt = log.createdAt || now; RLV.parts = parts.length;
    await DB.collection(rlCol('logmeta')).doc(no).set({ no, n: log.items.length, updatedAt: now });
    RLV.dirty = false; RLV.remote = null;
    toast(`${K.name} saved in ${MS_WHERE}`);
    return true;
  } catch (e) { toast(writeError(e), 6000); return false; }
  finally { RLV.busy = ''; rlRenderActions(); if (RLV.tab === 'SUM') rlRenderBody(); else { const n = $('#rl-body .ms-notice'); if (n && !RLV.remote) n.remove(); } }
}
async function rlDelete() {
  if (!msCanSave()) return;
  const no = RLV.no, K = rlK();
  try {
    await DB.collection(rlCol('logs')).doc(no).delete();
    await DB.collection(rlCol('logmeta')).doc(no).delete();
    for (let i = 0; i < RLV.parts; i++) { try { await DB.collection(rlCol('logparts')).doc(no + '_' + i).delete(); } catch (e) { /* left behind */ } }
    toast(`The ${K.name} of ${rlName()} was deleted from ${MS_WHERE}`);
    RLV.dirty = false; closeRlog(true);
  } catch (e) { toast(writeError(e), 6000); }
}
/* the Excel file: the standard workbook (kept beside the page as rlog-wir.js, rlog-mir.js, rlog-ncr.js, rlog-sor.js) with this log filled in */
async function rlSaveXlsx() {
  const kind = RLV.kind, log = RLV.log, p = rlProj();
  await Promise.all([loadScript(RL_LIBS.jszip), loadScript(`rlog-${kind}.js`)]);
  const tpl = window.__RLOG_TPL && window.__RLOG_TPL[kind]; if (!tpl || !window.JSZip) throw new Error('the standard workbook could not be loaded');
  const lg = await msLogos(p), logos = {};
  for (const k of ['client', 'consultant', 'contractor']) logos[k] = lg[k] ? { b64: lg[k].data.split(',')[1], w: lg[k].w, h: lg[k].h } : null;
  const sheets = {}; for (const d of rlCodes(kind)) sheets[d] = rlItemsOf(log, d);
  const u8 = await rlFillTemplate(window.JSZip, tpl, { kind, title: log.block.title, block: log.block, sheets, logos, allow: log.allow });
  await saveFile(rlFileBase() + '.xlsx', new Blob([u8], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
}

function bindRlog() {
  const v = $('#view-rlog');
  v.addEventListener('click', rlOnClick);
  v.addEventListener('input', rlOnInput);
  v.addEventListener('keydown', e => {
    const tab = e.target.closest('[role="tab"]');
    if (tab && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')) {
      const all = [...document.querySelectorAll('#rl-body [role="tab"]')], i = all.indexOf(tab), n = all[(i + (e.key === 'ArrowRight' ? 1 : -1) + all.length) % all.length];
      e.preventDefault(); n.click(); const s = document.querySelector(`#rl-body [data-rl-tab="${n.dataset.rlTab}"]`); if (s) s.focus();
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's' && S.view === 'rlog') { e.preventDefault(); if (RLV.dirty && msCanSave()) rlSave(); }
  });
}
