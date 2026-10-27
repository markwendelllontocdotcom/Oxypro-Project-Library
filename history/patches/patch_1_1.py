"""v1.1.0: Master List columns, Handover Stage status, View menu (light / dark / auto)."""
import os, re
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

# ---- tokens: info colour for Handover Stage
rep("--danger:#B3151C;", "--danger:#B3151C; --info:#1D5C96; --info-soft:#E3EEF8;")
rep("--danger:#FF6E74;", "--danger:#FF6E74; --info:#86BDF2; --info-soft:#17293B;", 2)

LIGHT = """  --red:#D81F27; --red-hover:#BC1820; --red-text:#C21A22; --red-soft:#FBECEC; --on-red:#FFFFFF;
  --bg:#F2F3F4; --surface:#FFFFFF; --surface-2:#F6F7F8; --line:#E0E2E5; --line-strong:#C9CCD1;
  --fg:#232425; --fg-2:#3C3F43; --muted:#62666C; --faint:#959AA0;
  --chip-on-bg:#2B2B2B; --chip-on-fg:#FFFFFF;
  --ok:#1E7046; --ok-soft:#E2F2E9; --warn:#87570A; --warn-soft:#FDF0D5; --danger:#B3151C; --info:#1D5C96; --info-soft:#E3EEF8;
  --scrim:rgba(20,21,23,.55); --focus:#D81F27;
  --shadow:0 1px 2px rgba(25,27,30,.06),0 6px 20px rgba(25,27,30,.07);
  --shadow-lg:0 10px 40px rgba(20,21,23,.22);
  --logo-light:block; --logo-dark:none;
  color-scheme:light;"""
DARK = """  --red:#E3333B; --red-hover:#F0474F; --red-text:#FF6E74; --red-soft:#3A1F21; --on-red:#FFFFFF;
  --bg:#141517; --surface:#1C1D20; --surface-2:#232428; --line:#2F3135; --line-strong:#43464C;
  --fg:#ECEDEF; --fg-2:#D3D5D8; --muted:#A3A7AD; --faint:#73777E;
  --chip-on-bg:#ECEDEF; --chip-on-fg:#17181A;
  --ok:#62D19B; --ok-soft:#173226; --warn:#F1C46E; --warn-soft:#382C13; --danger:#FF6E74; --info:#86BDF2; --info-soft:#17293B;
  --scrim:rgba(0,0,0,.66); --focus:#FF6E74;
  --shadow:0 1px 2px rgba(0,0,0,.35),0 6px 20px rgba(0,0,0,.3);
  --shadow-lg:0 10px 40px rgba(0,0,0,.55);
  --logo-light:none; --logo-dark:block;
  color-scheme:dark;"""
rep("  color-scheme:dark;\n}\n*{box-sizing:border-box}",
    "  color-scheme:dark;\n}\n/* View menu: the viewer's own choice (Light or Dark) wins over the Claude app and device theme */\n"
    "html:root[data-view=\"light\"]{\n" + LIGHT + "\n}\nhtml:root[data-view=\"dark\"]{\n" + DARK + "\n}\n*{box-sizing:border-box}")

# ---- CSS: view menu, status pill, year column, detail text
rep(".top-actions{margin-left:auto;display:flex;flex-wrap:wrap;gap:8px}",
    """.top-actions{margin-left:auto;display:flex;flex-wrap:wrap;gap:8px}
.viewmenu{position:relative}
.vm-cur{font-weight:500;color:var(--muted)}
.btn .chev{width:14px;height:14px;color:var(--muted)}
.menu{position:absolute;right:0;top:calc(100% + 6px);z-index:60;min-width:244px;background:var(--surface);border:1px solid var(--line-strong);border-radius:6px;box-shadow:var(--shadow-lg);padding:6px;display:flex;flex-direction:column;gap:2px}
.menu-label{font:600 12px var(--f-cond);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:6px 10px 4px}
.menu-item{display:flex;align-items:center;gap:11px;width:100%;padding:9px 10px;border:0;border-radius:4px;background:none;cursor:pointer;text-align:left;font:500 14px/1.25 var(--f-body);color:var(--fg)}
.menu-item:hover,.menu-item:focus-visible{background:var(--surface-2)}
.menu-item:focus-visible{outline-offset:-2px}
.menu-item small{display:block;color:var(--muted);font-size:12.5px;font-weight:400;margin-top:1px}
.menu-item[aria-checked="true"]{font-weight:600}
.sw{flex:none;width:24px;height:24px;border-radius:50%;border:1px solid var(--line-strong)}
.sw-light{background:#FFFFFF}
.sw-dark{background:#1C1D20}
.sw-auto{background:linear-gradient(135deg,#FFFFFF 50%,#1C1D20 50%)}
.tick{margin-left:auto;flex:none;width:16px;height:16px;color:var(--red-text);visibility:hidden}
.menu-item[aria-checked="true"] .tick{visibility:visible}""")
rep(".st-on{background:var(--warn-soft);color:var(--warn)}",
    ".st-on{background:var(--warn-soft);color:var(--warn)}\n.st-hand{background:var(--info-soft);color:var(--info)}")
rep("grid-template-columns:34px 68px minmax(0,2.3fr) minmax(0,1.3fr) minmax(0,1.6fr) 54px 100px;",
    "grid-template-columns:34px 68px minmax(0,2.2fr) minmax(0,1.2fr) minmax(0,1.5fr) 62px 54px 124px;")
rep(".dl dd{margin:0;overflow-wrap:anywhere;color:var(--fg)}",
    ".dl dd{margin:0;overflow-wrap:anywhere;color:var(--fg)}\n.dl dd.pre{white-space:pre-line}\n.r-year{font-variant-numeric:tabular-nums;white-space:nowrap}")

# ---- header: View menu
CHECK = '<svg class="tick" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
rep('      <button type="button" class="btn" id="btn-export" hidden>Export to Excel</button>\n    </div>',
    '''      <button type="button" class="btn" id="btn-export" hidden>Export to Excel</button>
      <div class="viewmenu">
        <button type="button" class="btn" id="btn-view" aria-haspopup="menu" aria-expanded="false" aria-controls="view-menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 3.5v17a8.5 8.5 0 0 0 0-17z" fill="currentColor"/></svg>View <span class="vm-cur" id="view-cur">Auto</span><svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></button>
        <div class="menu" id="view-menu" role="menu" aria-label="Background" hidden>
          <span class="menu-label">Background</span>
          <button type="button" class="menu-item" role="menuitemradio" aria-checked="false" data-view-opt="light"><span class="sw sw-light"></span><span>Light<small>White background</small></span>''' + CHECK + '''</button>
          <button type="button" class="menu-item" role="menuitemradio" aria-checked="false" data-view-opt="dark"><span class="sw sw-dark"></span><span>Dark<small>Dark background</small></span>''' + CHECK + '''</button>
          <button type="button" class="menu-item" role="menuitemradio" aria-checked="false" data-view-opt="auto"><span class="sw sw-auto"></span><span>Auto<small>Follows your Claude app setting</small></span>''' + CHECK + '''</button>
        </div>
      </div>
    </div>''')
rep('placeholder="Search name, project no., area, client…"', 'placeholder="Search name, project no., area, client, contractor…"')
rep('        <option value="emirate">Emirate</option>\n', '        <option value="emirate">Emirate</option>\n        <option value="year">Year (newest first)</option>\n')
rep('<span>Area</span><span>Emirate</span><span>Status</span>', '<span>Area</span><span>Year</span><span>Emirate</span><span>Status</span>')
rep('Version 1.0.0 (24 Oct 2026)', 'Version 1.1.0 (27 Oct 2026)')

# ---- helpers: formatting + view
rep("const lsGet = k =>",
    """const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const isNum = v => /^-?\\d[\\d,]*(\\.\\d+)?$/.test(String(v == null ? '' : v).trim());
function fmtValue(v) { const s = String(v == null ? '' : v).trim(); if (!isNum(s)) return s; return 'AED ' + Number(s.replace(/,/g, '')).toLocaleString('en-US', { maximumFractionDigits: 2 }); }
function fmtDuration(v) { const s = String(v == null ? '' : v).trim(); if (!/^\\d+(\\.\\d+)?$/.test(s)) return s; return s + (Number(s) === 1 ? ' month' : ' months'); }
function fmtDate(v) { const s = String(v == null ? '' : v).trim(); const m = s.match(/^(\\d{4})-(\\d{2})-(\\d{2})$/); return m ? `${+m[3]} ${MON[+m[2] - 1]} ${m[1]}` : s; }
const STATUSES = [['Completed', 'st-done', 'completed'], ['Handover Stage', 'st-hand', 'at handover'], ['Ongoing', 'st-on', 'ongoing']];
const lsGet = k =>""")

# ---- search, sort, status normalisation
rep("const hay = [p.no, p.name, p.sectors, p.levels, p.area, p.emirate, EMIRATES[p.emirate], p.client, p.mainContractor, p.scopeType, p.scope, p.status].join(' ').toLowerCase();",
    "const hay = [p.no, p.name, p.sectors, p.levels, p.area, p.emirate, EMIRATES[p.emirate], p.client, p.mainContractor, p.mepConsultant, p.leadConsultant, p.standards, p.scopeType, p.scope, p.year, p.status].join(' ').toLowerCase();")
rep("  else a.sort(byNo);\n  return a;",
    "  else if (S.sort === 'year') a.sort((x, y) => String(y.year || '').localeCompare(String(x.year || '')) || byNo(x, y));\n  else a.sort(byNo);\n  return a;")
rep("function normStatus(v) { const s = String(v || ''); if (/complet|handed|finish/i.test(s)) return 'Completed'; if (/ongoing|progress|running|current|active/i.test(s)) return 'Ongoing'; return ''; }",
    "function normStatus(v) { const s = String(v || ''); if (/complet|handed|finish/i.test(s)) return 'Completed'; if (/handover|hand over|snag|close ?out/i.test(s)) return 'Handover Stage'; if (/ongoing|progress|running|current|active|construction/i.test(s)) return 'Ongoing'; return ''; }")

# ---- header summary + status chips
rep("""  const done = [...S.projects.values()].filter(p => p.status === 'Completed').length;
  let txt = 'Loading projects…';
  if (S.dbState === 'ready') txt = n ? `${n} project${n === 1 ? '' : 's'}${names.length ? ' across ' + joinAnd(names) : ''}${done ? ' · ' + done + ' completed' : ''}` : 'No projects yet';""",
    """  const all = [...S.projects.values()];
  const parts = STATUSES.map(([st, , word]) => [all.filter(p => p.status === st).length, word]).filter(x => x[0]).map(x => x[0] + ' ' + x[1]);
  let txt = 'Loading projects…';
  if (S.dbState === 'ready') txt = n ? `${n} project${n === 1 ? '' : 's'}${names.length ? ' across ' + joinAnd(names) : ''}${parts.length ? ' · ' + parts.join(' · ') : ''}` : 'No projects yet';""")
rep("""  const done = all.filter(p => p.status === 'Completed').length, on = all.filter(p => p.status === 'Ongoing').length, none = all.length - done - on;
  $('#chips-status').innerHTML = all.length ? '<span class="fgroup-label">Status</span>' + chip('st', 'all', 'All', null, S.status === 'all') + chip('st', 'Completed', 'Completed', done, S.status === 'Completed') + chip('st', 'Ongoing', 'Ongoing', on, S.status === 'Ongoing') + (none ? chip('st', 'none', 'Not set', none, S.status === 'none') : '') : '';""",
    """  const none = all.filter(p => !STATUSES.some(([st]) => st === p.status)).length;
  $('#chips-status').innerHTML = all.length ? '<span class="fgroup-label">Status</span>' + chip('st', 'all', 'All', null, S.status === 'all')
    + STATUSES.map(([st]) => chip('st', st, st, all.filter(p => p.status === st).length, S.status === st)).join('')
    + (none ? chip('st', 'none', 'Not set', none, S.status === 'none') : '') : '';""")
rep("""function statusPill(s) {
  if (s === 'Completed') return '<span class="st st-done">Completed</span>';
  if (s === 'Ongoing') return '<span class="st st-on">Ongoing</span>';
  return '<span class="st st-none">Not set</span>';
}""",
    """function statusPill(s) {
  const hit = STATUSES.find(([st]) => st === s);
  return hit ? `<span class="st ${hit[1]}">${esc(hit[0])}</span>` : '<span class="st st-none">Not set</span>';
}""")
rep("  if (S.status !== 'all') a = a.filter(p => S.status === 'none' ? !p.status : p.status === S.status);",
    "  if (S.status !== 'all') a = a.filter(p => S.status === 'none' ? !STATUSES.some(([st]) => st === p.status) : p.status === S.status);")

# ---- list rows: year column
rep("    const meta = [p.levels, p.area].filter(Boolean).map(esc).join(' · ');",
    "    const meta = [p.levels, p.area, p.year].filter(Boolean).map(esc).join(' · ');")
rep("      <div class=\"r-cell\">${esc(p.area || '')}</div>\n",
    "      <div class=\"r-cell\">${esc(p.area || '')}</div>\n      <div class=\"r-cell r-year\">${esc(p.year || '')}</div>\n")

# ---- detail panel
rep("function dRow(label, v) { const s = String(v || '').trim(); return `<dt>${esc(label)}</dt><dd${s ? '' : ' class=\"none\"'}>${s ? esc(s) : 'Not recorded'}</dd>`; }",
    """function dRow(label, v, cls) {
  const s = String(v == null ? '' : v).trim();
  if (/^(n\\/?a|not applicable)$/i.test(s)) return `<dt>${esc(label)}</dt><dd class="none">Not applicable</dd>`;
  return `<dt>${esc(label)}</dt><dd class="${s ? (cls || '') : 'none'}">${s ? esc(s) : 'Not recorded'}</dd>`;
}""")
rep("""        ${dRow('Level / floors', p.levels)}${dRow('Area', p.area)}${dRow('Client', p.client)}${dRow('Main contractor', p.mainContractor)}
        ${dRow('Scope type', p.scopeType)}${dRow('Scope of works', p.scope)}${dRow('Contract value', p.value)}${dRow('Duration', p.duration)}${dRow('Completion', p.completion)}""",
    """        ${dRow('Level / floors', p.levels)}${dRow('Area', p.area)}${dRow('Year', p.year)}
        ${dRow("Client's name", p.client)}${dRow('Main contractor', p.mainContractor)}${dRow('MEP consultant', p.mepConsultant)}${dRow('Lead consultant', p.leadConsultant)}
        ${dRow('Scope of work', p.scope, 'pre')}${dRow('Standards / authorities', p.standards)}${dRow('Scope type', p.scopeType)}
        ${dRow('Contract value', fmtValue(p.value))}${dRow('Duration', fmtDuration(p.duration))}${dRow('Start date', fmtDate(p.startDate))}${dRow('Handover date', fmtDate(p.handoverDate))}""")

# ---- add / edit form
rep("""  ['status', 'Status', 'status', '', false],
  ['_h', 'For the presentation sheet'],
  ['client', 'Client', 'inp', '', false],
  ['mainContractor', 'Main contractor', 'inp', '', false],
  ['scopeType', 'Scope type', 'inp', 'e.g. MEP supply & install', false, 'dl-scopetype'],
  ['value', 'Contract value (AED)', 'inp', 'e.g. AED 24,500,000', false],
  ['duration', 'Duration', 'inp', 'e.g. 36 weeks on site', false],
  ['completion', 'Completion', 'inp', 'e.g. September 2025', false],
  ['scope', 'Scope of works', 'txt', 'Shown under the project name on the sheet (up to three lines)', true]
];""",
    """  ['status', 'Project status', 'status', '', false],
  ['year', 'Year', 'inp', 'e.g. 2024-26', false],
  ['_h', 'Parties'],
  ['client', "Client's name", 'inp', '', false],
  ['mainContractor', 'Main contractor', 'inp', '', false],
  ['mepConsultant', 'MEP consultant', 'inp', '', false],
  ['leadConsultant', 'Lead consultant', 'inp', 'na if there is none', false],
  ['_h', 'Contract'],
  ['value', 'Contract value (AED)', 'inp', 'e.g. 24500000', false],
  ['duration', 'Duration (months)', 'inp', 'e.g. 24', false],
  ['startDate', 'Start date', 'date', '', false],
  ['handoverDate', 'Handover date', 'date', '', false],
  ['_h', 'Scope'],
  ['scopeType', 'Scope type', 'inp', 'e.g. MEP supply & install', false, 'dl-scopetype'],
  ['standards', 'Standards / authorities', 'inp', 'e.g. DCD, DEWA, DM', false],
  ['scope', 'Scope of work', 'txt', 'Shown under the project name on the presentation sheet (up to three lines)', true]
];""")
rep("""    else if (type === 'status') ctl = `<select class="sel" id="${id}" name="${k}"><option value="Completed"${v(k) === 'Completed' ? ' selected' : ''}>Completed</option><option value="Ongoing"${v(k) === 'Ongoing' ? ' selected' : ''}>Ongoing</option><option value=""${!v(k) ? ' selected' : ''}>Not set</option></select>`;""",
    """    else if (type === 'status') ctl = `<select class="sel" id="${id}" name="${k}">${STATUSES.map(([st]) => `<option value="${st}"${v(k) === st ? ' selected' : ''}>${st}</option>`).join('')}<option value=""${!STATUSES.some(([st]) => st === v(k)) ? ' selected' : ''}>Not set</option></select>`;
    else if (type === 'date') { const dv = v(k); ctl = !dv || /^\\d{4}-\\d{2}-\\d{2}$/.test(dv) ? `<input class="inp" type="date" id="${id}" name="${k}" value="${esc(dv)}">` : `<input class="inp" id="${id}" name="${k}" value="${esc(dv)}">`; }""")

# ---- Excel import / export (Master List layout)
start = s.index("const COLMAP = [")
end = s.index("async function saveFile(filename, blob) {")
s = s[:start] + r"""const COLMAP = [
  ['no', h => /^(project ?no|project number|proj ?no|job ?no)/.test(h)],
  ['name', h => /(project|building).*name/.test(h) || h === 'name'],
  ['sectors', h => /sector/.test(h)],
  ['levels', h => /level|floor/.test(h)],
  ['emirate', h => /emirate/.test(h)],
  ['status', h => /status/.test(h)],
  ['mainContractor', h => /main ?contractor/.test(h)],
  ['mepConsultant', h => /mep ?consultant/.test(h)],
  ['leadConsultant', h => /lead ?consultant/.test(h)],
  ['client', h => /^client/.test(h)],
  ['scopeType', h => /scope ?type/.test(h)],
  ['scope', h => /scope/.test(h)],
  ['standards', h => /standard|strandard|authorit/.test(h)],
  ['value', h => /value|amount/.test(h)],
  ['duration', h => /duration/.test(h)],
  ['startDate', h => /^start/.test(h)],
  ['handoverDate', h => /handover|complet/.test(h)],
  ['year', h => /^year/.test(h)],
  ['area', h => /^area|location|address/.test(h)]
];
// Export columns follow the Oxypro Projects Master List; Scope Type is the library's own extra column.
const XL_COLS = [
  ['no', 'Project No', 10], ['name', 'Project / Building Name', 36], ['sectors', 'Sectors', 30], ['levels', 'Level/Floor No./\nUnit No.', 28], ['area', 'Area', 42], ['emirate', 'Emirate', 9],
  ['mainContractor', 'Main Contractor', 32], ['mepConsultant', 'MEP\nConsultant', 30], ['leadConsultant', 'Lead Consultant', 24], ['client', "Client's Name", 32], ['scope', 'Scope of Work', 50],
  ['standards', 'Standards / Authorities', 26], ['value', 'Contract\nValue', 16], ['duration', 'Duration\n(Months)', 11], ['startDate', 'Start Date', 13], ['handoverDate', 'Handover Date', 14],
  ['year', 'Year', 10], ['status', 'Project Status', 16], ['scopeType', 'Scope Type', 26]
];
const XL_LABEL = Object.fromEntries(XL_COLS.map(([k, l]) => [k, l.replace(/\s*\n\s*/g, ' ')]));
const DATE_KEYS = ['startDate', 'handoverDate'];
function serialToIso(n) { const d = new Date(Math.round((n - 25569) * 86400000)); return d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0'); }
function isoToSerial(s) { const m = String(s).match(/^(\d{4})-(\d{2})-(\d{2})$/); return m ? (Date.UTC(+m[1], +m[2] - 1, +m[3]) - Date.UTC(1899, 11, 30)) / 86400000 : null; }
function cleanCell(k, raw) {
  if (raw == null || raw === '') return '';
  if (DATE_KEYS.includes(k)) {
    if (typeof raw === 'number' && raw > 20000 && raw < 80000) return serialToIso(raw);
    if (raw instanceof Date && !isNaN(raw)) return raw.toISOString().slice(0, 10);
  }
  if (typeof raw === 'number') return String(Math.round(raw * 100) / 100);
  const t = String(raw);
  if (k === 'scope') return t.split(/\r?\n/).map(l => l.replace(/[ \t ]+/g, ' ').trim()).filter(Boolean).join('\n');
  let v = t.replace(/\s+/g, ' ').trim();
  if (k !== 'value') v = v.replace(/\s+,/g, ',').replace(/,(?=[^\s\d])/g, ', ');
  return v;
}
function changedKeys(r) {
  const p = S.projects.get(r.no); if (!p) return [];
  return Object.keys(r).filter(k => k !== 'no' && r[k] && r[k] !== String(p[k] == null ? '' : p[k]));
}
async function onXlsxFile(e) {
  const file = e.target.files && e.target.files[0]; if (!file) return;
  try { await loadScript(LIBS.xlsx); } catch (err) { toast('The Excel reader could not load. Check your connection and try again.'); return; }
  let best = null;
  try {
    const wb = XLSX.read(await file.arrayBuffer(), { type: 'array' });
    for (const name of wb.SheetNames) {
      const grid = XLSX.utils.sheet_to_json(wb.Sheets[name], { header: 1, raw: true, defval: '' });
      const hi = grid.findIndex(r => r.some(c => /^(project ?no|project number|proj ?no)/.test(String(c).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim())));
      if (hi < 0) continue;
      const cols = {}; const taken = new Set();
      grid[hi].forEach((c, i) => { const h = String(c).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim(); if (!h) return; const hit = COLMAP.find(([k, t]) => !taken.has(k) && t(h)); if (hit) { cols[hit[0]] = i; taken.add(hit[0]); } });
      const rows = [];
      for (const r of grid.slice(hi + 1)) {
        const no = normNo(r[cols.no]); if (!no || !NO_RE.test(no)) continue;
        const d = { no };
        for (const k of Object.keys(cols)) if (k !== 'no') d[k] = cleanCell(k, r[cols[k]]);
        if (d.emirate) d.emirate = normEmirate(d.emirate);
        if ('status' in d) d.status = normStatus(d.status);
        rows.push(d);
      }
      if (!best || rows.length > best.rows.length) best = { sheet: name, rows, cols };
    }
  } catch (err) { toast('This file could not be read. Save it as .xlsx and try again.'); return; }
  if (!best || !best.rows.length) { toast('No projects found. The sheet needs a "Project No" column header.'); return; }
  const seen = new Map(); best.rows.forEach(r => seen.set(r.no, r));
  S.imp = { file: file.name, sheet: best.sheet, rows: [...seen.values()], cols: Object.keys(best.cols), update: true };
  renderImport();
}
function renderImport() {
  const I = S.imp; if (!I) return;
  const isNew = r => !S.projects.has(r.no);
  const nNew = I.rows.filter(isNew).length;
  const nChg = I.rows.filter(r => !isNew(r) && changedKeys(r).length).length;
  const nSame = I.rows.length - nNew - nChg;
  const shown = ['no', 'name', 'emirate', 'year', 'status', 'mainContractor'].filter(k => I.cols.includes(k));
  const total = nNew + (I.update ? nChg : 0);
  const tag = r => isNew(r) ? '<span class="tag tag-new">New</span>' : changedKeys(r).length ? `<span class="tag">${changedKeys(r).length} change${changedKeys(r).length === 1 ? '' : 's'}</span>` : '<span class="tag">No change</span>';
  openModal(`<div class="dialog">
    <div class="dialog-head"><h2>Import from Excel</h2><button type="button" class="btn btn-ghost btn-sm" data-close>Close</button></div>
    <div class="dialog-body">
      <p style="margin:0">Found <strong>${I.rows.length}</strong> project${I.rows.length === 1 ? '' : 's'} on the sheet “${esc(I.sheet)}” in ${esc(I.file)}: <strong>${nNew}</strong> new, <strong>${nChg}</strong> with changes and <strong>${nSame}</strong> unchanged.</p>
      <p class="d-note" style="margin:0">Columns read: ${esc(joinAnd(I.cols.map(k => XL_LABEL[k])))}.</p>
      ${nChg ? `<label class="check-row"><input type="checkbox" id="imp-upd" ${I.update ? 'checked' : ''}> Update the ${nChg} project${nChg === 1 ? '' : 's'} with changes (empty cells in the file are skipped)</label>` : ''}
      <div class="imp-table"><table><thead><tr><th></th>${shown.map(k => `<th>${esc(XL_LABEL[k])}</th>`).join('')}</tr></thead><tbody>
      ${I.rows.map(r => `<tr><td>${tag(r)}</td>${shown.map(k => `<td>${esc(r[k] || '')}</td>`).join('')}</tr>`).join('')}
      </tbody></table></div>
      <p class="err" id="imp-err" hidden></p>
    </div>
    <div class="dialog-foot"><button type="button" class="btn" data-close>Cancel</button><button type="button" class="btn btn-primary" id="imp-go"${total ? '' : ' disabled'}>${total ? `Import ${total} project${total === 1 ? '' : 's'}` : 'Nothing to import'}</button></div>
  </div>`);
  const upd = $('#imp-upd'); if (upd) upd.addEventListener('change', e => { I.update = e.target.checked; renderImport(); });
  $('#imp-go').addEventListener('click', runImport);
}
async function runImport() {
  const I = S.imp; if (!I) return; const btn = $('#imp-go'); btn.disabled = true;
  const now = new Date().toISOString(); let done = 0, added = 0, updated = 0;
  const todo = I.rows.filter(r => !S.projects.has(r.no) || (I.update && changedKeys(r).length));
  try {
    for (const r of todo) {
      btn.textContent = `Importing ${++done} of ${todo.length}…`;
      const ref = DB.collection('projects').doc(r.no);
      if (S.projects.has(r.no)) {
        const upd = {}; for (const k of changedKeys(r)) upd[k] = r[k];
        if (Object.keys(upd).length) { upd.updatedAt = now; await ref.update(upd); updated++; }
      } else {
        const d = { no: r.no, photos: [null, null, null, null, null], createdAt: now, updatedAt: now };
        Object.keys(XL_LABEL).forEach(k => { if (k !== 'no') d[k] = r[k] || ''; });
        await ref.set(d); added++;
      }
    }
    closeModal(); toast(`Imported: ${added} added${updated ? ' and ' + updated + ' updated' : ''}`);
  } catch (e) { const err = $('#imp-err'); if (err) { err.textContent = writeError(e) + ` ${added + updated} were saved before the error.`; err.hidden = false; } btn.disabled = false; btn.textContent = 'Try again'; }
}
async function exportXlsx() {
  const btn = $('#btn-export'); btn.disabled = true;
  try {
    await loadScript(LIBS.xlsx);
    const a = sortedNos(S.projects).map(no => S.projects.get(no));
    const head = XL_COLS.map(c => c[1]).concat('Photos in Library');
    const aoa = [['Oxypro Electromechanical Works LLC - Projects Master List'], [], head]
      .concat(a.map(p => XL_COLS.map(([k]) => String(p[k] == null ? '' : p[k])).concat(photosOf(p).filter(Boolean).length)));
    const ws = XLSX.utils.aoa_to_sheet(aoa);
    a.forEach((p, i) => {
      const r = i + 3;
      XL_COLS.forEach(([k], c) => {
        const addr = XLSX.utils.encode_cell({ r, c }); const v = String(p[k] == null ? '' : p[k]).trim();
        if (DATE_KEYS.includes(k)) { const n = isoToSerial(v); if (n != null) ws[addr] = { t: 'n', v: n, z: 'dd-mmm-yyyy' }; }
        else if (k === 'value' && isNum(v)) ws[addr] = { t: 'n', v: Number(v.replace(/,/g, '')), z: '#,##0' };
        else if (k === 'duration' && /^\d+(\.\d+)?$/.test(v)) ws[addr] = { t: 'n', v: Number(v) };
      });
    });
    ws['!cols'] = XL_COLS.map(c => ({ wch: c[2] })).concat({ wch: 10 });
    ws['!merges'] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: head.length - 1 } }];
    ws['!autofilter'] = { ref: XLSX.utils.encode_range({ s: { r: 2, c: 0 }, e: { r: a.length + 2, c: head.length - 1 } }) };
    const wb = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, ws, 'OXYPRO PROJECT MASTER CASE');
    const buf = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
    await saveFile(`Oxypro - Projects Master List - ${today()}.xlsx`, new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
  } catch (e) { toast('The Excel file could not be made: ' + (e.message || e)); }
  finally { btn.disabled = false; }
}
""" + s[end:]

# ---- presentation sheet: number formatting
rep("""  if (key === 'client') return [sh.client, sh.mc].map(s => String(s || '').trim()).filter(Boolean).join(' / ');
  return String(sh[key] || '').trim();""",
    """  if (key === 'client') return [sh.client, sh.mc].map(s => String(s || '').trim()).filter(s => s && !/^(n\\/?a)$/i.test(s)).join(' / ');
  if (key === 'value') return fmtValue(sh.value);
  if (key === 'duration') return fmtDuration(sh.duration);
  return String(sh[key] || '').trim();""")
rep("  ['scope', 'Scope of works', 'txt', 'Up to three lines on the sheet'],", "  ['scope', 'Scope of work', 'txt', 'Up to three lines on the sheet'],")
rep("  ['value', 'Contract value (AED)', 'inp', 'e.g. AED 24,500,000'],\n  ['duration', 'Duration', 'inp', 'e.g. 36 weeks on site']",
    "  ['value', 'Contract value (AED)', 'inp', 'A plain number shows as AED 24,500,000'],\n  ['duration', 'Duration', 'inp', 'A plain number shows as months, e.g. 24 months']")

# ---- View menu behaviour
rep("function bindGlobal() {",
    """const VIEW_NAMES = { light: 'Light', dark: 'Dark', auto: 'Auto' };
function applyView(mode) {
  if (!VIEW_NAMES[mode]) mode = 'auto';
  const root = document.documentElement;
  if (mode === 'auto') root.removeAttribute('data-view'); else root.setAttribute('data-view', mode);
  document.querySelectorAll('[data-view-opt]').forEach(b => b.setAttribute('aria-checked', String(b.dataset.viewOpt === mode)));
  $('#view-cur').textContent = VIEW_NAMES[mode];
}
function bindView() {
  const btn = $('#btn-view'), menu = $('#view-menu');
  const items = () => [...menu.querySelectorAll('.menu-item')];
  const close = focus => { menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); if (focus) btn.focus(); };
  const place = () => {
    menu.style.left = ''; menu.style.right = '0';
    const r = menu.getBoundingClientRect(), pad = 12;
    if (r.left < pad) { const w = btn.parentElement.getBoundingClientRect(); menu.style.right = 'auto'; menu.style.left = (pad - w.left) + 'px'; }
  };
  btn.addEventListener('click', () => {
    if (!menu.hidden) return close();
    menu.hidden = false; btn.setAttribute('aria-expanded', 'true'); place();
    (menu.querySelector('[aria-checked="true"]') || items()[0]).focus();
  });
  menu.addEventListener('click', e => {
    const b = e.target.closest('[data-view-opt]'); if (!b) return;
    applyView(b.dataset.viewOpt); lsSet('viewTheme', b.dataset.viewOpt); close(true);
  });
  menu.addEventListener('keydown', e => {
    const list = items(), i = list.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') { e.preventDefault(); list[(i + 1) % list.length].focus(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); list[(i - 1 + list.length) % list.length].focus(); }
    else if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); close(true); }
    else if (e.key === 'Tab') close();
  });
  document.addEventListener('click', e => { if (!menu.hidden && !e.target.closest('.viewmenu')) close(); });
}
function bindGlobal() {""")
rep("  bindLibrary(); bindPres(); bindGlobal(); renderAll();",
    "  applyView(lsGet('viewTheme') || 'auto');\n  bindLibrary(); bindPres(); bindGlobal(); bindView(); renderAll();")

# no leftovers of the removed field
assert "completion" not in s.replace("complet|", ""), [m.start() for m in re.finditer("completion", s)]
open(P, 'w').write(s)
print('patched', len(s))
