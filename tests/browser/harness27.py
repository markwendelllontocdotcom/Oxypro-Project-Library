"""GitHub edition (1.11.0) as a plain website: served from site/ over http, no Claude runtime."""
import os, asyncio, subprocess, json
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'out27'); NM = '/home/claude/msra/node/node_modules'
LOCAL = {'jspdf.umd.min.js': 'jspdf/dist/jspdf.umd.min.js', 'xlsx.full.min.js': 'xlsx/dist/xlsx.full.min.js', 'exceljs.min.js': 'exceljs/dist/exceljs.min.js', 'jspdf.plugin.autotable.min.js': 'jspdf-autotable/dist/jspdf.plugin.autotable.min.js', 'pptxgen.bundle.js': '/home/claude/project-library/build/node_modules/pptxgenjs/dist/pptxgen.bundle.js'}
async def main():
    srv = subprocess.Popen(['python3', '-m', 'http.server', '8765', '--directory', os.path.join(ROOT, 'site')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1)
    try:
        async with async_playwright() as pw:
            br = await pw.chromium.launch()
            ctx = await br.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
            page = await ctx.new_page(); errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            async def route(r):
                url = r.request.url
                if url.startswith('http://localhost:8765/'): return await r.continue_()
                for k, p in LOCAL.items():
                    if url.endswith(k): return await r.fulfill(status=200, content_type='application/javascript', body=open(p if p.startswith('/') else os.path.join(NM, p), 'rb').read())
                return await r.abort()
            await ctx.route('**/*', route)
            await page.goto('http://localhost:8765/'); await page.wait_for_selector('.row'); await page.wait_for_timeout(800)
            print('rows:', await page.locator('.row').count(), '| edition:', (await page.inner_text('#edition'))[:120].replace('\n', ' '))
            print('buttons: add', await page.is_visible('#btn-add'), 'import', await page.is_visible('#btn-import'), 'export', await page.is_visible('#btn-export'))
            print('broken thumbs:', await page.evaluate("[...document.querySelectorAll('img.thumb')].filter(i => !i.complete || !i.naturalWidth).length"), 'of', await page.locator('img.thumb').count())
            await page.click('.row[data-no="P122"] .r-main'); await page.wait_for_timeout(400)
            print('edit button:', await page.locator('[data-act="edit"]').count(), '| detail photos ok:', await page.evaluate("[...document.querySelectorAll('#detail img')].every(i => i.naturalWidth > 0)"))
            await page.screenshot(path=os.path.join(OUT, '1-home.png'))
            # presentation PDF
            await page.click('[data-act="present"]'); await page.wait_for_timeout(1500)
            async with page.expect_download() as d: await page.click('#dl-pdf')
            dl = await d.value; p = os.path.join(OUT, dl.suggested_filename); await dl.save_as(p); print('pdf:', dl.suggested_filename, os.path.getsize(p))
            await page.click('#home-link'); await page.wait_for_timeout(300)
            # MSRA
            await page.click('[data-act="msra"]'); await page.wait_for_timeout(500)
            print('start hint:', (await page.inner_text('.ms-start .hint >> nth=1')) if await page.locator('.ms-start .hint').count() > 1 else '')
            await page.click('[data-ms-act="start"][data-how="std"]'); await page.wait_for_timeout(400)
            print('save label:', await page.inner_text('[data-ms-act="save"]'))
            await page.click('[data-ms-act="mode-edit"]'); await page.click('[data-ms-tab="MEC"]'); await page.wait_for_timeout(200)
            await page.locator('.ms-log tbody tr[data-id]').nth(0).locator('[data-k="fin"]').select_option('A')
            await page.click('[data-ms-act="save"]'); await page.wait_for_timeout(400)
            print('after save:', await page.inner_text('[data-ms-act="save"]'), '| toast:', await page.inner_text('#toast'))
            async with page.expect_download() as d:
                await page.click('[data-ms-act="saveas"]'); await page.click('[data-ms-act="save-xlsx"]')
            dl = await d.value; p = os.path.join(OUT, dl.suggested_filename); await dl.save_as(p); print('xlsx:', dl.suggested_filename, os.path.getsize(p))
            async with ctx.expect_page() as np: await page.click('[data-ms-act="print"]')
            pp = await np.value; print('print tab:', pp.url[:30], '| toast:', await page.inner_text('#toast'))
            await pp.close()
            # reload: the log is still there
            await page.reload(); await page.wait_for_selector('.row'); await page.wait_for_timeout(600)
            await page.click('.row[data-no="P122"] .r-main'); await page.wait_for_timeout(300)
            print('after reload button:', await page.inner_text('[data-act="msra"]'))
            await page.click('[data-act="msra"]'); await page.wait_for_timeout(500)
            print('reloaded strip MEC:', await page.inner_text('[data-ms-tab="MEC"]'), '| summary text:', (await page.inner_text('.ms-facts'))[:160].replace('\n', ' '))
            await page.screenshot(path=os.path.join(OUT, '2-msra.png'))
            await page.click('#home-link'); await page.wait_for_timeout(300)
            await page.click('#btn-about'); await page.wait_for_timeout(300)
            print('about data:', (await page.inner_text('.about section:nth-of-type(3)'))[:300].replace('\n', ' '))
            await page.keyboard.press('Escape')
            await page.set_viewport_size({'width': 390, 'height': 844}); await page.wait_for_timeout(300)
            await page.screenshot(path=os.path.join(OUT, '3-phone.png'))
            print('errors:', errors)
            await br.close()
    finally:
        srv.terminate()
asyncio.run(main())
