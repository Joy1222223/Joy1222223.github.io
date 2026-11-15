"""Build the static GitHub Pages site (EN / 繁 / 简) from blocks/*.json."""
import json, os, re, html, hashlib, shutil

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)  # gh-site/
os.chdir(SRC)

META = {m['id']: m for m in json.load(open('pages.json', encoding='utf-8'))}
WEEK_OWNER = json.load(open('weekowner.json'))
TR = {}
for lang in ('zh-hant', 'zh-hans'):
    p = f'i18n/{lang}.json'
    TR[lang] = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
UI = json.load(open('i18n/ui.json', encoding='utf-8'))
LANGS = [('en', '', 'EN'), ('zh-hant', 'zh-hant/', '繁'), ('zh-hans', 'zh-hans/', '简')]
HTML_LANG = {'en': 'en', 'zh-hant': 'zh-Hant', 'zh-hans': 'zh-Hans'}

# ---------- site map ----------
SERIES = [('c9bzj', 'special-project-part2'), ('y7cyp', 'special-project-part1'), ('jf7sb', 'harbour-x-etc'),
          ('eetmx', 'harbour'), ('qct2x', 'vsfx728')]
SLUG = {
    'c1dmp': '', 'zvl5w': 'fx', 'rplnm': 'fx/honeybear', 'uo03y': 'fx/horse', 'jibjd': 'fx/alice',
    'ffw6e': 'animation', 'xzvgv': 'animation/overpower', 'b5yv6': 'animation/hedwig',
    'ykqhq': 'modeling', 'x0f1i': 'modeling/apple', 'ejrov': 'modeling/osl', 'uojq2': 'modeling/procedural-building',
    'ysj9w': 'modeling/customized-building', 'vci6s': 'lighting-compositing', 'jool6': 'lighting-compositing/lighting',
    'pgadp': 'tools', 'n8i71': 'tools/idle', 'et3rh': 'unreal', 'pv1yq': 'about',
}
for pid, s in SERIES:
    SLUG[pid] = 'blog/' + s
for pid, m in META.items():
    if pid in SLUG or pid == 'm30gb':
        continue
    n = re.sub(r'\D', '', m['title']) or '0'
    if pid in WEEK_OWNER:
        base = SLUG[WEEK_OWNER[pid]] + f'/week-{n}'
    else:
        base = f'blog/archive/week-{n}'
    s, k = base, 2
    while s in SLUG.values():
        s = f'{base}-{k}'; k += 1
    SLUG[pid] = s

NAV = [
    ('c1dmp', []), ('zvl5w', ['rplnm', 'uo03y', 'jibjd']), ('ffw6e', ['xzvgv', 'b5yv6']),
    ('ykqhq', ['x0f1i', 'ejrov', 'uojq2', 'ysj9w']), ('vci6s', ['jool6']), ('pgadp', ['n8i71']),
    ('et3rh', []), ('pv1yq', []), ('BLOG', [p for p, _ in SERIES]),
]
TITLE_FIX = {'vci6s': 'Lighting/Compositing', 'zvl5w': 'FX'}

# ---------- hand-written projects from gh-site/content/ ----------
import content as CONTENT_MOD
CONTENT = {}
for _it in CONTENT_MOD.load():
    if _it['slug'] in SLUG.values():
        _it['slug'] += '-2'
    CONTENT[_it['pid']] = _it
    if _it['soon']:
        continue
    SLUG[_it['pid']] = _it['slug']
    for _p, _subs in NAV:
        if _p == _it['hub']:
            _subs.append(_it['pid'])
UNREAL_ITEMS = [p for p, it in CONTENT.items() if it['hub'] == 'et3rh']

def t_ui(key, lang):
    v = UI.get(key, {})
    return v.get(lang) or v.get('en') or key

def page_title(pid, lang='en'):
    if pid == 'BLOG':
        return t_ui('Blog', lang)
    if pid in CONTENT:
        return CONTENT_MOD.localized(CONTENT[pid], lang)[0]
    en = TITLE_FIX.get(pid, META[pid]['title']).strip()
    en = re.sub(r'\s*\|\s*', ' | ', en)
    return tr_plain(en, lang)

def key_of(s):
    return hashlib.sha1(s.strip().encode('utf-8')).hexdigest()[:16]

CATALOG = {}  # key -> english html (collected for translation)

def tr(htm, lang):
    k = key_of(htm)
    CATALOG[k] = htm
    if lang == 'en':
        return htm
    hit = TR[lang].get(k)
    if hit:
        return hit
    # untranslated "WeekN" labels -> 第 N 週 / 第 N 周
    if re.fullmatch(r'\s*Week\s*\d+[\s​]*', re.sub(r'<[^>]+>', '', htm)):
        wk = '週' if lang == 'zh-hant' else '周'
        return re.sub(r'Week\s*(\d+)', lambda m: f'第 {m.group(1)} {wk}', htm)
    return htm

def tr_plain(s, lang):
    return re.sub('<[^>]+>', '', tr(s, lang)) if s else s

# ---------- media ----------
MEDIA = set()   # wix image uris to download

def img_url(uri):
    if not uri or uri.startswith('http'):
        return ''
    MEDIA.add(uri)
    return 'assets/media/' + re.sub(r'[^A-Za-z0-9_]', '_', uri.split('.')[0]) + '.webp'

def vid_url(m):
    qs = m.get('q') or []
    q = '1080p' if '1080p' in qs else ('720p' if '720p' in qs else (qs[0] if qs else '720p'))
    return f"https://video.wixstatic.com/video/{m['vid']}/{q}/mp4/file.mp4"

def link_url(l, root, lang_prefix):
    if not l:
        return None
    if l.startswith('PAGE:'):
        pid = l[5:]
        if pid in SLUG:
            s = SLUG[pid]
            return root + lang_prefix + (s + '/' if s else '')
        return None
    return l

def fix_links(htm, root, lp):
    def sub(m):
        u = link_url('PAGE:' + m.group(1), root, lp)
        return f'href="{u}"' if u else 'href="#"'
    return re.sub(r'href="PAGE:([a-z0-9]+)"', sub, htm)

# ---------- block rendering ----------
def media_html(m, root, cls='', autoplay=False, title=''):
    if not m:
        return ''
    if m['kind'] == 'image':
        w, h = m.get('w') or 1600, m.get('h') or 900
        if 'src' in m:
            u = m['src'] if m['src'].startswith('http') else root + m['src']
            return f'<img class="{cls} zoomable" loading="lazy" src="{u}" alt="{html.escape(m.get("alt") or title or "")}">'
        return (f'<img class="{cls} zoomable" loading="lazy" src="{root}{img_url(m["uri"])}" '
                f'width="{w}" height="{h}" alt="{html.escape(m.get("alt") or title or "")}">')
    poster = f' poster="{root}{img_url(m["poster"])}"' if m.get('poster') else ''
    if autoplay:
        return f'<video class="{cls}" autoplay muted loop playsinline preload="metadata"{poster} src="{vid_url(m)}"></video>'
    return f'<video class="{cls}" controls playsinline preload="none"{poster} src="{vid_url(m)}"></video>'

def embed_html(url):
    yt = re.search(r'(?:youtu\.be/|v=)([\w-]{6,})', url)
    vm = re.search(r'vimeo\.com/(\d+)', url)
    if yt:
        src = f'https://www.youtube-nocookie.com/embed/{yt.group(1)}'
    elif vm:
        src = f'https://player.vimeo.com/video/{vm.group(1)}'
    else:
        return f'<a class="btn ghost ripple" href="{html.escape(url)}" target="_blank" rel="noopener"><span>{html.escape(url)}</span></a>'
    return f'<div class="embed"><iframe src="{src}" loading="lazy" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div>'

def atom_html(a, root, lang, lp):
    t = a['t']
    if t == 'text':
        h = fix_links(tr(a['html'], lang), root, lp)
        plain = a['plain']
        is_head = a.get('head') and len(plain) < 70 and h.count('<p') <= 1 and '<li' not in h
        if is_head:
            inner = re.sub(r'</?(p|h\d)>', '', h)
            return f'<h2 class="ttl reveal">{inner}</h2>'
        return f'<div class="prose reveal">{h}</div>'
    if t == 'image':
        u = link_url(a.get('link'), root, lp)
        im = media_html(a['media'], root, 'media')
        if u:
            ext = '' if u.startswith(root) else ' target="_blank" rel="noopener"'
            im = f'<a class="media-link ripple" href="{u}"{ext}>{im.replace(" zoomable", "")}</a>'
        return f'<figure class="fig reveal">{im}</figure>'
    if t == 'video':
        return f'<figure class="fig vid reveal">{media_html(a["media"], root, "media")}</figure>'
    if t == 'embed':
        return f'<figure class="fig reveal">{embed_html(a["url"])}</figure>'
    if t == 'gallery':
        items = ''.join(f'<div class="g-item ripple">{media_html(i, root, "media")}</div>' for i in a['items'])
        return f'<div class="gallery reveal">{items}</div>'
    if t == 'button':
        u = link_url(a.get('link'), root, lp) or '#'
        return f'<a class="btn primary ripple reveal" href="{u}"><span>{html.escape(tr_plain(a["label"], lang))}</span></a>'
    if t == 'slides':
        return slides_html(a, root, lang, lp)
    return ''

CUR = {'pid': None}

def cover_of(pid):
    if pid in CONTENT:
        return CONTENT[pid]['cover']
    try:
        b = json.load(open(f'blocks/{pid}.json', encoding='utf-8'))
    except FileNotFoundError:
        return None
    for want in ('banner', 'video', 'image'):
        for a in b['atoms']:
            if a['t'] == want and a.get('media'):
                return a['media']
    return None

def slides_html(a, root, lang, lp):
    subs = next((s for p, s in NAV if p == CUR['pid']), None)
    if subs:
        by_link = {s.get('link'): s.get('media') for s in a['slides'] if s.get('media')}
        slides = [{'media': by_link.get('PAGE:' + sp) or cover_of(sp), 'link': 'PAGE:' + sp,
                   'title': page_title(sp, lang)} for sp in subs]
    else:
        slides = a['slides']
    cards = []
    for s in slides:
        if 'title' in s:
            title = s['title']
        else:
            texts = [fix_links(tr(x, lang), root, lp) for x in s['texts']]
            title = re.sub('<[^>]+>', '', texts[0]).strip() if texts else ''
        link = link_url(s.get('link'), root, lp)
        m = s.get('media')
        if not m:
            continue
        mh = media_html(m, root, 'cm', autoplay=False)
        if m['kind'] == 'video':
            mh = (f'<img class="cm" loading="lazy" src="{root}{img_url(m["poster"])}" alt="">' if m.get('poster') else '') + \
                 f'<video class="cm hv" muted loop playsinline preload="none" data-src="{vid_url(m)}"></video>'
        else:
            mh = mh.replace(' zoomable', '')
        tag = 'a' if link else 'div'
        href = f' href="{link}"' if link else ''
        cards.append(f'<{tag} class="pcard ripple tilt reveal"{href}>{mh}<div class="glare"></div>'
                     f'<div class="cap glass"><div class="t">{html.escape(title)}</div>'
                     f'<div class="arrow">&#8594;</div></div></{tag}>')
    return f'<div class="pgrid">{"".join(cards)}</div>'

def layout(atoms, root, lang, lp):
    """Group atoms (absolute Wix coords) into banners + rows, in reading order."""
    banners = [a for a in atoms if a['t'] == 'banner']
    rest = [a for a in atoms if a['t'] != 'banner']
    used = set()
    out = []
    # attach overlay texts/buttons to banners
    bmap = []
    for b in banners:
        inside = []
        for i, a in enumerate(rest):
            if i in used or a['t'] not in ('text', 'button'):
                continue
            cy = a['y'] + a['h'] / 2
            if b['y'] <= cy <= b['y'] + b['h']:
                inside.append(a); used.add(i)
        bmap.append((b, inside))
    items = [('banner', b['y'], (b, ins)) for b, ins in bmap] + \
            [('atom', a['y'], a) for i, a in enumerate(rest) if i not in used]
    items.sort(key=lambda x: x[1])
    rows = []
    for kind, y, obj in items:
        if kind == 'banner':
            rows.append(('banner', obj)); continue
        a = obj
        if rows and rows[-1][0] == 'row':
            row = rows[-1][1]
            top = min(r['y'] for r in row); bot = max(r['y'] + r['h'] for r in row)
            ov = min(bot, a['y'] + a['h']) - max(top, a['y'])
            if a['t'] not in ('slides', 'gallery') and all(r['t'] not in ('slides', 'gallery') for r in row) \
                    and ov > 0.35 * min(a['h'] or 1, bot - top or 1) and len(row) < 4 \
                    and all(abs(r['x'] - a['x']) > 60 for r in row):
                row.append(a); continue
        rows.append(('row', [a]))
    for kind, obj in rows:
        if kind == 'banner':
            b, ins = obj
            ins.sort(key=lambda a: (a['y'], a['x']))
            inner = ''.join(atom_html(a, root, lang, lp) for a in ins)
            out.append(f'<section class="banner">{media_html(b["media"], root, "bm", autoplay=True).replace(" zoomable", "")}'
                       f'<div class="bshade"></div><div class="binner">{inner}</div></section>')
        else:
            row = sorted(obj, key=lambda a: a['x'])
            if len(row) == 1:
                out.append(f'<div class="row one">{atom_html(row[0], root, lang, lp)}</div>')
            else:
                cols = ''.join(f'<div class="col" style="flex:{max(1, round(a["w"] / 100))}">{atom_html(a, root, lang, lp)}</div>' for a in row)
                out.append(f'<div class="row multi">{cols}</div>')
    return '\n'.join(out)

# ---------- page shell ----------
def nav_html(cur, root, lang, lp):
    def href(pid):
        if pid == 'BLOG':
            return root + lp + 'blog/'
        s = SLUG[pid]
        return root + lp + (s + '/' if s else '')
    lis = []
    for pid, subs in NAV:
        active = ' active' if cur == pid or cur in subs or (pid == 'BLOG' and SLUG.get(cur, '').startswith('blog')) else ''
        sub = ''
        if subs:
            sub = '<div class="sub glass">' + ''.join(f'<a class="ripple" href="{href(s)}">{html.escape(page_title(s, lang))}</a>' for s in subs) + '</div>'
        lis.append(f'<div class="ni{" has" if subs else ""}"><a class="nl ripple{active}" href="{href(pid)}">{html.escape(page_title(pid, lang))}</a>{sub}</div>')
    return ''.join(lis)

def lang_switch(slug_path, root, lang):
    out = []
    for code, pre, label in LANGS:
        on = ' on' if code == lang else ''
        out.append(f'<a class="lg ripple{on}" href="{root}{pre}{slug_path}" hreflang="{HTML_LANG[code]}">{label}</a>')
    return '<div class="langs glass">' + ''.join(out) + '</div>'

FOOT = None

VER = hashlib.sha1(b''.join(open(f, 'rb').read() for f in ('site.css', 'fx.css', 'site.js', 'fx.js'))).hexdigest()[:8]

def shell(title, body, cur, slug, lang, extra_head='', body_cls=''):
    lp = dict((c, p) for c, p, _ in LANGS)[lang]
    depth = (lp + (slug + '/' if slug else '')).count('/')
    root = '../' * depth
    slug_path = slug + '/' if slug else ''
    full_title = (title + ' | ' if title and cur != 'c1dmp' else '') + 'Yiqi Zheng'
    return f'''<!doctype html>
<html lang="{HTML_LANG[lang]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(t_ui('meta_desc', lang))}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Inter:wght@400;500;600&family=Noto+Sans+TC:wght@400;500;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/site.css?v={VER}">
<link rel="stylesheet" href="{root}assets/fx.css?v={VER}">
{"".join(f'<link rel="alternate" hreflang="{HTML_LANG[c]}" href="{root}{p}{slug_path}">' for c, p, _ in LANGS)}
{extra_head}</head>
<body class="lang-{lang} {body_cls}">
<header class="top glass"><a class="logo ripple" href="{root}{lp}">YIQI</a>
<nav class="nav" id="nav">{nav_html(cur, root, lang, lp)}</nav>
{lang_switch(slug_path, root, lang)}
<button class="burger ripple" id="burger" aria-label="Menu"><span></span><span></span><span></span></button></header>
<main>{body}</main>
<footer class="foot"><div class="fin glass reveal">
<div><div class="eyebrow">{t_ui('Contact', lang)}</div><h3>{t_ui('lets_talk', lang)}</h3></div>
<div class="contacts"><a class="btn ghost ripple" href="mailto:yiqi_zheng@outlook.com"><span>&#9993; yiqi_zheng@outlook.com</span></a>
<a class="btn ghost ripple" href="tel:+19129405889"><span>&#9742; 912-940-5889</span></a></div>
</div><div class="copy">&copy; Yiqi Zheng</div></footer>
<div class="lb" id="lb"><img alt=""></div>
<script src="{root}assets/site.js?v={VER}"></script>
<script src="{root}assets/fx.js?v={VER}"></script>
</body></html>'''

def write(slug, lang, content):
    lp = dict((c, p) for c, p, _ in LANGS)[lang]
    d = os.path.join(OUT, lp, slug) if slug else os.path.join(OUT, lp)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(content)

# ---------- special pages ----------
WORK = [
    ('et3rh', 'Unreal Engine', 'unreal_desc', None, None, True),
    ('zvl5w', 'FX & Procedural', 'fx_desc', 'f7279b_9b49193cda7345b98f7a24b56ff7d7b2~mv2.png', 'f7279b_c42fa3d2cb414f9e81b18a141ac4c779', False),
    ('ykqhq', 'Modeling & Texturing', 'model_desc', 'f7279b_7ba8710744034afa96c748b4994e6582~mv2.jpg', 'f7279b_6aa4009c366945818cecda7050c7b883', False),
    ('vci6s', 'Lighting & Compositing', 'light_desc', 'f7279b_3bd8e0cd5c914d81bd706bc04af5b679f000.jpg', 'f7279b_3bd8e0cd5c914d81bd706bc04af5b679', False),
    ('ffw6e', 'Animation', 'anim_desc', 'f7279b_7be4ab20ebcf4c7b9732f6a3843bbb95~mv2.png', 'f7279b_68e0ca3a74654cca928121107a44518a', False),
    ('pgadp', 'Technical Art · Tools', 'tools_desc', 'f7279b_39580be12f214170884a9c30fd2ef34cf000.jpg', 'f7279b_39580be12f214170884a9c30fd2ef34c', False),
]
TOOLS = ['Unreal Engine', 'Houdini', 'Maya', 'Substance', 'Nuke', 'Python', 'VEX', 'Blueprints']

def home(lang):
    lp = dict((c, p) for c, p, _ in LANGS)[lang]
    root = '../' * lp.count('/')
    b = json.load(open('blocks/c1dmp.json', encoding='utf-8'))
    reel = next((a for a in b['atoms'] if a['t'] == 'video'), None)
    cards = []
    for pid, en_t, dkey, img, vid, empty in WORK:
        href = root + lp + SLUG[pid] + '/'
        t = t_ui(en_t, lang); d = t_ui(dkey, lang)
        cov = next((cover_of(u) for u in UNREAL_ITEMS if cover_of(u)), None) if pid == 'et3rh' else None
        if cov:
            empty = False
            u = cov['src'] if cov['src'].startswith('http') else root + cov['src']
            media = f'<img class="cm" loading="lazy" src="{u}" alt="">'
            tag = ''
        elif empty:
            media = '<div class="ph"><div class="ue">U</div></div>'
            tag = f'<span class="tag tsoon">{t_ui("COMING SOON", lang)}</span>'
        else:
            media = (f'<img class="cm" loading="lazy" src="{root}{img_url(img)}" alt="">'
                     f'<video class="cm hv" muted loop playsinline preload="none" data-src="https://video.wixstatic.com/video/{vid}/480p/mp4/file.mp4"></video>')
            tag = ''
        cards.append(f'<a class="pcard ripple tilt reveal{" empty" if empty else ""}" href="{href}">{media}<div class="glare"></div>{tag}'
                     f'<div class="cap glass"><div><div class="t">{html.escape(t)}</div><div class="d">{html.escape(d)}</div></div><div class="arrow">&#8594;</div></div></a>')
    pills = ''.join(f'<span class="pill ripple">{x}</span>' for x in TOOLS)
    reel_html = ''
    if reel:
        reel_html = f'''<section class="wrap" id="reel"><div class="head reveal"><div><div class="eyebrow">{t_ui("SHOWREEL", lang)}</div><h2 class="big">{t_ui("Demo Reel", lang)}</h2></div></div>
<figure class="fig vid reel reveal">{media_html(reel["media"], root, "media")}</figure></section>'''
    body = f'''<section class="hero" id="hero">
<video class="hv-bg" autoplay muted loop playsinline src="https://video.wixstatic.com/video/f7279b_f837161814a74c1284962c25c2e3d861/1080p/mp4/file.mp4"></video>
<div class="hshade"></div><canvas id="particles"></canvas>
<div class="hwrap"><div class="hcard glass" id="hcard">
<div class="chip"><span class="dot"></span>{t_ui("TECHNICAL ARTIST / CG GENERALIST", lang)}</div>
<h1 class="name" id="name"><span class="w">YIQI</span><span class="w">ZHENG</span></h1>
<p>{t_ui("hero_intro", lang)}</p>
<div class="btns"><a class="btn primary ripple mag" href="#work"><span>{t_ui("VIEW MY WORK", lang)}</span></a>
<a class="btn ghost ripple mag" href="#contact"><span>{t_ui("CONTACT ME", lang)}</span></a></div></div></div>
<a class="scroll glass ripple" href="#work"><span class="mouse"></span>{t_ui("SCROLL", lang)}</a></section>
{reel_html}
<section class="wrap" id="work"><div class="blob b1"></div><div class="blob b2"></div>
<div class="head reveal"><div><div class="eyebrow">{t_ui("SELECTED WORK", lang)}</div><h2 class="big">{t_ui("What I Make", lang)}</h2></div>
<p class="lede">{t_ui("work_sub", lang)}</p></div>
<div class="pgrid">{"".join(cards)}</div>
<div class="tools glass reveal"><span class="lbl">{t_ui("TOOLKIT", lang)}</span>{pills}</div></section>
<span id="contact"></span>'''
    write('', lang, shell('', body, 'c1dmp', '', lang, body_cls='home'))

def unreal(lang):
    lp = dict((c, p) for c, p, _ in LANGS)[lang]
    if UNREAL_ITEMS:
        root = '../' * (lp + SLUG['et3rh'] + '/').count('/')
        cards = []
        for u in UNREAL_ITEMS:
            it = CONTENT[u]; t = CONTENT_MOD.localized(it, lang)[0]
            sub = html.escape(CONTENT_MOD.localized_meta(it, 'subtitle', lang))
            d = f'<div class="d">{sub}</div>' if sub else ''
            cov = it['cover']
            if it['soon'] or not cov:
                media = '<div class="ph"><div class="ue">U</div></div>'
                tag = f'<span class="tag tsoon">{t_ui("COMING SOON", lang)}</span>' if it['soon'] else ''
            else:
                cu = cov['src'] if cov['src'].startswith('http') else root + cov['src']
                media = f'<img class="cm" loading="lazy" src="{cu}" alt="">'; tag = ''
            el, href = ('div', '') if it['soon'] else ('a', f' href="{root}{lp}{SLUG[u]}/"')
            cards.append(f'<{el} class="pcard ripple tilt reveal{" empty" if it["soon"] else ""}"{href}>{media}<div class="glare"></div>{tag}'
                         f'<div class="cap glass"><div><div class="t">{html.escape(t)}</div>{d}</div><div class="arrow">&#8594;</div></div></{el}>')
        grid = f'<div class="pgrid two">{"".join(cards)}</div>'
        body = f'''<section class="wrap"><div class="blob b1"></div><div class="blob b2"></div>
<div class="head reveal"><div><div class="eyebrow">{t_ui("SELECTED WORK", lang)}</div><h1 class="big">Unreal Engine</h1></div></div>{grid}</section>'''
        write(SLUG['et3rh'], lang, shell(page_title('et3rh', lang), body, 'et3rh', SLUG['et3rh'], lang))
        return
    body = f'''<section class="wrap center"><div class="blob b1"></div><div class="blob b2"></div>
<div class="soon glass tilt reveal"><div class="ue spin">U</div><span class="chip">{t_ui("COMING SOON", lang)}</span>
<h1 class="big">Unreal Engine</h1><p>{t_ui("unreal_soon", lang)}</p></div></section>'''
    write(SLUG['et3rh'], lang, shell(page_title('et3rh', lang), body, 'et3rh', SLUG['et3rh'], lang))

def blog_index(lang):
    lp = dict((c, p) for c, p, _ in LANGS)[lang]
    root = '../' * (lp + 'blog/').count('/')
    cards = []
    for pid, s in SERIES:
        b = json.load(open(f'blocks/{pid}.json', encoding='utf-8'))
        img = next((a['media'] for a in b['atoms'] if a['t'] == 'image'), None) or \
              next((a['media'] for a in b['atoms'] if a['t'] in ('banner',) and a['media']['kind'] == 'image'), None)
        n = sum(1 for w, o in WEEK_OWNER.items() if o == pid)
        mh = f'<img class="cm" loading="lazy" src="{root}{img_url(img["uri"])}" alt="">' if img else '<div class="ph"></div>'
        cards.append(f'<a class="pcard ripple tilt reveal" href="{root}{lp}{SLUG[pid]}/">{mh}<div class="glare"></div>'
                     f'<div class="cap glass"><div><div class="t">{html.escape(page_title(pid, lang))}</div>'
                     f'<div class="d">{n} {t_ui("entries", lang)}</div></div><div class="arrow">&#8594;</div></div></a>')
    body = f'''<section class="wrap"><div class="blob b1"></div>
<div class="head reveal"><div><div class="eyebrow">{t_ui("PROCESS", lang)}</div><h1 class="big">{t_ui("Blog", lang)}</h1></div>
<p class="lede">{t_ui("blog_sub", lang)}</p></div><div class="pgrid">{"".join(cards)}</div></section>'''
    write('blog', lang, shell(t_ui('Blog', lang), body, 'BLOG', 'blog', lang))

def generic(pid, lang):
    slug = SLUG[pid]
    lp = dict((c, p) for c, p, _ in LANGS)[lang]
    root = '../' * (lp + slug + '/').count('/')
    b = json.load(open(f'blocks/{pid}.json', encoding='utf-8'))
    CUR['pid'] = pid
    atoms = [a for a in b['atoms'] if a['t'] != 'html']
    content = layout(atoms, root, lang, lp)
    crumbs = ''
    parent = None
    for p, subs in NAV:
        if pid in subs:
            parent = p
    if pid in WEEK_OWNER:
        parent = WEEK_OWNER[pid]
    if parent:
        ph = root + lp + ('blog/' if parent == 'BLOG' else SLUG[parent] + '/')
        crumbs = f'<a class="crumb glass ripple" href="{ph}">&#8592; {html.escape(page_title(parent, lang))}</a>'
    # prev/next for weeks
    pn = ''
    if pid in WEEK_OWNER:
        sib = sorted([w for w, o in WEEK_OWNER.items() if o == WEEK_OWNER[pid]],
                     key=lambda w: int(re.sub(r'\D', '', META[w]['title']) or 0))
        i = sib.index(pid)
        lnk = lambda w, cls, lab: f'<a class="btn ghost ripple {cls}" href="{root}{lp}{SLUG[w]}/"><span>{lab}</span></a>'
        pn = '<div class="pn">' + (lnk(sib[i - 1], 'prev', '&#8592; ' + html.escape(page_title(sib[i - 1], lang))) if i > 0 else '<span></span>') + \
             (lnk(sib[i + 1], 'next', html.escape(page_title(sib[i + 1], lang)) + ' &#8594;') if i < len(sib) - 1 else '') + '</div>'
    first_banner = atoms and atoms[0]['t'] == 'banner'
    title_html = '' if first_banner else ''
    body = f'<div class="page">{crumbs}{title_html}{content}{pn}</div>'
    write(slug, lang, shell(page_title(pid, lang), body, pid, slug, lang))

def content_page(pid, lang):
    it = CONTENT[pid]
    slug = SLUG[pid]
    lp = dict((c, p) for c, p, _ in LANGS)[lang]
    root = '../' * (lp + slug + '/').count('/')
    title, md = CONTENT_MOD.localized(it, lang)
    ph = root + lp + SLUG[it['hub']] + '/'
    crumbs = f'<a class="crumb glass ripple" href="{ph}">&#8592; {html.escape(page_title(it["hub"], lang))}</a>'
    head = f'<div class="row one"><h1 class="ttl reveal">{html.escape(title)}</h1></div>'
    body = f'<div class="page">{crumbs}{head}{CONTENT_MOD.render(md, it["folder"], root)}</div>'
    write(slug, lang, shell(title, body, pid, slug, lang))

def build():
    for code, _, _ in LANGS:
        home(code); unreal(code); blog_index(code)
        for pid in SLUG:
            if pid in ('c1dmp', 'et3rh'):
                continue
            if pid in CONTENT:
                content_page(pid, code)
            else:
                generic(pid, code)
    json.dump(sorted(MEDIA), open('media_list.json', 'w'), indent=0)
    json.dump(CATALOG, open('i18n/catalog_en.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    shutil.copy('site.css', os.path.join(OUT, 'assets', 'site.css'))
    shutil.copy('site.js', os.path.join(OUT, 'assets', 'site.js'))
    shutil.copy('fx.js', os.path.join(OUT, 'assets', 'fx.js'))
    shutil.copy('fx.css', os.path.join(OUT, 'assets', 'fx.css'))
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    print('pages', len(SLUG) * 3, 'media', len(MEDIA), 'strings', len(CATALOG))

if __name__ == '__main__':
    os.makedirs(os.path.join(OUT, 'assets', 'media'), exist_ok=True)
    build()
