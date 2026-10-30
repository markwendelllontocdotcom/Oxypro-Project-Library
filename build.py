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
# the MSRA Generator's standard list and default settings (Generate MSRA), from its repository data
std=open(os.path.join(here,'build','msra-gen-std.json')).read().replace('</','<\\/')
assert s.count('__MSRA_GEN_STD__')==1, '__MSRA_GEN_STD__'
s=s.replace('__MSRA_GEN_STD__',std)
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
    logos=json.dumps(snap.get('logos',{}),ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    rt=rt.replace('__PROJECTS__',data).replace('__LOGOS__',logos).replace('__SNAPSHOT_DATE__',snap['date'])
    marker="<script>\n(() => {\n'use strict';"
    assert s.count(marker)==1, 'main script marker'
    page=s.replace(marker,'<script>\n'+rt+'\n</script>\n'+marker)
    # a full document, with the same base styles Claude wraps artifacts in ([hidden] really hides, UTF-8)
    page=page.replace('<title>Oxypro Project Library</title>\n','',1)
    # icons and the link preview (chat apps, social sites): file names with ?v=<version>, so a new icon is fetched
    # again instead of a copy kept for the old address
    import re
    ver=re.search(r"APP_VERSION = '([^']+)'",s).group(1)
    GH_SITE='https://markwendelllontocdotcom.github.io/Oxypro-Project-Library/'
    DESC='Oxypro Electromechanical project library: project details and photos, presentation sheets, QA/QC (PQP and Method Statement Logs) and HSE Plans.'
    def meta_head(icons, url):
        return (f'<link rel="icon" href="{icons}favicon.ico?v={ver}" sizes="any">\n<link rel="apple-touch-icon" href="{icons}apple-touch-icon.png?v={ver}">\n'
                f'<meta name="theme-color" content="#D81F27">\n<meta name="description" content="{DESC}">\n'
                f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="Oxypro Project Library">\n'
                f'<meta property="og:title" content="Oxypro Project Library">\n<meta property="og:description" content="{DESC}">\n'
                f'<meta property="og:url" content="{url}">\n<meta property="og:image" content="{GH_SITE}docs/icon-512.png?v={ver}">\n'
                f'<meta property="og:image:width" content="512">\n<meta property="og:image:height" content="512">\n<meta property="og:image:alt" content="Oxypro Library logo">\n'
                f'<meta name="twitter:card" content="summary">\n<meta name="twitter:image" content="{GH_SITE}docs/icon-512.png?v={ver}">\n')
    page=('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
          '<title>Oxypro Project Library</title>\n'+meta_head('', GH_SITE+'docs/')+
          '<style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}'
          'body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style>\n'
          '</head>\n<body>\n'+page+'\n</body>\n</html>\n')
    site=os.path.join(here,'docs'); os.makedirs(os.path.join(site,'photos'),exist_ok=True)   # GitHub Pages serves main /docs
    open(os.path.join(site,'index.html'),'w').write(page)
    open(os.path.join(site,'.nojekyll'),'w').write('')
    # the start page at the repository root (GitHub Pages publishes main /): sends visitors to docs/ with the hash
    open(os.path.join(here,'index.html'),'w').write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>Oxypro Project Library</title>\n'+meta_head('docs/', GH_SITE)+
        '<!-- GitHub Pages set to the repository root serves this page: the Library itself is in docs/ (the hash is kept) -->\n'
        "<script>location.replace('docs/' + location.search + location.hash);</script>\n"
        '<noscript><meta http-equiv="refresh" content="0; url=docs/"></noscript>\n'
        '<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#111;color:#eee;font:16px system-ui,sans-serif}a{color:#ff5a5f}</style>\n'
        '</head>\n<body><p><a href="docs/">Open the Oxypro Project Library</a></p></body>\n</html>\n')
    from PIL import Image
    ico=Image.open(os.path.join(here,'build','app-icon-512.png')).convert('RGBA')
    shutil.copy(os.path.join(here,'build','favicon.ico'),os.path.join(site,'favicon.ico'))   # the book alone at 16-32 px, the full logo at 48-64 px
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
    # company logos: from github/logos (asset id .png), as the projects' photos
    os.makedirs(os.path.join(site,'logos'),exist_ok=True)
    lused=set(x['id'] for x in snap.get('logos',{}).values())
    for f in os.listdir(os.path.join(site,'logos')):
        if f[:-4] not in lused: os.remove(os.path.join(site,'logos',f))
    for i in lused:
        src=os.path.join(here,'github','logos',i+'.png'); dst=os.path.join(site,'logos',i+'.png')
        if os.path.exists(src): shutil.copyfile(src,dst)
        assert os.path.exists(dst), 'missing logo '+i
    print(os.path.join(site,'index.html'), round(len(page)/1024),'KB,', len(used),'photos,', len(lused),'logos')
