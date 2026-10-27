import json, os
here=os.path.dirname(os.path.abspath(__file__))
a=json.load(open(os.path.join(here,'build','assets.json')))
s=open(os.path.join(here,'src','library.html')).read()
ic=json.load(open(os.path.join(here,'build','app-icon.json')))
for k,v in {'__APP_ICON32__':ic['icon32'],'__APP_ICON128__':ic['icon128'],'__APP_ICON180__':ic['icon180']}.items():
    assert k in s, k
    s=s.replace(k,v)
for k,v in {'__LOGO_LIGHT__':a['logoLight'],'__LOGO_DARK__':a['logoDark'],'__CALADEA__':a['caladea'],'__CARLITO__':a['carlito'],'__CARLITOB__':a['carlitoBold']}.items():
    assert k in s, k
    s=s.replace(k,v)
ma=json.load(open(os.path.join(here,'build','msra-assets.json')))
msjs='\n'.join(open(os.path.join(here,'src','msra',f)).read() for f in ['core.js','xlsx.js','pdf.js','ui.js'])
for k,v in {'__MSRA_STD__':ma['std'],'__MSRA_LOGO__':ma['logo'],'__OPENSANS_R__':ma['osr'],'__OPENSANS_B__':ma['osb']}.items():
    assert k in msjs, k
    msjs=msjs.replace(k,v)
for k,v in {'/*__MSRA_JS__*/':msjs,'/*__MSRA_CSS__*/':open(os.path.join(here,'src','msra','msra.css')).read()}.items():
    assert s.count(k)==1, k
    s=s.replace(k,v)
os.makedirs(os.path.join(here,'dist'),exist_ok=True)
out=os.path.join(here,'dist','Oxypro Project Library.html')
open(out,'w').write(s)
print(out, round(len(s)/1024),'KB')

# GitHub edition: the same page as a static website (site/), with runtime.js standing in for Claude's runtime,
# the project snapshot inlined and the photos as files
import shutil
snap_path=os.path.join(here,'github','snapshot.json')
if os.path.exists(snap_path):
    snap=json.load(open(snap_path))
    rt=open(os.path.join(here,'src','github','runtime.js')).read()
    data=json.dumps(snap['projects'],ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    assert '__PROJECTS__' in rt and '__SNAPSHOT_DATE__' in rt
    rt=rt.replace('__PROJECTS__',data).replace('__SNAPSHOT_DATE__',snap['date'])
    marker="<script>\n(() => {\n'use strict';"
    assert s.count(marker)==1, 'main script marker'
    page=s.replace(marker,'<script>\n'+rt+'\n</script>\n'+marker)
    # a full document, with the same base styles Claude wraps artifacts in ([hidden] really hides, UTF-8)
    page=page.replace('<title>Oxypro Project Library</title>\n','',1)
    page=('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
          '<title>Oxypro Project Library</title>\n<link rel="icon" href="favicon.ico" sizes="any">\n<link rel="apple-touch-icon" href="apple-touch-icon.png">\n<meta name="theme-color" content="#D81F27">\n<meta name="description" content="Oxypro Electromechanical project library: project details and photos, presentation sheets, PQP Maker and Method Statement Logs (GitHub edition).">\n'
          '<style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}'
          'body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style>\n'
          '</head>\n<body>\n'+page+'\n</body>\n</html>\n')
    site=os.path.join(here,'docs'); os.makedirs(os.path.join(site,'photos'),exist_ok=True)   # GitHub Pages serves main /docs
    open(os.path.join(site,'index.html'),'w').write(page)
    open(os.path.join(site,'.nojekyll'),'w').write('')
    from PIL import Image
    ico=Image.open(os.path.join(here,'build','app-icon-512.png')).convert('RGBA')
    ico.save(os.path.join(site,'favicon.ico'),sizes=[(16,16),(32,32),(48,48),(64,64)])
    ico.resize((180,180),Image.LANCZOS).save(os.path.join(site,'apple-touch-icon.png'))
    ico.resize((192,192),Image.LANCZOS).save(os.path.join(site,'icon-192.png'))
    ico.save(os.path.join(site,'icon-512.png'))
    used=set(x['id'] for p in snap['projects'].values() for x in (p.get('photos') or []) if x)
    for f in os.listdir(os.path.join(site,'photos')):
        if f[:-4] not in used: os.remove(os.path.join(site,'photos',f))
    # photos: from github/photos when a new snapshot brings them, otherwise the ones already in docs/photos
    for i in used:
        src=os.path.join(here,'github','photos',i+'.jpg'); dst=os.path.join(site,'photos',i+'.jpg')
        if os.path.exists(src) and (not os.path.exists(dst) or os.path.getsize(dst)!=os.path.getsize(src)): shutil.copyfile(src,dst)
        assert os.path.exists(dst), 'missing photo '+i
    print(os.path.join(site,'index.html'), round(len(page)/1024),'KB,', len(used),'photos')
