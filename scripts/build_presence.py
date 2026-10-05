#!/usr/bin/env python3
"""Build the existing static site with verified ZYK identity and channel pages.

Standard library only. No social API calls, credentials, or publishing actions.
"""
import argparse
import html
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = 'https://zykai.net'
EMAIL = 'hello@zykai.net'
LEGACY_IDS = {'318077031657092', '4540708', '_000RnCdMwdLs183UxqWEBIQTb-y-Qu_4EKX', '40779'}
HOSTS = {
    'facebook': {'facebook.com', 'www.facebook.com'},
    'linkedin': {'linkedin.com', 'www.linkedin.com'},
    'instagram': {'instagram.com', 'www.instagram.com'},
    'threads': {'threads.com', 'www.threads.com', 'threads.net', 'www.threads.net'},
    'x': {'x.com', 'www.x.com'},
    'tiktok': {'tiktok.com', 'www.tiktok.com'},
    'youtube': {'youtube.com', 'www.youtube.com'},
}
COPY = {
    'en': ['Official channels', 'One ZYK identity. Clear, verified contact details.',
           'ZhiAn YunKe brings education, institutional AI and responsible implementation together.',
           'Website', 'Contact', 'Social channels',
           'Our dedicated ZYK social presence is being established. Confirmed profiles will be listed here; no social profile is currently listed as an official ZYK channel.',
           'Our story',
           'Earlier William Morris and Oxbridge College identities belong to our founder\u2019s professional history. They are not ZYK social accounts and do not imply ownership or formal affiliation.',
           'Read the background', 'View profile'],
    'zh-cn': ['\u5b98\u65b9\u6e20\u9053', '\u7edf\u4e00\u7684ZYK\u54c1\u724c\uff0c\u6e05\u6670\u53ef\u6838\u5b9e\u7684\u8054\u7cfb\u65b9\u5f0f\u3002',
              '\u667a\u5b89\u4e91\u79d1\u5c06\u6559\u80b2\u7ecf\u9a8c\u3001\u673a\u6784\u7ea7AI\u4e0e\u8d1f\u8d23\u4efb\u7684\u5b9e\u8df5\u76f8\u7ed3\u5408\u3002',
              '\u5b98\u65b9\u7f51\u7ad9', '\u8054\u7cfb\u6211\u4eec', '\u793e\u4ea4\u5a92\u4f53',
              'ZYK\u4e13\u5c5e\u793e\u4ea4\u5a92\u4f53\u6e20\u9053\u6b63\u5728\u5efa\u7acb\u3002\u7ecf\u6838\u5b9e\u7684\u8d26\u53f7\u5c06\u5728\u6b64\u5217\u51fa\uff1b\u76ee\u524d\u6682\u672a\u5217\u51fa\u5b98\u65b9ZYK\u793e\u4ea4\u8d26\u53f7\u3002',
              '\u6211\u4eec\u7684\u80cc\u666f',
              'William Morris\u53caOxbridge College\u7684\u65e9\u671f\u8eab\u4efd\u5c5e\u4e8e\u521b\u59cb\u4eba\u7684\u4e13\u4e1a\u7ecf\u5386\uff0c\u5e76\u975eZYK\u793e\u4ea4\u8d26\u53f7\uff0c\u4e5f\u4e0d\u4ee3\u8868\u6240\u6709\u6743\u6216\u6b63\u5f0f\u96b6\u5c5e\u5173\u7cfb\u3002',
              '\u4e86\u89e3\u80cc\u666f', '\u67e5\u770b\u8d26\u53f7'],
    'zh-hk': ['\u5b98\u65b9\u6e20\u9053', '\u7d71\u4e00\u7684ZYK\u54c1\u724c\uff0c\u6e05\u6670\u53ef\u6838\u5be6\u7684\u806f\u7d61\u65b9\u5f0f\u3002',
              '\u667a\u5b89\u96f2\u79d1\u5c07\u6559\u80b2\u7d93\u9a57\u3001\u6a5f\u69cb\u7d1aAI\u8207\u8ca0\u8cac\u4efb\u7684\u5be6\u8e10\u76f8\u7d50\u5408\u3002',
              '\u5b98\u65b9\u7db2\u7ad9', '\u806f\u7d61\u6211\u5011', '\u793e\u4ea4\u5a92\u9ad4',
              'ZYK\u5c08\u5c6c\u793e\u4ea4\u5a92\u9ad4\u6e20\u9053\u6b63\u5728\u5efa\u7acb\u3002\u7d93\u6838\u5be6\u7684\u5e33\u6236\u5c07\u5728\u6b64\u5217\u51fa\uff1b\u76ee\u524d\u66ab\u672a\u5217\u51fa\u5b98\u65b9ZYK\u793e\u4ea4\u5e33\u6236\u3002',
              '\u6211\u5011\u7684\u80cc\u666f',
              'William Morris\u53caOxbridge College\u7684\u65e9\u671f\u8eab\u4efd\u5c6c\u65bc\u5275\u8fa6\u4eba\u7684\u5c08\u696d\u7d93\u6b77\uff0c\u4e26\u975eZYK\u793e\u4ea4\u5e33\u6236\uff0c\u4e5f\u4e0d\u4ee3\u8868\u6240\u6709\u6b0a\u6216\u6b63\u5f0f\u96b8\u5c6c\u95dc\u4fc2\u3002',
              '\u4e86\u89e3\u80cc\u666f', '\u67e5\u770b\u5e33\u6236'],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(config, queue):
    require(config['website'] == DOMAIN and config['email'] == EMAIL, 'Canonical identity changed')
    require(config['name'] == 'ZhiAn YunKe' and config['short_name'] == 'ZYK', 'Brand name changed')
    require(config['publishing_enabled'] is False, 'This release is preparation-only; no social publisher is installed')
    seen = set()
    for profile in config['verified_profiles']:
        platform = profile['platform']
        account = str(profile['account_id'])
        url = urlparse(profile['url'])
        require(platform in HOSTS, 'Unknown platform')
        require(account not in LEGACY_IDS, 'Historical account is forbidden as a ZYK destination')
        require(profile['ownership_confirmed'] is True and profile['brand'] == 'ZYK', 'ZYK ownership is not confirmed')
        require(bool(profile.get('verified_at')) and bool(profile.get('verification_note')), 'Verification evidence is missing')
        require(url.scheme == 'https' and url.hostname in HOSTS[platform] and url.path not in ('', '/'), 'Invalid profile URL')
        require(not url.username and not url.password and not url.query and not url.fragment, 'Profile URLs must not contain credentials or tracking data')
        require((platform, account) not in seen, 'Duplicate social account')
        seen.add((platform, account))
    ids = set()
    for post in queue['posts']:
        require(post['id'] not in ids, 'Duplicate post ID')
        ids.add(post['id'])
        require(post['status'] in ('draft', 'approved'), 'Unsupported post status')
        require(post['status'] != 'approved' or bool(post.get('approved_at')), 'Approved content needs approval evidence')
        require(bool(post['body_en'].strip()) and bool(post['body_zh_cn'].strip()), 'Missing bilingual copy')
        require(all(platform in HOSTS for platform in post['platforms']), 'Unknown post platform')
        target = urlparse(post['landing_url'])
        require(target.scheme == 'https' and target.netloc == 'zykai.net' and not target.query and not target.fragment, 'Landing pages must use the canonical domain')
    return len(ids)


def channel_page(template, lang, profiles):
    c = [html.escape(item) for item in COPY[lang]]
    social = '<p>' + c[6] + '</p>'
    if profiles:
        social = ''.join('<p><a rel="me noopener" href="{}">{}: {}</a></p>'.format(
            html.escape(p['url'], quote=True), html.escape(p['platform'].title()), c[10]) for p in profiles)
    main = ('<main><section class="hero"><div class="wrap"><div class="eyebrow">ZYK / ZhiAn YunKe</div>'
            '<h1>' + c[1] + '</h1><p class="lead">' + c[2] + '</p></div></section>'
            '<section class="section"><div class="wrap"><h2>' + c[0] + '</h2><div class="grid">'
            '<article class="card"><h3>' + c[3] + '</h3><p><a href="' + DOMAIN + '">zykai.net</a></p></article>'
            '<article class="card"><h3>' + c[4] + '</h3><p><a href="mailto:' + EMAIL + '">' + EMAIL + '</a></p></article>'
            '<article class="card"><h3>' + c[5] + '</h3>' + social + '</article></div></div></section>'
            '<section class="section alt"><div class="wrap"><h2>' + c[7] + '</h2><p class="intro">' + c[8] + '</p>'
            '<a class="textlink" href="about.html">' + c[9] + '</a></div></section></main>')
    require(len(re.findall(r'<main\b', template, re.I)) == 1, 'Template must contain one main element')
    result = re.sub(r'<main\b[^>]*>.*?</main>', lambda _: main, template, count=1, flags=re.S | re.I)
    result = re.sub(r'<title>.*?</title>', lambda _: '<title>' + c[0] + ' | ZYK / ZhiAn YunKe</title>', result, count=1, flags=re.S | re.I)
    result = re.sub(r'<meta\b(?=[^>]*\bname=[\"\']description[\"\'])[^>]*>', lambda _: '<meta name="description" content="' + c[2] + '">', result, flags=re.I)
    for locale in COPY:
        result = result.replace('../' + locale + '/index.html', '../' + locale + '/channels.html')
    return result


def enrich(document, relative, config, site):
    # Work only on the build output: preserve every authored source page.
    document = re.sub(r'<!-- ZYK PRESENCE START -->.*?<!-- ZYK PRESENCE END -->', '', document, flags=re.S)
    url = DOMAIN + '/' + relative.as_posix()
    if relative.as_posix() == 'index.html':
        url = DOMAIN + '/'
    title_match = re.search(r'<title>(.*?)</title>', document, re.S | re.I)
    title = html.escape(html.unescape(title_match.group(1)) if title_match else config['name'], quote=True)
    schema = {'@context': 'https://schema.org', '@type': 'Brand', '@id': DOMAIN + '/#brand',
              'name': config['name'], 'alternateName': [config['short_name'], config['name_zh_cn']], 'url': DOMAIN + '/'}
    if config['verified_profiles']:
        schema['sameAs'] = [p['url'] for p in config['verified_profiles']]
    metadata = [f'<link rel="canonical" href="{url}">', '<meta property="og:type" content="website">',
                f'<meta property="og:site_name" content="ZYK / ZhiAn YunKe">',
                f'<meta property="og:title" content="{title}">', f'<meta property="og:url" content="{url}">',
                '<meta name="twitter:card" content="summary">',
                '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>']
    description = re.search(r'<meta\b[^>]*name="description"[^>]*content="([^"]*)"', document, re.I)
    if description:
        metadata.append('<meta property="og:description" content="' + description.group(1) + '">')
    if len(relative.parts) == 2 and relative.parts[0] in COPY:
        for lang in COPY:
            if (site / lang / relative.name).is_file():
                metadata.append(f'<link rel="alternate" hreflang="{lang}" href="{DOMAIN}/{lang}/{relative.name}">')
        if (site / 'en' / relative.name).is_file():
            metadata.append(f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}/en/{relative.name}">')
        footer = ('<div class="wrap"><p data-zyk-presence="true"><a href="channels.html">' + COPY[relative.parts[0]][0] + '</a> &middot; '
                  '<a href="mailto:' + EMAIL + '">' + EMAIL + '</a></p></div>')
        require('</footer>' in document.lower(), 'Localised source page has no footer: ' + str(relative))
        document = re.sub(r'</footer>', lambda _: footer + '</footer>', document, count=1, flags=re.I)
    # Existing authored metadata wins, except the canonical brand block is always supplied.
    for tag in metadata[:]:
        key = re.search(r'(?:name|property|rel)="([^"]+)"', tag)
        if key and key.group(1) not in ('alternate',) and re.search(r'(?:name|property|rel)=[\"\']' + re.escape(key.group(1)) + r'[\"\']', document, re.I):
            metadata.remove(tag)
    block = '<!-- ZYK PRESENCE START -->' + ''.join(metadata) + '<!-- ZYK PRESENCE END -->'
    require('</head>' in document.lower(), 'HTML document has no head')
    return re.sub(r'</head>', lambda _: block + '</head>', document, count=1, flags=re.I)


def check_live():
    paths = ['/en/channels.html', '/zh-cn/channels.html', '/zh-hk/channels.html', '/channels.json']
    for path in paths:
        request = urllib.request.Request(DOMAIN + path, headers={'User-Agent': 'ZYK-Presence-Health/1.0'})
        with urllib.request.urlopen(request, timeout=30) as response:
            require(response.status == 200 and urlparse(response.url).hostname == 'zykai.net', 'Unexpected live response')
            text = response.read(1000000).decode('utf-8')
        require(EMAIL in text and 'ZhiAn YunKe' in text, 'Live identity missing: ' + path)
        if path.endswith('.json'):
            register = json.loads(text)
            require(register['website'] == DOMAIN and register['email'] == EMAIL, 'Live register mismatch')
        print('LIVE PASS ' + path)


def build():
    config = json.loads((ROOT / 'brand/presence.json').read_text(encoding='utf-8'))
    queue = json.loads((ROOT / 'brand/social-launch.json').read_text(encoding='utf-8'))
    count = validate(config, queue)
    source, site = ROOT / 'public-site', ROOT / 'site'
    require(source.is_dir() and source != site and not site.is_symlink(), 'Invalid build paths')
    for lang in COPY:
        require((source / lang / 'index.html').is_file(), 'Missing language home page: ' + lang)
    if site.exists():
        shutil.rmtree(site)
    shutil.copytree(source, site)
    for lang in COPY:
        template = (source / lang / 'index.html').read_text(encoding='utf-8')
        (site / lang / 'channels.html').write_text(channel_page(template, lang, config['verified_profiles']), encoding='utf-8')
    pages = sorted(site.rglob('*.html'))
    for path in pages:
        path.write_text(enrich(path.read_text(encoding='utf-8'), path.relative_to(site), config, site), encoding='utf-8')
    public_register = {key: config[key] for key in ('name', 'short_name', 'name_zh_cn', 'website', 'email')}
    public_register['profiles'] = [{'platform': p['platform'], 'url': p['url']} for p in config['verified_profiles']]
    (site / 'channels.json').write_text(json.dumps(public_register, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    sitemap = ET.Element('{' + namespace + '}urlset')
    for path in pages:
        if path.name == '404.html':
            continue
        node = ET.SubElement(sitemap, '{' + namespace + '}url')
        ET.SubElement(node, '{' + namespace + '}loc').text = DOMAIN + '/' + path.relative_to(site).as_posix()
    ET.ElementTree(sitemap).write(site / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (site / 'CNAME').write_text('zykai.net\n', encoding='utf-8')
    # Queue and account evidence stay out of the public Pages artifact.
    require(not (site / 'brand').exists(), 'Operational data must not be deployed')
    for path in pages:
        text = path.read_text(encoding='utf-8')
        require('2026wm@gmail.com' not in text and 'editormorris@gmail.com' not in text, 'Private administrative email in public output')
        for href in re.findall(r'(?:href|src)=[\"\']([^\"\']+)', text):
            parsed = urlparse(href)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (site / parsed.path.lstrip('/')) if parsed.path.startswith('/') else path.parent / parsed.path
            require(target.resolve().is_relative_to(site.resolve()), 'Link escapes site: ' + href)
            require(target.exists(), 'Broken local link: ' + str(path.relative_to(site)) + ' -> ' + href)
    print(json.dumps({'html_pages': len(pages), 'social_drafts': count,
                      'verified_social_destinations': len(config['verified_profiles']),
                      'social_publishing_enabled': False, 'result': 'PASS'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-live', action='store_true')
    arguments = parser.parse_args()
    try:
        build()
        if arguments.check_live:
            check_live()
    except (ValueError, KeyError, OSError) as error:
        print('PRESENCE CHECK FAILED: ' + str(error), file=sys.stderr)
        sys.exit(1)
