"""Render both top sheet designs from the app's real PDF/PPTX output (mocked window.claude)."""
import json, os, glob, base64, asyncio
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'out22'); os.makedirs(OUT, exist_ok=True)
SP = '/tmp/claude-0/-home-claude/0eb838aa-d16c-5b60-a2e1-bc2abae7b604/scratchpad'
NM = os.path.join(ROOT, 'build', 'node_modules')
page_html = open(os.path.join(ROOT, 'dist', 'Oxypro Project Library.html')).read()
docs = json.load(open(os.path.join(HERE, 'docs-1.7.json')))
BLOBS = json.load(open(os.path.join(ROOT, 'photos', 'db', '_blobmap.json')))
PHOTO = os.path.join(HERE, 'sample-photo.jpg')
PQPWEB = '/home/claude/markwendelllontocdotcom/mep-pqp-maker/dist/web'

MOCK = """
(() => {
  const store = new Map(%s.map(d => [d.no, d]));
  const listeners = [];
  const snap = () => ({ docs: [...store.entries()].sort().map(([id, d]) => ({ id, exists: true, data: () => JSON.parse(JSON.stringify(d)), metadata: {} })), size: store.size, empty: !store.size, metadata: {} });
  window.__set = {}; window.__sl = {};
  const db = {
    collection: () => ({ onSnapshot: (next) => { listeners.push(next); setTimeout(() => next(snap()), 30); return () => {}; },
      doc: (id) => ({ id, set: async (d) => { store.set(id, JSON.parse(JSON.stringify(d))); listeners.forEach(fn => setTimeout(() => fn(snap()), 5)); }, update: async (d) => { const o = store.get(id); const n = { ...o, ...JSON.parse(JSON.stringify(d)) }; if (d.extra) n.extra = { ...(o.extra || {}), ...d.extra }; store.set(id, n); listeners.forEach(fn => setTimeout(() => fn(snap()), 5)); }, delete: async () => {} }) }),
    doc: (path) => ({ onSnapshot: (next) => { (window.__sl[path] = window.__sl[path] || []).push(next); setTimeout(() => next({ exists: path in window.__set, data: () => window.__set[path] }), 30); return () => {}; },
      set: async (d) => { window.__set[path] = JSON.parse(JSON.stringify(d)); (window.__sl[path] || []).forEach(fn => fn({ exists: true, data: () => window.__set[path] })); } })
  };
  let n = 0;
  const ALLOW = /\\.(gif|png|jpe?g|webp|mp4|webm|mov|txt|json|md|docx|pptx|epub|csv|ttf|html|svg|pdf|xlsx|zip)$/i;
  const downloads = { save: async ({ filename, data }) => { if (!ALLOW.test(filename)) { const e = new Error('rejected'); e.code = 'rejected_extension'; throw e; } const u = new Uint8Array(await new Response(data).arrayBuffer()); let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); await window.__save((++n) + '-' + filename, btoa(s)); return { status: 'saved' }; } };
  const caps = { db, downloads, assets: { upload: async () => ({}), delete: async () => ({}) }, user: { can: async () => true } };
  window.__dump = () => JSON.stringify([...store.values()]);
  window.claude = { use: (k) => new Promise(r => setTimeout(() => r(caps[k] || null), 40)) };
})();
""" % json.dumps(docs)

def wrap(html):
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{{color-scheme:light}}body{{margin:0;font:14px system-ui}}img{{max-width:100%}}[hidden]{{display:none!important}}</style><script>{MOCK}</script></head><body>{html}</body></html>'
LOCAL = {'jspdf.umd.min.js': 'jspdf/dist/jspdf.umd.min.js', 'pptxgen.bundle.js': 'pptxgenjs/dist/pptxgen.bundle.js', 'xlsx.full.min.js': 'xlsx/dist/xlsx.full.min.js'}
saved = []

async def setup(ctx):
    page = await ctx.new_page(); errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    async def save(name, b64):
        p = os.path.join(OUT, name); open(p, 'wb').write(base64.b64decode(b64)); saved.append(p); return True
    await page.expose_function('__save', save)
    async def route(r):
        url = r.request.url
        if '/_blob/' in url:
            bid = url.rsplit('/', 1)[-1]
            return await r.fulfill(status=200, content_type='image/jpeg', body=open(BLOBS[bid], 'rb').read()) if bid in BLOBS else await r.fulfill(status=404, body='')
        if url.startswith('https://markwendelllontocdotcom.github.io/MEP-PQP-Maker/'):
            rel = url.split('/MEP-PQP-Maker/', 1)[1].split('#')[0].split('?')[0] or 'index.html'
            fp = os.path.join(PQPWEB, rel)
            if os.path.isfile(fp):
                ct = {'html': 'text/html', 'js': 'application/javascript', 'css': 'text/css', 'png': 'image/png', 'ico': 'image/x-icon', 'json': 'application/json', 'webmanifest': 'application/manifest+json', 'woff2': 'font/woff2', 'ttf': 'font/ttf', 'svg': 'image/svg+xml', 'jpg': 'image/jpeg'}.get(rel.rsplit('.', 1)[-1], 'application/octet-stream')
                return await r.fulfill(status=200, content_type=ct, body=open(fp, 'rb').read())
            return await r.fulfill(status=404, body='')
        if url.startswith('https://test.local/'): return await r.fulfill(status=200, content_type='text/html', body=wrap(page_html))
        for k, p in LOCAL.items():
            if url.endswith(k): return await r.fulfill(status=200, content_type='application/javascript', body=open(os.path.join(NM, p), 'rb').read())
        return await r.abort()
    await ctx.route('**/*', route)
    await page.goto('https://test.local/index.html'); await page.wait_for_selector('.row')
    return page, errors

async def dl(page, sel):
    n = len(saved); await page.click(sel)
    for _ in range(60):
        await page.wait_for_timeout(250)
        if len(saved) > n: return saved[-1]
    raise RuntimeError('no download for ' + sel)





async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        ctx = await br.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block')
        page, errors = await setup(ctx)
        await page.wait_for_timeout(500)
        print('footer:', await page.inner_text('#version'))
        for no in ['P122', 'P120', 'P100']:
            await page.click(f'.row[data-no="{no}"] .r-main'); await page.wait_for_timeout(400)
            await page.click('[data-act="pqp"]'); await page.wait_for_timeout(400)
            if no == 'P122': print('dialog text:', (await page.inner_text('#pqp-how'))[-120:])
            f = await dl(page, '#pqp-go'); print(no, '->', os.path.basename(f).split('-', 1)[1])
        print('errors:', errors)
        await br.close()
asyncio.run(main())
