"""v1.4.0: every presentation can use any of the four top sheet designs; the library keeps a default for new presentations."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'library.html')
s = open(P).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('Version 1.3.0 (27 Oct 2026)', 'Version 1.4.0 (27 Oct 2026)')
rep(".flabel{font-weight:600;font-size:13.5px}",
    ".flabel{font-weight:600;font-size:13.5px}\n.def-row{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px}")
# per-presentation design, starting from the library default
rep("const CLEAN = d => d === 'C' || d === 'D';",
    "const CLEAN = d => d === 'C' || d === 'D';\nconst curDesign = () => (S.pres.cover && S.pres.cover.design) || S.coverDesign;")
rep("    include: true, title: n === 1 ? 'Project Profile' : 'Project References',",
    "    include: true, design: S.coverDesign, title: n === 1 ? 'Project Profile' : 'Project References',")
rep("  const ph = coverPhoto(S.pres.cover, S.pres.sheets, S.coverDesign);\n  const bg = await coverBg(S.coverDesign, ph, dpi);",
    "  const ph = coverPhoto(S.pres.cover, S.pres.sheets, curDesign());\n  const bg = await coverBg(curDesign(), ph, dpi);")
rep("  const L = coverLayout(S.coverDesign, S.pres.cover, S.pres.sheets);", "  const L = coverLayout(curDesign(), S.pres.cover, S.pres.sheets);")
rep("esc(DESIGNS[S.coverDesign].join(' · '))", "esc(DESIGNS[curDesign()].join(' · '))")
rep("  const cv = S.pres.cover, d = S.coverDesign, w = canWrite(), key = photoKey(cv, d);",
    "  const cv = S.pres.cover, d = curDesign(), w = canWrite(), key = photoKey(cv, d), def = S.coverDesign;")
rep("""      <span class="hint">${w ? 'The design you choose is used for every presentation.' : 'Only library editors can change the design for everyone; this choice applies to this presentation.'}</span></div>""",
    """      <div class="def-row">${d === def ? `<span class="hint">${DESIGNS[d][0]} is the default for new presentations.</span>`
        : w ? `<button type="button" class="btn btn-sm" data-set-default>Make ${DESIGNS[d][0]} the default</button><span class="hint">New presentations start with ${DESIGNS[def][0]}.</span>`
        : `<span class="hint">New presentations start with ${DESIGNS[def][0]}.</span>`}</div></div>""")
rep("""async function setDesign(d) {
  if (!DESIGNS[d] || d === S.coverDesign) return;
  S.coverDesign = d; renderRail(); buildCover(); renderCoverForm();
  if (!canWrite()) return;
  try { await DB.doc('settings/cover').set({ design: d, updatedAt: new Date().toISOString() }); toast(`${DESIGNS[d][0]} is now the top sheet for every presentation`); }
  catch (e) { toast(writeError(e)); }
}""",
    """function setDesign(d) {
  const cv = S.pres.cover;
  if (!cv || !DESIGNS[d] || d === cv.design) return;
  cv.design = d; if (!cv.edited.includes('design')) cv.edited.push('design');
  renderRail(); buildCover(); renderCoverForm();
}
async function setDefaultDesign() {
  const d = curDesign(); if (!canWrite() || d === S.coverDesign) return;
  try {
    await DB.doc('settings/cover').set({ design: d, updatedAt: new Date().toISOString() });
    S.coverDesign = d; renderCoverForm(); queueThumbs();
    toast(`${DESIGNS[d][0]} is now the default for new presentations`);
  } catch (e) { toast(writeError(e)); }
}""")
rep("    const [, , bw, bh] = PHOTO_BOX[S.coverDesign], sc", "    const [, , bw, bh] = PHOTO_BOX[curDesign()], sc")
rep("    const cv = S.pres.cover, ph = coverPhoto(cv, S.pres.sheets, S.coverDesign); if (!ph) return;\n    const gm",
    "    const cv = S.pres.cover, ph = coverPhoto(cv, S.pres.sheets, curDesign()); if (!ph) return;\n    const gm")
rep("[bx, by, bw, bh] = PHOTO_BOX[S.coverDesign];", "[bx, by, bw, bh] = PHOTO_BOX[curDesign()];")
rep("    const cv = S.pres.cover, ph = coverPhoto(cv, S.pres.sheets, S.coverDesign); if (!ph) return;\n    e.preventDefault(); cv.focus",
    "    const cv = S.pres.cover, ph = coverPhoto(cv, S.pres.sheets, curDesign()); if (!ph) return;\n    e.preventDefault(); cv.focus")
rep("  const design = S.coverDesign, bg = await coverBg(design, coverPhoto(cv, sheets, design), 200);",
    "  const design = cv.design || S.coverDesign, bg = await coverBg(design, coverPhoto(cv, sheets, design), 200);")
rep("  const design = S.coverDesign, sl = pptx.addSlide();", "  const design = cv.design || S.coverDesign, sl = pptx.addSlide();")
rep("    const d = e.target.closest('[data-design]'); if (d) return setDesign(d.dataset.design);",
    "    const d = e.target.closest('[data-design]'); if (d) return setDesign(d.dataset.design);\n    if (e.target.closest('[data-set-default]')) return setDefaultDesign();")
rep("""    S.coverDesign = v;
    if (S.view === 'pres') { renderRail(); if (S.pres.cur === -1) { buildCover(); renderCoverForm(); } }""",
    """    S.coverDesign = v;
    const cv = S.pres.cover; if (cv && !cv.edited.includes('design')) cv.design = v;
    if (S.view === 'pres') { renderRail(); if (S.pres.cur === -1) { buildCover(); renderCoverForm(); } }""")
print('\n'.join(l.strip()[:110] for l in s.splitlines() if 'S.coverDesign' in l))
open(P, 'w').write(s)
print('patched', len(s))
