import json,sys
meta={m['uri']:m['id'] for m in json.load(open('pages.json',encoding='utf-8'))}
pid=meta.get(sys.argv[1],sys.argv[1])
d=json.load(open('pages/'+pid+'.json',encoding='utf-8'))
dd=d['data']['document_data']; ds=d['data']['design_data']
def q(k): return (k or '').lstrip('#')
def walk(c,ind=0):
    lay=c.get('layout',{})
    dt=dd.get(q(c.get('dataQuery')),{})
    info=dt.get('type','')
    extra=''
    if info=='StyledText': 
        import re; extra=re.sub('<[^>]+>','',dt.get('text',''))[:60]
    elif info in('Image',): extra=dt.get('uri','')[:50]
    elif info in('WixVideo','Video'): extra=str(dt.get('videoId') or dt.get('videoRef') or dt.get('videoUrl'))[:60]
    elif dt: extra=','.join(list(dt.keys())[:6])
    des=ds.get(q(c.get('designQuery')),{})
    bg=''
    b=des.get('background') if isinstance(des.get('background'),dict) else None
    if b: 
        mr=dd.get(q(b.get('mediaRef')),{}) if b.get('mediaRef') else {}
        bg=' BG:'+mr.get('type','')+':'+str(mr.get('uri') or mr.get('videoId') or '')[:40]
    print('  '*ind+f"{c.get('componentType','').split('.')[-1]} {c.get('id')} y={lay.get('y')} x={lay.get('x')} w={lay.get('width')} h={lay.get('height')} [{info}] {extra}{bg}")
    for ch in c.get('components',[]) or []: walk(ch,ind+1)
walk(d['structure'])
