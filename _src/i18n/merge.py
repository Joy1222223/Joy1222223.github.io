"""Merge i18n/chunks/zh_*.json -> zh-hant.json, and convert to zh-hans.json with OpenCC."""
import json, glob, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import opencc
hant = {}
for f in sorted(glob.glob('chunks/zh_*.json')):
    hant.update(json.load(open(f, encoding='utf-8')))
en = json.load(open('catalog_en.json', encoding='utf-8'))
t2s = opencc.OpenCC('t2s').convert
hans = {k: t2s(v) for k, v in hant.items()}
json.dump(hant, open('zh-hant.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(hans, open('zh-hans.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
missing = [k for k in en if k not in hant]
def plain(s): return re.sub(r'<[^>]+>', '', s).strip()
real = [k for k in missing if not re.fullmatch(r'(https?://\S+|\s|&nbsp;|​)*', plain(en[k]))]
print('translated', len(hant), '/', len(en), '| missing', len(missing), '| missing non-URL', len(real))
bad = [k for k in hant if hant[k].count('<a ') != en.get(k, '').count('<a ')]
print('link-count mismatches', bad)
for k in real: print(k, repr(plain(en[k])[:80]))
