"""MSRA Log (1.10.0): create, edit, save, MSL upload, Excel / PDF / print, reopen (mocked window.claude)."""
import json, os, base64, asyncio, sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'out23'); os.makedirs(OUT, exist_ok=True)
NM = '/home/claude/msra/node/node_modules'
page_html = open(os.path.join(ROOT, 'dist', 'Oxypro Project Library.html')).read()
docs = json.load(open(os.path.join(HERE, 'docs-1.7.json')))
BLOBS = json.load(open(os.path.join(ROOT, 'photos', 'db', '_blobmap.json')))
WRITE = os.environ.get('WRITE', '1') == '1'

MOCK = """
(() => {
  const stores = { projects: new Map(%s.map(d => [d.no, d])) };
  const st = n => stores[n] || (stores[n] = new Map());
  const colL = {}, docL = {};
  const clone = x => JSON.parse(JSON.stringify(x));
  const csnap = n => ({ docs: [...st(n).entries()].sort().map(([id, d]) => ({ id, exists: true, data: () => clone(d) })), size: st(n).size });
  const dsnap = (n, id) => ({ id, exists: st(n).has(id), data: () => st(n).has(id) ? clone(st(n).get(id)) : undefined });
  const fire = (n, id) => { (colL[n] || []).forEach(fn => setTimeout(() => fn(csnap(n)), 5)); (docL[n + '/' + id] || []).forEach(fn => setTimeout(() => fn(dsnap(n, id)), 5)); };
  const docRef = (n, id) => ({ id,
    get: async () => dsnap(n, id),
    set: async d => { st(n).set(id, clone(d)); fire(n, id); },
    update: async d => { const o = st(n).get(id) || {}; st(n).set(id, { ...o, ...clone(d) }); fire(n, id); },
    delete: async () => { st(n).delete(id); fire(n, id); },
    onSnapshot: (next) => { (docL[n + '/' + id] = docL[n + '/' + id] || []).push(next); setTimeout(() => next(dsnap(n, id)), 30); return () => { docL[n + '/' + id] = docL[n + '/' + id].filter(f => f !== next); }; } });
  const db = {
    collection: n => ({ onSnapshot: next => { (colL[n] = colL[n] || []).push(next); setTimeout(() => next(csnap(n)), 30); return () => {}; }, doc: id => docRef(n, id) }),
    doc: path => { const [n, id] = path.split('/'); return docRef(n, id); }
  };
  window.__stores = stores; window.__fire = fire;
  let k = 0;
  const ALLOW = /\\.(gif|png|jpe?g|webp|mp4|webm|mov|txt|json|md|docx|pptx|epub|csv|ttf|html|svg|pdf|xlsx|zip)$/i;
  const downloads = { save: async ({ filename, data }) => { if (!ALLOW.test(filename)) { const e = new Error('rejected'); e.code = 'rejected_extension'; throw e; } const u = new Uint8Array(await new Response(data).arrayBuffer()); let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); await window.__save((++k) + '-' + filename, btoa(s)); return { status: 'saved' }; } };
  const caps = { db, downloads, assets: { upload: async () => ({}), delete: async () => ({}) }, user: { can: async () => %s } };
  window.claude = { use: (k) => new Promise(r => setTimeout(() => r(caps[k] || null), 40)) };
})();
""" % (json.dumps(docs), 'true' if WRITE else 'false')

def wrap(html):
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style><script>{MOCK}</script></head><body>{html}</body></html>'
LOCAL = {'jspdf.umd.min.js': 'jspdf/dist/jspdf.umd.min.js', 'xlsx.full.min.js': 'xlsx/dist/xlsx.full.min.js', 'exceljs.min.js': 'exceljs/dist/exceljs.min.js', 'jspdf.plugin.autotable.min.js': 'jspdf-autotable/dist/jspdf.plugin.autotable.min.js'}
saved = []; requested = []

async def setup(ctx):
    page = await ctx.new_page(); errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append('console: ' + m.text) if m.type == 'error' else None)
    async def save(name, b64):
        p = os.path.join(OUT, name); open(p, 'wb').write(base64.b64decode(b64)); saved.append(p); return True
    await page.expose_function('__save', save)
    async def route(r):
        url = r.request.url
        if '/_blob/' in url:
            bid = url.rsplit('/', 1)[-1]
            return await r.fulfill(status=200, content_type='image/jpeg', body=open(BLOBS[bid], 'rb').read()) if bid in BLOBS else await r.fulfill(status=404, body='')
        if url.startswith('https://test.local/'): return await r.fulfill(status=200, content_type='text/html', body=wrap(page_html))
        for k, p in LOCAL.items():
            if url.endswith(k): requested.append(url); return await r.fulfill(status=200, content_type='application/javascript', body=open(os.path.join(NM, p), 'rb').read())
        return await r.abort()
    await ctx.route('**/*', route)
    await page.goto('https://test.local/index.html'); await page.wait_for_selector('.row')
    return page, errors

async def dl(page, sel):
    n = len(saved); await page.click(sel)
    for _ in range(120):
        await page.wait_for_timeout(250)
        if len(saved) > n: return saved[-1]
    raise RuntimeError('no download for ' + sel)

async def shot(page, name, full=False):
    await page.screenshot(path=os.path.join(OUT, name), full_page=full)

async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        ctx = await br.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block')
        page, errors = await setup(ctx)
        await page.wait_for_timeout(500)
        print('footer:', await page.inner_text('#version'))
        await page.click('.row[data-no="P122"] .r-main'); await page.wait_for_timeout(300)
        print('button:', await page.inner_text('[data-act="msra"]'))
        await shot(page, '01-detail.png')
        await page.click('[data-act="msra"]'); await page.wait_for_timeout(400)
        await shot(page, '02-start.png')
        await page.click('[data-ms-act="start"][data-how="std"]'); await page.wait_for_timeout(500)
        print('tabs:', await page.inner_text('.ms-tabs'))
        print('save btn:', await page.inner_text('[data-ms-act="save"]'))
        await shot(page, '03-summary.png')
        await page.click('[data-ms-tab="MEC"]'); await page.wait_for_timeout(300)
        await shot(page, '04-mec-view.png')
        await page.click('[data-ms-act="mode-edit"]'); await page.wait_for_timeout(300)
        rows = page.locator('.ms-log tbody tr[data-id]')
        print('MEC rows:', await rows.count())
        r1 = rows.nth(0)
        await r1.locator('[data-k="b"]').fill('U-1001')
        await r1.locator('[data-k="ref"]').fill('OXY-BRH-MS-001')
        await r1.locator('[data-k="plan"]').fill('2026-10-20')
        await r1.locator('[data-k="sub"]').fill('2026-10-21')
        await r1.locator('[data-k="ret"]').fill('2026-10-29')
        await r1.locator('[data-k="st"]').select_option('A'); await r1.locator('[data-k="fin"]').select_option('A')
        r2 = rows.nth(1); await r2.locator('[data-k="plan"]').fill('2026-10-01'); await r2.locator('[data-k="fin"]').select_option('UR')
        print('review:', await r1.locator('[data-rv]').inner_text(), 'strip:', await page.inner_text('.ms-strip'))
        # add, type ALL CAPS title, move up, remove
        await page.click('[data-ms-act="add"][data-st="I"]'); await page.wait_for_timeout(200)
        ta = page.locator('.ms-log tbody tr[data-id] textarea[data-k="t"]').nth(16)
        await ta.fill('INSTALLATION OF VRF OUTDOOR UNITS & REFRIGERANT PIPES'); await ta.press('Tab')
        print('title case:', await ta.input_value())
        await page.locator('.ms-log tbody tr[data-id]').nth(16).locator('[data-ms-act="up"]').click(); await page.wait_for_timeout(150)
        print('moved:', await page.locator('.ms-log tbody tr[data-id]').nth(15).locator('textarea[data-k="t"]').input_value())
        await page.locator('.ms-log tbody tr[data-id]').nth(3).locator('[data-ms-act="rm"]').click(); await page.wait_for_timeout(150)
        await page.click('[data-ms-act="rm-yes"]'); await page.wait_for_timeout(200)
        print('MEC rows now:', await page.locator('.ms-log tbody tr[data-id]').count())
        await page.locator('[data-bl="0"][data-f="value"]').fill('THE BOROUGH - RESIDENTIAL PROJECT (G+5P+17F+R), PLOT NO. JVC17TCP001B, JVC, DUBAI (DXB-243)')
        await shot(page, '05-mec-edit.png')
        await page.click('[data-ms-act="save"]'); await page.wait_for_timeout(500)
        st = json.loads(await page.evaluate("JSON.stringify({log: window.__stores.mslogs && window.__stores.mslogs.get('P122'), meta: window.__stores.mslogmeta && window.__stores.mslogmeta.get('P122')})"))
        print('saved items:', len(st['log']['items']), 'meta:', st['meta'], 'size', len(json.dumps(st['log'])))
        print('save btn after:', await page.inner_text('[data-ms-act="save"]'), '| notice:', await page.locator('.ms-notice').count())
        # MSL upload
        async with page.expect_file_chooser() as fc: await page.click('[data-ms-act="msl-up"]')
        await (await fc.value).set_files('/home/claude/msra/msl/cbd2.xlsx'); await page.wait_for_timeout(1200)
        print('dialog:', (await page.inner_text('.dialog-body'))[:400].replace('\n', ' | '))
        await shot(page, '06-msl-dialog.png')
        await page.check('#msl-fill') if await page.locator('#msl-fill').count() else None
        await page.click('#msl-go'); await page.wait_for_timeout(500)
        await shot(page, '07-msl-tab.png')
        print('msl top:', (await page.inner_text('.ms-msl-top'))[:300].replace('\n', ' | '))
        # planned dates from the MSL: type two material dates, fill
        await page.locator('.ms-msl tbody tr[data-k="ELE-03"] input[type=date]').fill('2026-11-01')
        await page.locator('.ms-msl tbody tr[data-k="ELE-07"] input[type=date]').fill('2026-11-14')
        await page.click('[data-ms-act="fill"]'); await page.wait_for_timeout(300)
        lg = json.loads(await page.evaluate("JSON.stringify(MSV.log.items.filter(it => it.d === 'ELE').slice(0, 1).map(it => [it.t, it.plan, it.m]))")) if False else None
        # link an uncovered material and add a MOS for another
        unc = page.locator('.ms-msl tbody tr.ms-unc')
        print('uncovered rows:', await unc.count())
        await unc.nth(0).locator('[data-ms-act="mat-add"]').click(); await page.wait_for_timeout(200)
        await shot(page, '08-add-mos.png')
        await page.check('#ms-a-tc'); await page.click('#ms-a-ok'); await page.wait_for_timeout(300)
        await page.locator('.ms-msl tbody tr.ms-unc').nth(0).locator('[data-ms-act="mat-link"]').click(); await page.wait_for_timeout(200)
        await page.locator('#ms-link input[type=checkbox]').nth(0).check(); await page.click('#ms-link-ok'); await page.wait_for_timeout(300)
        print('uncovered after:', await page.locator('.ms-msl tbody tr.ms-unc').count())
        await page.click('[data-ms-tab="ELE"]'); await page.wait_for_timeout(300)
        await page.locator('.ms-log tbody tr[data-id]').nth(0).locator('[data-ms-act="mats"]').click(); await page.wait_for_timeout(200)
        await shot(page, '09-mats.png')
        await page.click('#ms-mats-ok'); await page.wait_for_timeout(200)
        # files
        await page.click('[data-ms-act="saveas"]'); await page.wait_for_timeout(150); await shot(page, '10-saveas.png')
        f = await dl(page, '[data-ms-act="save-xlsx"]'); print('xlsx ->', os.path.basename(f))
        await page.click('[data-ms-act="saveas"]'); await page.wait_for_timeout(150)
        f = await dl(page, '[data-ms-act="save-pdf"]'); print('pdf ->', os.path.basename(f))
        f = await dl(page, '[data-ms-act="print"]'); print('print ->', os.path.basename(f))
        await page.click('[data-ms-act="save"]'); await page.wait_for_timeout(500)
        # leave and come back
        await page.click('[data-ms-act="back"]'); await page.wait_for_timeout(400)
        print('button after save:', await page.inner_text('[data-act="msra"]'))
        await page.click('[data-act="msra"]'); await page.wait_for_timeout(600)
        print('reopened tabs:', await page.inner_text('.ms-tabs'))
        # unsaved change then back: asks
        await page.click('[data-ms-act="mode-edit"]'); await page.click('[data-ms-tab="PLU"]'); await page.wait_for_timeout(200)
        await page.locator('.ms-log tbody tr[data-id]').nth(0).locator('[data-k="rem"]').fill('Test remark')
        await page.click('[data-ms-act="back"]'); await page.wait_for_timeout(200)
        print('leave dialog:', (await page.inner_text('.dialog')).replace('\n', ' | ')[:200])
        await page.click('#ms-leave-discard'); await page.wait_for_timeout(300)
        print('view after discard:', await page.evaluate('S.view') if False else await page.evaluate("document.querySelector('#view-library').hidden"))
        # remote change while editing
        await page.click('[data-act="msra"]'); await page.wait_for_timeout(600)
        await page.click('[data-ms-act="mode-edit"]'); await page.click('[data-ms-tab="FF"]'); await page.wait_for_timeout(200)
        await page.locator('.ms-log tbody tr[data-id]').nth(0).locator('[data-k="rem"]').fill('Mine')
        await page.evaluate("(() => { const d = window.__stores.mslogs.get('P122'); d.updatedAt = new Date(Date.now() + 1000).toISOString(); d.items[0].rem = 'Theirs'; window.__fire('mslogs', 'P122'); })()"); await page.wait_for_timeout(300)
        print('remote notice:', await page.locator('.ms-notice').count())
        await page.emulate_media(color_scheme='dark'); await page.wait_for_timeout(200)
        await shot(page, '11-dark-edit.png')
        await page.click('[data-ms-act="load-remote"]'); await page.wait_for_timeout(300)
        await page.emulate_media(color_scheme='light')
        await page.click('[data-ms-tab="SUM"]'); await page.wait_for_timeout(200); await shot(page, '12-summary-after.png', True)
        await page.set_viewport_size({'width': 390, 'height': 844}); await page.wait_for_timeout(300)
        await page.click('[data-ms-tab="MEC"]'); await page.wait_for_timeout(200)
        await shot(page, '13-phone.png')
        sw = await page.evaluate('document.documentElement.scrollWidth'); print('phone scrollWidth:', sw)
        print('requested:', sorted(set(u.rsplit('/', 1)[-1] for u in requested)))
        print('errors:', errors)
        await br.close()
asyncio.run(main())
