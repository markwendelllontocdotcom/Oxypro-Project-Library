"""MSRA Log (1.10.0): create, edit, save, MSL upload, Excel / PDF / print, reopen (mocked window.claude)."""
import json, os, base64, asyncio, sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'out25'); os.makedirs(OUT, exist_ok=True)
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


async def vis(page):
    return {k: not await page.evaluate(f"document.querySelector('#{k}').hidden") for k in ['view-library','view-pres','view-msra']}
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        ctx = await br.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block')
        page, errors = await setup(ctx)
        await page.wait_for_timeout(500)
        print('title:', await page.inner_text('#home-link'), await page.get_attribute('#home-link','title'))
        await page.click('.row[data-no="P115"] .r-main'); await page.wait_for_timeout(300)
        await page.click('[data-act="present"]'); await page.wait_for_timeout(800)
        print('pres:', await vis(page))
        await page.click('#home-link'); await page.wait_for_timeout(400)
        print('after title:', await vis(page))
        await page.click('[data-act="msra"]'); await page.wait_for_timeout(400)
        await page.click('[data-ms-act="start"][data-how="std"]'); await page.wait_for_timeout(300)
        await page.click('#home-link'); await page.wait_for_timeout(300)
        print('unsaved dialog:', await page.locator('.dialog h2').inner_text() if await page.locator('.dialog').count() else None, await vis(page))
        await page.click('#ms-leave-discard'); await page.wait_for_timeout(300)
        print('after discard:', await vis(page), 'scrollY', await page.evaluate('scrollY'))
        await page.hover('#home-link'); await page.screenshot(path=os.path.join(OUT,'hover.png'), clip={'x':0,'y':0,'width':900,'height':130})
        await page.set_viewport_size({'width': 390, 'height': 844}); await page.wait_for_timeout(200)
        await page.click('.row[data-no="P119"] .r-main'); await page.wait_for_timeout(300)
        print('mobile panel open:', await page.evaluate("document.querySelector('#detail').classList.contains('open')"))
        print('title visible behind panel:', await page.evaluate("(() => { const r = document.querySelector('#home-link').getBoundingClientRect(); const e = document.elementFromPoint(r.x+5, r.y+5); return e && e.id; })()"))
        print('errors:', [e for e in errors if 'Failed to load' not in e])
        await br.close()
asyncio.run(main())
