import json, os
here=os.path.dirname(os.path.abspath(__file__))
a=json.load(open(os.path.join(here,'build','assets.json')))
s=open(os.path.join(here,'src','library.html')).read()
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
