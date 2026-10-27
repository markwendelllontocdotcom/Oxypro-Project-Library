"""v1.10.2: About the Oxypro Project Library: a dialog from the About button in the header and the footer link,
with what the app does, how to use it, where the data lives, related apps, the version history and credits."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('Version 1.10.1 (27 Oct 2026)', 'Version 1.10.2 (27 Oct 2026)')
rep("const APP_VERSION = '1.10.1';", "const APP_VERSION = '1.10.2';")
# header button after the View menu, footer link after the version
rep("""          <button type="button" class="menu-item" role="menuitemradio" aria-checked="false" data-view-opt="auto">""", """          <button type="button" class="menu-item" role="menuitemradio" aria-checked="false" data-view-opt="auto">""")
i = s.index('<div class="menu" id="view-menu"'); j = s.index('</div>\n      </div>', i) + len('</div>\n      </div>')
s = s[:j] + """
      <button type="button" class="btn" id="btn-about" aria-haspopup="dialog" title="About the Oxypro Project Library"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><circle cx="12" cy="7.6" r=".6" fill="currentColor"/></svg>About</button>""" + s[j:]
rep("""    <span id="version">Version 1.10.2 (27 Oct 2026)</span>""", """    <span id="version">Version 1.10.2 (27 Oct 2026)</span> · <button type="button" class="linkbtn" id="foot-about" aria-haspopup="dialog">About this app</button>""")
rep(""".foot{padding-block:26px 120px;""", """.linkbtn{border:0;background:none;padding:0;font:inherit;color:var(--red-text);cursor:pointer;text-decoration:underline;text-underline-offset:2px}
.dialog-about{width:min(860px,100%)}
.about{display:flex;flex-direction:column;gap:20px;font-size:14.5px;line-height:1.55}
.about-card{display:flex;flex-wrap:wrap;gap:14px 20px;align-items:center;padding-bottom:16px;border-bottom:1px solid var(--line)}
.about-card .logo{height:52px}
.about-name{font:600 26px/1.05 var(--f-cond);letter-spacing:.03em;text-transform:uppercase}
.about-ver{color:var(--muted);font-size:13.5px;margin-top:3px}
.about-tag{margin:6px 0 0;color:var(--fg-2);max-width:62ch}
.about h3{margin:0 0 6px;font:600 14px var(--f-cond);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.about p{margin:0 0 8px}
.about ul,.about ol{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:5px}
.about b{font-weight:600}
.about-changes{display:flex;flex-direction:column;gap:8px}
.about-changes div{display:grid;grid-template-columns:92px minmax(0,1fr);gap:4px 12px}
.about-changes dt{font-weight:600;font-variant-numeric:tabular-nums}
.about-changes dt small{display:block;font-weight:400;color:var(--muted);font-size:12px}
.about-changes dd{margin:0}
.about-credit{color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:14px}
@media (max-width:560px){.about-changes div{grid-template-columns:minmax(0,1fr)}}
.foot{padding-block:26px 120px;""")
ABOUT = r"""
/* ---------- About ---------- */
const ABOUT_CHANGES = [
  ['1.10.2', '27 Oct 2026', 'This About page (About in the header and in the footer).'],
  ['1.10.1', '27 Oct 2026', 'The PROJECT LIBRARY title goes back to the library list from any page.'],
  ['1.10.0', '27 Oct 2026', 'MSRA Log: each project\'s Method Statement Log in the Oxypro template (standard list of 72, the project\'s MSL or an empty log), edited and saved in the library, saved as Excel or PDF and printed, in Open Sans.'],
  ['1.9.0 – 1.9.2', '27 Oct 2026', 'PQP details and file: choose the cover photo for the PQP; files named with the project number, name and revision; saved as .pqp.json.'],
  ['1.8.0 – 1.8.1', '27 Oct 2026', 'Open in PQP Maker creates the project\'s PQP directly in PQP Maker.'],
  ['1.7.0', '27 Oct 2026', 'Project Code, Approving Authorities and Codes & Standards from the updated Master List.'],
  ['1.6.0', '27 Oct 2026', 'View / Present: run the presentation full screen before saving it.'],
  ['1.5.0', '27 Oct 2026', 'Project summary page at the end of a presentation; extra Master List columns kept as project details.'],
  ['1.2.0 – 1.4.0', '27 Oct 2026', 'Top sheet (cover) in four designs, with or without a photo.'],
  ['1.1.0', '27 Oct 2026', 'Import from and export to the Projects Master List; Handover Stage status; Light, Dark and Auto view.'],
  ['1.0.0', '24 Oct 2026', 'First version: the 17 Oxypro projects, project photos and the Project Presentation Sheet as PDF and PowerPoint.']
];
function openAbout() {
  const n = S.projects.size, w = canWrite();
  openModal(`<div class="dialog dialog-about" role="dialog" aria-modal="true" aria-labelledby="about-title">
    <div class="dialog-head"><h2 id="about-title">About</h2><button type="button" class="btn btn-ghost btn-sm" data-close>Close</button></div>
    <div class="dialog-body about">
      <div class="about-card">
        <img class="logo logo-l" src="${logoSrc(false)}" alt="Oxypro"><img class="logo logo-d" src="${logoSrc(true)}" alt="Oxypro">
        <div><div class="about-name">Oxypro Project Library</div><div class="about-ver">Version ${APP_VERSION} · 27 Oct 2026${n ? ` · ${n} projects` : ''}</div>
          <p class="about-tag">One shared library of Oxypro Electromechanical's projects: project details and photos, presentation sheets, the Project Quality Plan hand-off to PQP Maker and each project's Method Statement Log.</p></div>
      </div>
      <section><h3>What it does</h3>
        <ul>
          <li><b>Projects:</b> search and filter by emirate, status and sector; each project shows its details from the Projects Master List and up to five photos.</li>
          <li><b>Presentations:</b> select one or more projects for a top sheet, an Oxypro Project Presentation Sheet per project and a summary page, as PDF or PowerPoint; View / Present runs them full screen first.</li>
          <li><b>PQP details and file:</b> opens PQP Maker with the project's PQP already created, or saves a PQP file.</li>
          <li><b>MSRA Log:</b> the project's Method Statement Submittal Log in the Oxypro template, with the Summary, seven discipline logs and the planner's MSL, saved as Excel or PDF.</li>
          <li><b>Master List:</b> add projects, import from the Projects Master List (Excel) and export the whole list in the same layout.</li>
        </ul></section>
      <section><h3>How to use it</h3>
        <ol>
          <li>Find a project with the search box or the filters and click it to see its details and photos.</li>
          <li>For a presentation, tick the projects and choose <b>Make presentation</b>, or use <b>New presentation sheet</b> on one project. Adjust photos and text, then <b>View / Present</b>, <b>Download PDF</b> or <b>Download PowerPoint</b>.</li>
          <li>For a PQP, open the project and choose <b>PQP details and file</b>, pick the cover photo, then <b>Open in PQP Maker</b>.</li>
          <li>For the Method Statement Log, choose <b>Create MSRA Log</b> (or <b>Open MSRA Log</b>). Use <b>Edit</b> to change it, <b>Save to library</b> to keep it, <b>Save as</b> for Excel or PDF and <b>Print</b> for a print-ready PDF.</li>
          <li>Click <b>Project Library</b> at the top to come back to the list from any page. <b>View</b> switches between Light, Dark and Auto.</li>
        </ol></section>
      <section><h3>Your data</h3>
        <ul>
          <li>Projects, photos and MSRA Logs are kept in this shared library in Claude. Everyone with the link sees the same, up-to-date list.</li>
          <li>Only the library's owner and editors can add or change projects, photos and MSRA Logs${w ? ' (you can)' : ' (you can view, make presentations and download files)'}.</li>
          <li>Files you make (PDF, PowerPoint, Excel, PQP files) are downloaded to your device. Printing is done from the downloaded PDF, as Claude cannot open the print window.</li>
          <li>Open in PQP Maker passes the project's text details to PQP Maker in its link; the cover photo goes by copy and paste. Nothing else leaves the library.</li>
        </ul></section>
      <section><h3>Related</h3>
        <ul>
          <li><a href="${PQP_URL}" target="_blank" rel="noopener">PQP Maker</a>: Project Quality Plans in the Oxypro template (opens in a new tab).</li>
          <li>Projects Master List (Excel): the source of the project details, imported and exported here.</li>
        </ul></section>
      <section><h3>What's new</h3>
        <dl class="about-changes">${ABOUT_CHANGES.map(([v, d, t]) => `<div><dt>${esc(v)}<small>${esc(d)}</small></dt><dd>${esc(t)}</dd></div>`).join('')}</dl></section>
      <p class="about-credit">Developed by Mark Lontoc | Dubai, United Arab Emirates | © 2026 MLWorks. All rights reserved.<br>
        Fonts: Barlow; Caladea and Carlito on the presentation sheets; Open Sans by Steve Matteson in the MSRA Log. Built with jsPDF, jsPDF-AutoTable, PptxGenJS, SheetJS and ExcelJS.</p>
    </div>
    <div class="dialog-foot"><button type="button" class="btn btn-primary" data-close>Close</button></div>
  </div>`);
  const c = document.querySelector('#modal .dialog-head [data-close]'); if (c) c.focus();
}
"""
rep("""/* the PROJECT LIBRARY title: back to the library list from anywhere */""", ABOUT.strip('\n') + "\n\n/* the PROJECT LIBRARY title: back to the library list from anywhere */")
rep("""  $('#home-link').addEventListener('click', goHome);""", """  $('#home-link').addEventListener('click', goHome);
  $('#btn-about').addEventListener('click', openAbout);
  $('#foot-about').addEventListener('click', openAbout);""")
open(P, 'w').write(s)
print('patched', len(s))
