"""Load hand-written projects from gh-site/content/<section>/*.md.

Each .md file becomes one project page under that section, plus a card on the
section page and an entry in the menu. See content/README.md for the format.
"""
import os, re, html
from urllib.parse import quote

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'content')

# content folder name -> section page id
SECTIONS = {
    'unreal': 'et3rh', 'fx': 'zvl5w', 'animation': 'ffw6e', 'modeling': 'ykqhq',
    'lighting-compositing': 'vci6s', 'tools': 'pgadp',
}

try:
    import opencc
    _T2S = opencc.OpenCC('t2s').convert
except Exception:  # OpenCC missing: Simplified just reuses the Traditional text
    _T2S = lambda s: s

YT = re.compile(r'(?:youtube\.com/(?:watch\?v=|shorts/|embed/)|youtu\.be/)([\w-]{6,})')
VM = re.compile(r'vimeo\.com/(?:video/)?(\d+)')
IMG_EXT = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif')
VID_EXT = ('.mp4', '.webm', '.mov')


def _front(text):
    meta = {}
    m = re.match(r'^﻿?---\s*\n(.*?)\n---\s*\n?', text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip().lower()] = v.strip().strip('"\'')
        text = text[m.end():]
    return meta, text


def _src(ref, folder):
    """Resolve an image/video reference written in a .md file to a site path or URL."""
    ref = ref.strip().strip('<>')
    if re.match(r'^https?://', ref):
        return ref
    p = os.path.normpath(os.path.join(folder, ref))
    rel = os.path.relpath(p, os.path.dirname(ROOT)).replace('\\', '/')
    return quote(rel)


def _media(ref, folder):
    """A cover/image reference -> media dict understood by build.media_html."""
    if not ref:
        return None
    yt = YT.search(ref)
    if yt:
        return {'kind': 'image', 'src': f'https://i.ytimg.com/vi/{yt.group(1)}/hqdefault.jpg'}
    return {'kind': 'image', 'src': _src(ref, folder)}


def _inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+|mailto:[^)\s]+)\)',
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    s = re.sub(r'(?<!["=>])(https?://[^\s<]+)', r'<a href="\1" target="_blank" rel="noopener">\1</a>', s)
    return s


def _embed(url):
    yt, vm = YT.search(url), VM.search(url)
    src = (f'https://www.youtube-nocookie.com/embed/{yt.group(1)}' if yt else
           f'https://player.vimeo.com/video/{vm.group(1)}')
    return (f'<div class="row one"><figure class="fig reveal"><div class="embed"><iframe src="{src}" loading="lazy" '
            f'allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div></figure></div>')


# compare: a.jpg | b.jpg      or      compare Fresh | Rotten: a.jpg | b.jpg
CMP = re.compile(r'compare(?:\s+([^:|]+?)\s*\|\s*([^:|]+?))?\s*:\s*(\S+)\s*\|\s*(\S+)', re.I)


def _compare(m, folder, root):
    """Before/after slider: image A on the left of the handle, image B on the right."""
    la, lb, a, b = m.groups()
    def u(ref):
        s = _src(ref, folder)
        return html.escape(s if s.startswith('http') else root + s)
    labs = ''.join(f'<span class="cmp-lab {side}">{html.escape(t.strip())}</span>'
                   for side, t in (('l', la), ('r', lb)) if t)
    aria = html.escape(f'{la.strip()} / {lb.strip()}' if la else 'Compare')
    return (f'<div class="row one"><figure class="fig cmp reveal"><div class="cmp-box">'
            f'<img class="cmp-b" loading="lazy" src="{u(b)}" alt="{html.escape((lb or "").strip())}">'
            f'<img class="cmp-a" loading="lazy" src="{u(a)}" alt="{html.escape((la or "").strip())}">'
            f'<div class="cmp-bar"></div>{labs}'
            f'<input class="cmp-rng" type="range" min="0" max="100" step="0.1" value="50" aria-label="{aria}">'
            f'</div></figure></div>')


def _switch(items, folder, root):
    """Apple-style stage: segmented tabs over a stack of videos/images that cross-fade."""
    def u(ref):
        s = _src(ref, folder)
        return html.escape(s if s.startswith('http') else root + s)
    tabs, stage = [], []
    for i, (label, ref) in enumerate(items):
        on = ' on' if i == 0 else ''
        tabs.append(f'<button type="button" class="sw-tab{on}" role="tab" aria-selected="{"true" if i == 0 else "false"}">{_inline(label)}</button>')
        if ref.lower().split('?')[0].endswith(VID_EXT):
            media = f'<video muted loop playsinline preload="{"auto" if i == 0 else "none"}" src="{u(ref)}"></video><div class="sw-prog"><i></i></div>'
        else:
            media = f'<img class="zoomable" loading="lazy" src="{u(ref)}" alt="{html.escape(label)}">'
        stage.append(f'<div class="sw-item{on}">{media}</div>')
    one = ' single' if len(items) == 1 else ''
    return (f'<div class="row one"><div class="sw reveal{one}"><div class="sw-tabs" role="tablist">{"".join(tabs)}<span class="sw-ind"></span></div>'
            f'<div class="sw-stage">{"".join(stage)}</div></div></div>')


def _params(items, folder, root):
    """Drag-a-slider explorer: material tabs, parameter chips, a range input scrubbing pre-rendered frames.
    items: (material, label, frames folder) — the folder holds 00.webp.. and info.json (vals, default, dec)."""
    import json
    mats = {}
    for mat, label, ref in items:
        d = os.path.normpath(os.path.join(folder, ref))
        try:
            info = json.load(open(os.path.join(d, 'info.json'), encoding='utf-8'))
        except OSError:
            continue
        mats.setdefault(mat, []).append((label, root + _src(ref.rstrip('/'), folder) + '/', info))
    if not mats:
        return ''
    tabs, panes = [], []
    for mi, (mat, plist) in enumerate(mats.items()):
        on = ' on' if mi == 0 else ''
        tabs.append(f'<button type="button" class="sw-tab{on}" role="tab" aria-selected="{"true" if mi == 0 else "false"}">{_inline(mat)}</button>')
        chips = []
        for pi, (label, url, info) in enumerate(plist):
            vals = info['vals']; dec = info.get('dec', 2)
            fmt = [('%.*f' % (dec, v)) for v in vals]
            chips.append(f'<button type="button" class="pm-chip{" on" if pi == 0 else ""}" data-src="{html.escape(url)}" '
                         f'data-def="{info["default"]}" data-vals="{html.escape(json.dumps(fmt))}">{_inline(label)}</button>')
        label0, url0, info0 = plist[0]
        n0 = len(info0['vals'])
        panes.append(
            f'<div class="pm-mat{on}"><div class="pm-view"><img class="pm-img" alt="{html.escape(mat)}" '
            f'src="{html.escape(url0)}{info0["default"]:02d}.webp" loading="lazy"></div>'
            f'<div class="pm-ctrl"><div class="pm-chips">{"".join(chips)}</div>'
            f'<div class="pm-row"><span class="pm-name">{_inline(label0)}</span><output class="pm-val"></output></div>'
            f'<input class="pm-range" type="range" min="0" max="{n0 - 1}" step="1" value="{info0["default"]}" aria-label="{html.escape(label0)}">'
            f'<div class="pm-ends"><span></span><span></span></div><p class="pm-hint">Drag the slider</p></div></div>')
    return (f'<div class="row one"><div class="pm reveal"><div class="sw-tabs pm-tabs" role="tablist">{"".join(tabs)}<span class="sw-ind"></span></div>'
            f'<div class="pm-stage">{"".join(panes)}</div></div></div>')


def _stats(line):
    cells = []
    for part in line.split('|'):
        part = part.strip()
        m = re.match(r'^([\d.,]+)\s*(.*)$', part)
        if m:
            n = m.group(1).replace(',', '')
            cells.append(f'<div class="st"><b data-n="{html.escape(n)}">{html.escape(m.group(1))}</b><span>{_inline(m.group(2))}</span></div>')
        else:
            cells.append(f'<div class="st"><b>{_inline(part)}</b></div>')
    return f'<div class="row one"><div class="stats reveal">{"".join(cells)}</div></div>'


def render(body, folder, root):
    """Tiny Markdown subset -> page HTML using the site's own classes."""
    out, para, lst, imgs = [], [], [], []

    def flush_para():
        if para:
            out.append('<div class="row one"><div class="prose reveal"><p>' + '<br>'.join(_inline(x) for x in para) + '</p></div></div>')
            para.clear()

    def flush_list():
        if lst:
            out.append('<div class="row one"><div class="prose reveal"><ul>' + ''.join(f'<li>{_inline(x)}</li>' for x in lst) + '</ul></div></div>')
            lst.clear()

    def flush_imgs():
        if not imgs:
            return
        def tag(src, alt):
            u = src if src.startswith('http') else root + src
            return f'<img class="media zoomable" loading="lazy" src="{u}" alt="{html.escape(alt)}">'
        if len(imgs) == 1:
            out.append(f'<div class="row one"><figure class="fig reveal">{tag(*imgs[0])}</figure></div>')
        else:
            out.append('<div class="row one"><div class="gallery reveal">' +
                       ''.join(f'<div class="g-item ripple">{tag(s, a)}</div>' for s, a in imgs) + '</div></div>')
        imgs.clear()

    def flush_all():
        flush_para(); flush_list(); flush_imgs()

    block = None   # items of an open ::: switch / ::: params block
    kind = None
    for raw in body.splitlines():
        line = raw.strip()
        if block is not None:
            if line == ':::':
                out.append(_switch(block, folder, root) if kind == 'switch' else _params(block, folder, root)); block = None
            elif '|' in line:
                block.append(tuple(p.strip() for p in (line.rsplit('|', 1) if kind == 'switch' else line.split('|', 2))))
            continue
        km = re.fullmatch(r':::\s*(switch|params)', line, re.I)
        if km:
            flush_all(); block = []; kind = km.group(1).lower(); continue
        if not line:
            flush_all(); continue
        sm = re.match(r'^stats:\s*(.+)$', line, re.I)
        if sm:
            flush_all(); out.append(_stats(sm.group(1))); continue
        cm = CMP.fullmatch(line)
        if cm:
            flush_all()
            out.append(_compare(cm, folder, root))
            continue
        m = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', line)
        bare_img = re.fullmatch(r'\S+', line) and line.lower().split('?')[0].endswith(IMG_EXT)
        if m or bare_img:
            flush_para(); flush_list()
            alt, ref = (m.group(1), m.group(2)) if m else ('', line)
            if ref.lower().split('?')[0].endswith(VID_EXT):
                flush_imgs()
                u = _src(ref, folder); u = u if u.startswith('http') else root + u
                out.append(f'<div class="row one"><figure class="fig vid reveal"><video class="media" controls playsinline preload="metadata" src="{u}"></video></figure></div>')
            else:
                imgs.append((_src(ref, folder), alt))
            continue
        flush_imgs()
        if re.fullmatch(r'https?://\S+', line) and (YT.search(line) or VM.search(line)):
            flush_para(); flush_list(); out.append(_embed(line)); continue
        if re.fullmatch(r'\S+', line) and line.lower().split('?')[0].endswith(VID_EXT):
            flush_para(); flush_list()
            u = _src(line, folder); u = u if u.startswith('http') else root + u
            out.append(f'<div class="row one"><figure class="fig vid reveal"><video class="media" controls playsinline preload="metadata" src="{u}"></video></figure></div>')
            continue
        h = re.match(r'^(#{1,3})\s+(.*)', line)
        if h:
            flush_para(); flush_list()
            if len(h.group(1)) <= 2:
                out.append(f'<div class="row one"><h2 class="ttl reveal">{_inline(h.group(2))}</h2></div>')
            else:
                out.append(f'<div class="row one"><div class="prose reveal"><h3>{_inline(h.group(2))}</h3></div></div>')
            continue
        li = re.match(r'^[-*•]\s+(.*)', line)
        if li:
            flush_para(); lst.append(li.group(1)); continue
        flush_list(); para.append(line)
    flush_all()
    return '\n'.join(out)


def load():
    """Return list of items: {pid, section, hub, slug, order, folder, en:{title,body}, zh:{...}|None}."""
    items = []
    if not os.path.isdir(ROOT):
        return items
    for sec, hub in SECTIONS.items():
        d = os.path.join(ROOT, sec)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith('.md') or fn.startswith(('_', '.')) or fn.endswith('.zh.md'):
                continue
            name = fn[:-3]
            meta, body = _front(open(os.path.join(d, fn), encoding='utf-8-sig').read())
            if meta.get('hide', '').lower() in ('yes', 'true', '1'):
                continue
            zh = None
            zp = os.path.join(d, name + '.zh.md')
            if os.path.exists(zp):
                zm, zb = _front(open(zp, encoding='utf-8-sig').read())
                zh = {'title': zm.get('title') or meta.get('title') or name, 'body': zb, 'meta': zm}
            slug_name = re.sub(r'[^a-z0-9-]+', '-', name.lower()).strip('-') or 'project'
            try:
                order = float(meta.get('order', 100))
            except ValueError:
                order = 100
            items.append({
                'pid': f'md:{sec}/{slug_name}', 'section': sec, 'hub': hub,
                'slug': f'{sec}/{slug_name}', 'order': order, 'folder': d,
                'cover': _media(meta.get('cover'), d), 'meta': meta,
                'soon': meta.get('soon', '').lower() in ('yes', 'true', '1'),
                'en': {'title': meta.get('title') or name, 'body': body}, 'zh': zh,
            })
    items.sort(key=lambda it: (it['order'], it['slug']))
    return items


def localized(item, lang):
    """(title, markdown body) for a language; Simplified is converted from Traditional."""
    if lang == 'en' or not item['zh']:
        return item['en']['title'], item['en']['body']
    t, b = item['zh']['title'], item['zh']['body']
    if lang == 'zh-hans':
        t, b = _T2S(t), _T2S(b)
    return t, b


def localized_meta(item, key, lang):
    """A front-matter field (e.g. subtitle) in the right language."""
    v = item['meta'].get(key, '')
    if lang != 'en' and item['zh']:
        v = item['zh']['meta'].get(key) or v
        if lang == 'zh-hans':
            v = _T2S(v)
    return v
