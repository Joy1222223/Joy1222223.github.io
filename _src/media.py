import json, os, re, urllib.request, concurrent.futures as cf
UA={'User-Agent':'Mozilla/5.0'}
OUT=os.path.join('..','assets','media')
lst=json.load(open('media_list.json'))
def one(uri):
    fn=os.path.join(OUT,re.sub(r'[^A-Za-z0-9_]','_',uri.split('.')[0])+'.webp')
    if os.path.exists(fn) and os.path.getsize(fn)>0: return 'skip',0
    u=f'https://static.wixstatic.com/media/{uri}/v1/fit/w_1600,h_1600,q_82/f.webp'
    try:
        b=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
        open(fn,'wb').write(b); return 'ok',len(b)
    except Exception as e:
        return 'err '+uri+' '+str(e)[:60],0
res=list(cf.ThreadPoolExecutor(12).map(one,lst))
errs=[r[0] for r in res if r[0].startswith('err')]
print('ok',sum(1 for r in res if r[0]=='ok'),'skip',sum(1 for r in res if r[0]=='skip'),'MB',round(sum(r[1] for r in res)/1e6,1),'errors',len(errs)); print('\n'.join(errs[:10]))
