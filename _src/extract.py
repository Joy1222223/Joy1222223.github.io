"""Convert downloaded Wix page JSON into simple ordered content blocks (blocks/<id>.json)."""
import json, os, re, html

META = json.load(open('pages.json', encoding='utf-8'))
os.makedirs('blocks', exist_ok=True)

def q(ref):
    return (ref or '').lstrip('#')

def clean_html(h, dd):
    """Keep simple formatting; resolve Wix link refs; drop inline styles/classes."""
    if not h:
        return ''
    # resolve links: <a dataquery="#xxx"> ... or data-anchor
    def link_sub(m):
        attrs = m.group(1)
        ref = re.search(r'dataquery="#?([^"]+)"', attrs)
        href = re.search(r'href="([^"]+)"', attrs)
        url = None
        if ref:
            url = resolve_link(dd.get(ref.group(1)), dd)
        elif href:
            url = href.group(1)
        if url:
            ext = url.startswith('http')
            return f'<a href="{html.escape(url)}"' + (' target="_blank" rel="noopener"' if ext else '') + '>'
        return '<a>'
    h = re.sub(r'<a([^>]*)>', link_sub, h)
    h = re.sub(r'\s(class|style|dir|data-[a-z-]+|wix-[a-z-]+|id)="[^"]*"', '', h)
    h = re.sub(r'<(/?)(span|font)[^>]*>', '', h)
    h = re.sub(r'<h[1-6]>', '<h3>', h); h = re.sub(r'</h[1-6]>', '</h3>', h)
    h = h.replace('&nbsp;', ' ')
    h = re.sub(r'<p>\s*(<br\s*/?>)?\s*</p>', '', h)
    return h.strip()

PAGE_IDS = {m['id'] for m in META}

def resolve_link(item, dd):
    if not item:
        return None
    t = item.get('type')
    if t == 'PageLink':
        return 'PAGE:' + q(item.get('pageId'))
    if t == 'ExternalLink':
        return item.get('url')
    if t == 'AnchorLink':
        return 'PAGE:' + q(item.get('pageId')) if item.get('pageId') else '#'
    if t == 'EmailLink':
        return 'mailto:' + item.get('recipient', '')
    if t == 'PhoneLink':
        return 'tel:' + item.get('phoneNumber', '')
    if t == 'DocumentLink':
        return 'https://static.wixstatic.com/ugd/' + item.get('docId', '')
    return None

DS = {}

def media_of(ref, dd):
    m = (dd.get(q(ref)) or DS.get(q(ref))) if ref else None
    if not m:
        return None
    t = m.get('type')
    if t == 'Image':
        return {'kind': 'image', 'uri': m.get('uri'), 'w': m.get('width'), 'h': m.get('height'), 'alt': m.get('alt') or m.get('title') or ''}
    if t == 'WixVideo':
        poster = dd.get(q(m.get('posterImageRef'))) or DS.get(q(m.get('posterImageRef'))) or {}
        return {'kind': 'video', 'vid': m.get('videoId'), 'poster': poster.get('uri'),
                'w': m.get('videoWidth') or poster.get('width'), 'h': m.get('videoHeight') or poster.get('height'),
                'q': [x.get('quality') for x in (m.get('qualities') or [])]}
    return None

def bg_media(comp, dd, ds):
    des = ds.get(q(comp.get('designQuery')), {})
    b = des.get('background')
    if isinstance(b, str):
        b = ds.get(q(b), {})
    if not isinstance(b, dict):
        return None
    mr = b.get('mediaRef')
    return media_of(mr, dd) if mr else None

def convert(pid):
    d = json.load(open(f'pages/{pid}.json', encoding='utf-8'))
    dd = d['data']['document_data']; ds = d['data']['design_data']
    DS.clear(); DS.update(ds)
    atoms = []

    def texts_in(c, sfx, out):
        data = dd.get(q(c.get('dataQuery')) + sfx) or dd.get(q(c.get('dataQuery')), {})
        if data.get('type') == 'StyledText':
            t = clean_html(data.get('text', ''), dd)
            if re.sub('<[^>]+>', '', t).strip():
                out.append(t)
        for ch in c.get('components', []) or []:
            texts_in(ch, sfx, out)
        return out

    def walk(c, ox, oy, sfx=''):
        lay = c.get('layout', {}) or {}
        x = ox + (lay.get('x') or 0); y = oy + (lay.get('y') or 0)
        w = lay.get('width') or 0; h = lay.get('height') or 0
        ct = (c.get('componentType') or '').split('.')[-1]
        data = (dd.get(q(c.get('dataQuery')) + sfx) if sfx else None) or dd.get(q(c.get('dataQuery')), {})
        dtype = data.get('type')
        if ct == 'BoxSlideShow':
            slides = []
            for s in c.get('components', []) or []:
                bm = bg_media(s, dd, ds)
                tx = texts_in(s, sfx, [])
                links = []
                for t in tx:
                    links += re.findall(r'href="([^"]+)"', t)
                slides.append({'media': bm, 'texts': tx, 'link': links[0] if links else None})
            atoms.append({'t': 'slides', 'x': x, 'y': y, 'w': w, 'h': h, 'slides': slides})
            return
        if ct == 'Repeater' and dtype == 'Repeater':
            for it in data.get('items', []):
                for ch in c.get('components', []) or []:
                    walk(ch, x, y, '__' + it)
            return
        if dtype == 'TextFxData':
            t = (data.get('text') or '').strip()
            if t:
                atoms.append({'t': 'text', 'x': x, 'y': y, 'w': w, 'h': h, 'html': '<h2>' + html.escape(t) + '</h2>', 'plain': t, 'head': True})
            return
        # backgrounds on containers
        if ct in ('StripColumnsContainer', 'Column', 'ClassicSection', 'Section', 'BoxContainer', 'Container', 'HoverBox'):
            bm = bg_media(c, dd, ds)
            if bm and h > 150 and ct != 'MediaPlayer':
                atoms.append({'t': 'banner', 'x': x, 'y': y, 'w': w, 'h': h, 'media': bm})
        if ct == 'WRichText' and dtype == 'StyledText':
            txt = clean_html(data.get('text', ''), dd)
            plain = re.sub('<[^>]+>', '', txt).strip()
            if plain and plain.lower() not in ('back to top',):
                big = bool(re.search(r'<h3>', txt)) or h < 140 and len(plain) < 40
                atoms.append({'t': 'text', 'x': x, 'y': y, 'w': w, 'h': h, 'html': txt, 'plain': plain[:80], 'head': big})
        elif ct in ('WPhoto', 'ImageX', 'Image') or dtype == 'Image':
            if dtype == 'Image':
                link = resolve_link(dd.get(q(data.get('link'))), dd) if data.get('link') else None
                mm = media_of('#' + data['id'], dd)
                if mm and mm.get('uri'):
                    atoms.append({'t': 'image', 'x': x, 'y': y, 'w': w, 'h': h, 'media': mm, 'link': link})
        elif ct == 'MediaPlayer':
            bm = bg_media(c, dd, ds)
            if bm:
                atoms.append({'t': 'video', 'x': x, 'y': y, 'w': w, 'h': h, 'media': bm})
        elif ct == 'VideoPlayer' or dtype == 'Video' or dtype == 'VideoPlayer':
            vm = None
            for v in data.values():
                if isinstance(v, str) and v.startswith('#'):
                    mm = media_of(v, dd)
                    if mm and mm['kind'] == 'video':
                        vm = mm
            if vm:
                atoms.append({'t': 'video', 'x': x, 'y': y, 'w': w, 'h': h, 'media': vm})
                return
            url = data.get('videoUrl') or ''
            if not url and data.get('videoId'):
                vt = data.get('videoType', 'YOUTUBE')
                url = ('https://www.youtube.com/watch?v=' if vt == 'YOUTUBE' else 'https://vimeo.com/') + data['videoId']
            if url:
                atoms.append({'t': 'embed', 'x': x, 'y': y, 'w': w, 'h': h, 'url': url})
        elif dtype == 'ImageList':
            items = []
            for ref in data.get('items', []):
                m = dd.get(q(ref), {})
                mm = media_of(ref, dd)
                if mm:
                    mm['title'] = m.get('title') or ''
                    mm['desc'] = m.get('description') or ''
                    mm['link'] = resolve_link(dd.get(q(m.get('link'))), dd) if m.get('link') else None
                    items.append(mm)
            if items:
                atoms.append({'t': 'gallery', 'x': x, 'y': y, 'w': w, 'h': h, 'items': items, 'kind': ct})
        elif ct in ('StylableButton', 'SiteButton', 'Button') and data:
            label = data.get('label') or ''
            link = resolve_link(dd.get(q(data.get('link'))), dd) if data.get('link') else None
            if label and label.lower() != 'back to top':
                atoms.append({'t': 'button', 'x': x, 'y': y, 'w': w, 'h': h, 'label': label, 'link': link})
        elif ct == 'HtmlComponent':
            atoms.append({'t': 'html', 'x': x, 'y': y, 'w': w, 'h': h, 'url': data.get('url'), 'src': data.get('sourceType')})
        elif dtype and dtype not in ('StyledText',) and ct not in ('FiveGridLine', 'Anchor', 'VectorImage', 'ShapeContainer'):
            if ct not in ('StripColumnsContainer', 'Column', 'ClassicSection', 'Section', 'Page', 'BoxContainer', 'Container', 'MediaOverlayControls', 'MediaControls', 'HoverBox'):
                atoms.append({'t': 'unknown', 'ct': ct, 'dtype': dtype, 'x': x, 'y': y, 'w': w, 'h': h})
        for ch in c.get('components', []) or []:
            walk(ch, x, y, sfx)

    walk(d['structure'], 0, 0)
    atoms.sort(key=lambda a: (round(a['y']), a['x']))
    return atoms

if __name__ == '__main__':
    stats = {}
    PG = json.load(open('progallery.json'))
    for m in META:
        a = convert(m['id'])
        used_pg = False
        na = []
        for x in a:
            if x['t'] == 'unknown' and x['ct'] in ('TPAWidget', 'TPAMultiSection'):
                if m['uri'] in PG and not used_pg:
                    na.append({'t': 'gallery', 'x': x['x'], 'y': x['y'], 'w': x['w'], 'h': x['h'], 'items': PG[m['uri']], 'kind': 'grid'})
                    used_pg = True
                continue
            na.append(x)
        a = na
        json.dump({'meta': m, 'atoms': a}, open(f"blocks/{m['id']}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        for x in a:
            k = x['t'] if x['t'] != 'unknown' else 'unknown:' + x['ct'] + '/' + x['dtype']
            stats[k] = stats.get(k, 0) + 1
    print(json.dumps(stats, indent=1))
