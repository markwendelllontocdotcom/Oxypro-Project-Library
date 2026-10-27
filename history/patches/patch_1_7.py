"""v1.7.0: Project Code, Approving Authorities and Codes & Standards from the new Master List; Send to PQP Maker."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('Version 1.6.0 (27 Oct 2026)', 'Version 1.7.0 (27 Oct 2026)')

# ---------- fields ----------
rep("  ['no', 'Project no.', 'inp', 'e.g. P123', false],\n",
    "  ['no', 'Project no.', 'inp', 'e.g. P123', false],\n  ['code', 'Project code', 'inp', 'e.g. DXB-243 (used in the PQP Doc Ref)', false],\n")
rep("  ['standards', 'Standards / authorities', 'inp', 'e.g. DCD, DEWA, DM', false],\n",
    "  ['authorities', 'Approving authorities', 'inp', 'e.g. DM, DEWA, DCD, DDA', true],\n  ['codes', 'Codes & standards', 'inp', 'e.g. UAE Fire and Life Safety Code of Practice, ASHRAE, NFPA', true],\n")
rep("p.leadConsultant, p.standards, p.scopeType,", "p.leadConsultant, p.code, p.authorities, p.codes, p.scopeType,")
rep("        ${dRow('Level / floors', p.levels)}${dRow('Area', p.area)}${dRow('Year', p.year)}",
    "        ${dRow('Project code', p.code)}${dRow('Level / floors', p.levels)}${dRow('Area', p.area)}${dRow('Year', p.year)}")
rep("${dRow('Standards / authorities', p.standards)}", "${dRow('Approving authorities', p.authorities)}${dRow('Codes & standards', p.codes)}")

# ---------- Excel: the Master List now starts "Oxypro Project No | Project Code" and has two columns for authorities and codes ----------
rep("  ['no', h => /^(project ?no|project number|proj ?no|job ?no)/.test(h)],",
    "  ['code', h => /^(project|job) ?code/.test(h)],\n  ['no', h => /^(oxypro )?(project ?no|project number|proj ?no|job ?no)/.test(h)],")
rep("  ['standards', h => /standard|strandard|authorit/.test(h)],",
    "  ['codes', h => /codes?\\b.*standard|^codes?$/.test(h)],\n  ['authorities', h => /authorit/.test(h)],   // an older \"Standards / Authorities\" column lands here too")
rep("const hi = grid.findIndex(r => r.some(c => /^(project ?no|project number|proj ?no)/.test(",
    "const hi = grid.findIndex(r => r.some(c => /^(oxypro )?(project ?no|project number|proj ?no)/.test(")
rep("""  ['no', 'Project No', 10], ['name', 'Project / Building Name', 36],""",
    """  ['no', 'Oxypro Project No', 11], ['code', 'Project Code', 13], ['name', 'Project / Building Name', 36],""")
rep("""  ['standards', 'Standards / Authorities', 26], ['value', 'Contract\\nValue', 16],""",
    """  ['authorities', 'Approving Authorities', 30], ['codes', 'Codes & Standards', 36], ['value', 'Contract\\nValue', 16],""")
rep("""        const no = normNo(r[cols.no]); if (!no || !NO_RE.test(no)) continue;
        const d = { no };
        for (const k of Object.keys(cols)) if (k !== 'no') d[k] = cleanCell(k, r[cols[k]]);""",
    """        const no = normNo(r[cols.no]); if (!no || !NO_RE.test(no)) continue;
        const d = { no };
        for (const k of Object.keys(cols)) if (k !== 'no') d[k] = cleanCell(k, r[cols[k]]);
        if (d.code) d.code = d.code.toUpperCase();""")

# ---------- summary page options ----------
rep("const SUM_BASE = [['no', 'Project No'], ['name', 'Project / Building Name'],",
    "const SUM_BASE = [['no', 'Project No'], ['code', 'Project Code'], ['name', 'Project / Building Name'],")
rep("  ['standards', 'Standards / Authorities'], ['value', 'Contract Value'],",
    "  ['authorities', 'Approving Authorities'], ['codes', 'Codes & Standards'], ['value', 'Contract Value'],")
rep("'leadConsultant', 'standards', 'sectors', 'levels']);", "'leadConsultant', 'authorities', 'codes', 'sectors', 'levels']);")
rep("  const MIN = { no: 1.45, year: 1.55,", "  const MIN = { no: 1.45, code: 1.9, year: 1.55,")

# ---------- Send to PQP Maker ----------
rep("""        ${w ? '<button type="button" class="btn" data-act="edit">Edit</button>' : ''}
      </div>""",
    """        ${w ? '<button type="button" class="btn" data-act="edit">Edit</button>' : ''}
        <button type="button" class="btn" data-act="pqp" title="Save a PQP Maker project file filled with this project's details">Send to PQP Maker</button>
      </div>""")
rep("    case 'edit': if (p) openEdit(p.no); return;", "    case 'edit': if (p) openEdit(p.no); return;\n    case 'pqp': if (p) openPqp(p.no); return;")

JS = r"""
/* ---------- Send to PQP Maker ---------- */
// Saves a .pqp file with only what the Library knows. PQP Maker's Open lays the file over a new project made from its
// own settings, so everything left out (Our Role, Disciplines, document control, key personnel, ISO certificates,
// amendment record, branding, quality settings) stays the user's input there, starting from PQP Maker's defaults.
const PQP_URL = 'https://markwendelllontocdotcom.github.io/MEP-PQP-Maker/';
const PQP_AUTH = [['DM', /^(dm|dubai municipality)\b/], ['DEWA', /\bdewa\b|dubai electricity/], ['DCD', /^(dcd|dubai civil defen[cs]e)\b/], ['Trakhees', /trakhees/],
  ['Dubai South', /dubai south/], ['DDA', /^(dda|dubai development authority)\b/], ['RTA', /^(rta|roads? (and|&) transport)/], ['Etisalat/du', /etisalat|^du$|^e&/],
  ['ADM', /^(adm|abu dhabi municipality)\b/], ['ADDC', /^(addc|abu dhabi distribution)/], ['ADCD', /^(adcd|abu dhabi civil defen)/], ['SEWA', /^(sewa|sharjah electricity)/],
  ['Etihad WE', /etihad/], ['Sharjah Civil Defence', /sharjah civil defen|^scda$/]];
const PQP_CODES = [['UAE Fire & Life Safety Code', /fire (and|&) life safety|^dcd$/], ['DEWA Regulations', /\bdewa\b/], ['DM Building Code', /^dm\b|dubai municipality|dm building/],
  ["Al Sa'fat (Dubai Green Building System)", /sa.?fat/], ['Estidama (Abu Dhabi)', /estidama/], ['ASHRAE', /ashrae/], ['NFPA', /nfpa/], ['BS 7671', /7671/],
  ['CIBSE', /cibse/], ['SMACNA', /smacna/], ['Project Specifications', /specification/]];
const PQP_TYPES = [['Residential', /resident|villa|apartment|town ?house|housing/], ['Commercial', /commercial|retail|mall|office|business|shop/], ['Hospitality', /hotel|hospitality|resort/],
  ['Industrial', /industr|warehouse|factory/], ['Infrastructure', /infra|parking|car ?park|utilit|road/], ['Mixed-Use', /mixed/], ['Healthcare', /health|hospital|clinic|medical/],
  ['Education', /school|education|universit|college/]];
// a list cell to PQP Maker options (in PQP Maker's order) plus the rest as "Other" text, as typed
function pqpList(text, table) {
  const items = String(text || '').split(/[,;\n|]+/).map(x => x.replace(/\s+/g, ' ').trim()).filter(Boolean), hit = new Set(), other = [];
  for (const it of items) { const m = table.find(([, rx]) => rx.test(it.toLowerCase())); if (m) hit.add(m[0]); else if (!other.includes(it)) other.push(it); }
  const list = table.map(([o]) => o).filter(o => hit.has(o));
  return { list: other.length ? list.concat('Other') : list, other };
}
const isoOk = v => /^\d{4}-\d{2}-\d{2}$/.test(String(v || ''));
const realName = v => { const t = String(v || '').replace(/^m\/s\.?\s*/i, '').trim(); return /^(n\/?a|not applicable|-|–)$/i.test(t) ? '' : t; };
function pqpData(p) {
  const pr = {}, rows = [], put = (k, label, v, show) => { pr[k] = v; rows.push([label, show == null ? v : show]); };
  if (p.name) put('P01', 'Project Name', String(p.name).trim().slice(0, 150));
  const code = String(p.code || p.no || '').trim().toUpperCase().replace(/\s+/g, '-');
  if (/^[A-Z0-9]+(-[A-Z0-9]+)*$/.test(code) && code.length <= 20) put('P02', 'Project Code & Project Number', code);
  const em = EMIRATES[p.emirate];
  if (em) put('P04', 'Location / Emirate', em);
  // the PQP adds the emirate and UAE to the location, so the area loses its own ending
  let area = String(p.area || '').replace(/\s+/g, ' ').trim().replace(/,?\s*(uae|united arab emirates)\.?$/i, '');
  if (em) area = area.replace(new RegExp(',\\s*' + em + '\\.?$', 'i'), '');
  if (area) put('P05', 'Plot No. / Address', area);
  const types = PQP_TYPES.filter(([, rx]) => rx.test(String(p.sectors || '').toLowerCase())).map(([t]) => t);
  if (types.length) put('P06', 'Project Type', types, types.join(', '));
  if (p.scope) put('P07', 'Scope of Work (summary)', String(p.scope).trim().slice(0, 2000));
  if (isoOk(p.startDate)) put('P10', 'Commencement Date', p.startDate, fmtDate(p.startDate));
  if (isoOk(p.handoverDate)) put('P11', 'Completion Date', p.handoverDate, fmtDate(p.handoverDate));
  if (p.levels) put('P13', 'Building Configuration / Description', String(p.levels).trim().slice(0, 500));
  if (realName(p.client)) put('R01', 'Client / Employer', realName(p.client));
  const cons = realName(p.mepConsultant) || realName(p.leadConsultant);
  if (cons) put('R02', 'Consultant / Engineer', cons);
  if (realName(p.mainContractor)) put('R03', 'Main Contractor', realName(p.mainContractor));
  const au = pqpList(p.authorities, PQP_AUTH);
  if (au.list.length) { put('R06', 'Approving Authorities', au.list, au.list.filter(x => x !== 'Other').concat(au.other.map(x => x + ' (as Other)')).join(', ')); if (au.other.length) pr.R06other = au.other.join(', '); }
  const co = pqpList(p.codes, PQP_CODES);
  if (!co.list.includes('Project Specifications')) co.list.unshift('Project Specifications');   // ticked in every new PQP
  put('Q07', 'Applicable Codes & Standards', PQP_CODES.map(([o]) => o).filter(o => co.list.includes(o)).concat(co.other.length ? ['Other'] : []),
    PQP_CODES.map(([o]) => o).filter(o => co.list.includes(o)).concat(co.other.map(x => x + ' (as Other)')).join(', '));
  if (co.other.length) pr.Q07other = co.other.join(', ');
  return { pr, rows, otherAu: au.other, otherCo: co.other };
}
async function pqpPhoto(p) {
  const ph = photosOf(p)[0]; if (!ph) return null;
  const img = await loadImg(blobUrl(ph.id)), k = Math.min(1, 2000 / Math.max(img.naturalWidth, img.naturalHeight));
  const c = document.createElement('canvas'); c.width = Math.round(img.naturalWidth * k); c.height = Math.round(img.naturalHeight * k);
  const g = c.getContext('2d'); g.fillStyle = '#FFFFFF'; g.fillRect(0, 0, c.width, c.height); g.imageSmoothingQuality = 'high'; g.drawImage(img, 0, 0, c.width, c.height);
  return { name: `${safeName(p.name || p.no)} - Cover Photo.jpg`, type: 'image/jpeg', dataUrl: c.toDataURL('image/jpeg', 0.86), w: c.width, h: c.height };
}
const PQP_LEFT = ['Our Role', 'Disciplines', 'document control (revision, issue date, status, prepared, reviewed and approved by)', 'key personnel', 'ISO certificates', 'the amendment record'];
function openPqp(no) {
  const p = S.projects.get(no); if (!p) return;
  const { rows, otherAu, otherCo } = pqpData(p), hasPhoto = !!photosOf(p)[0];
  const cell = v => esc(Array.isArray(v) ? v.join(', ') : String(v)).replace(/\n/g, '<br>');
  openModal(`<div class="dialog">
    <div class="dialog-head"><h2>Send ${esc(p.no)} to PQP Maker</h2><button type="button" class="btn btn-ghost btn-sm" data-close>Close</button></div>
    <div class="dialog-body">
      <p style="margin:0">Saves <strong>${esc(safeName(p.name || p.no))}.pqp</strong>. In PQP Maker choose <strong>Open</strong> and pick the file: these details are filled in for you.</p>
      <div class="imp-table"><table><thead><tr><th>PQP Maker field</th><th>From the Library</th></tr></thead><tbody>
        ${rows.map(([l, v]) => `<tr><td>${esc(l)}</td><td>${cell(v)}</td></tr>`).join('')}
        <tr><td>Cover Photo</td><td>${hasPhoto ? 'The main library photo' : 'None in the library: PQP Maker shows the photo box'}</td></tr>
      </tbody></table></div>
      ${otherAu.length || otherCo.length ? `<p class="d-note" style="margin:0">Not in PQP Maker's lists, so they go in as “Other” text: ${esc(joinAnd(otherAu.concat(otherCo)))}. Check them in PQP Maker.</p>` : ''}
      <p class="d-note" style="margin:0">Left for you to fill in PQP Maker: ${esc(joinAnd(PQP_LEFT))}. Branding and the quality settings come from your PQP Maker settings.</p>
      <p class="err" id="pqp-err" hidden></p>
    </div>
    <div class="dialog-foot"><a class="btn" href="${PQP_URL}" target="_blank" rel="noopener">Open PQP Maker</a><button type="button" class="btn btn-primary" id="pqp-go">Save PQP file</button></div>
  </div>`);
  $('#pqp-go').addEventListener('click', async () => {
    const btn = $('#pqp-go'); btn.disabled = true; btn.textContent = 'Preparing…';
    try {
      const { pr } = pqpData(p);
      try { const ph = await pqpPhoto(p); if (ph) pr.R10 = ph; } catch (e) { /* no photo: PQP Maker shows the photo box */ }
      const file = { format: 'pqp-maker-project', version: 1, app: 'Oxypro Project Library ' + APP_VERSION, saved: new Date().toISOString(), source: { library: p.no }, project: pr };
      const ok = await saveFile(safeName(p.name || p.no) + '.pqp', new Blob([JSON.stringify(file, null, 1)], { type: 'application/json' }));
      if (ok) closeModal(); else { btn.disabled = false; btn.textContent = 'Save PQP file'; }
    } catch (e) { const er = $('#pqp-err'); er.textContent = 'The file could not be made: ' + ((e && e.message) || e); er.hidden = false; btn.disabled = false; btn.textContent = 'Save PQP file'; }
  });
}
"""
rep("/* ---------- Excel import / export ---------- */", JS.strip('\n') + "\n\n/* ---------- Excel import / export ---------- */")
rep("const CM = 96 / 2.54;", "const APP_VERSION = '1.7.0';\nconst CM = 96 / 2.54;")
open(P, 'w').write(s)
print('patched', len(s))
