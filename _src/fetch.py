import re, json, urllib.request, os
UA={'User-Agent':'Mozilla/5.0'}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
html=get('https://yiqizheng.wixsite.com/yiqizheng/unreal').decode('utf-8','ignore')
pm=re.findall(r'"pageId":"([a-z0-9]+)","title":"([^"]*)","pageUriSEO":"([^"]*)","pageJsonFileName":"([^"]+)"',html)
mp=re.findall(r'"masterPageJsonFileName"\s*:\s*"([^"]+)"',html) or re.findall(r'masterPage[^"]{0,30}"([^"]*_\d+\.json)',html)
print('pages',len(pm),'master',mp[:2])
os.makedirs('pages',exist_ok=True)
meta=[]
for pid,title,uri,js in pm:
    d=get('https://static.wixstatic.com/sites/'+js+'.json.z?v=3')
    open('pages/'+pid+'.json','wb').write(d)
    meta.append({'id':pid,'title':json.loads('"'+title+'"'),'uri':uri})
json.dump(meta,open('pages.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
open('home.html','w',encoding='utf-8').write(html)
print('ok')
