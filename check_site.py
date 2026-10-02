#!/usr/bin/env python3
"""Consistency checks for the static site. Run before every commit:

    python3 check_site.py

Exits 1 and prints every problem when something is off. Source of truth for course
facts is data/courses.json.
"""
import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
from fix_course_pages import BLOCK, MARK_BEFORE_QUOTE, MARK_BEFORE_TAG, MARK_BEFORE_TEXT, RUN_ON, STEM, STEM_MARK  # noqa: E402

COURSES = json.loads((ROOT / 'data' / 'courses.json').read_text(encoding='utf-8'))
SKIP_DIRS = {'legacy', 'preview_source', 'node_modules', '.git', 'scripts', 'data'}
errors = []


def err(where, msg):
    errors.append('%s: %s' % (where, msg))


def html_files():
    for path in sorted(ROOT.rglob('*.html')):
        if SKIP_DIRS & set(path.relative_to(ROOT).parts[:-1]):
            continue
        yield path


def rel(path):
    return str(path.relative_to(ROOT))


# ------------------------------------------------------------------ stale claims
FREE_WINDOW = re.compile(r'\bfree\b[^.]{0,80}(?:June|Dec(?:ember)?)\s+(?:30,\s+)?2026|(?:June|Dec(?:ember)?)\s+(?:30,\s+)?2026[^.]{0,80}\bfree\b', re.I)
PAST = re.compile(r'\b(ended|closed|closes|offered|had|was|were|expired|waived|no longer|since)\b', re.I)


def check_stale():
    files = list(html_files()) + [ROOT / 'llms.txt']
    for path in files:
        text = path.read_text(encoding='utf-8')
        for m in re.finditer(r'\$350', text):
            err('%s:%d' % (rel(path), text.count('\n', 0, m.start()) + 1), 'wrong retake fee ($350)')
        for m in re.finditer(r'[^.<>]*\.|[^.<>]+(?=<)', text):
            sentence = m.group(0)
            if FREE_WINDOW.search(sentence) and not PAST.search(sentence):
                err('%s:%d' % (rel(path), text.count('\n', 0, m.start()) + 1),
                    'free-attempt window stated in the present tense: %s' % ' '.join(sentence.split())[:110])


# ------------------------------------------------------------------ corrupted question marks
def check_marks():
    for path in sorted((ROOT / 'courses').glob('*.html')):
        text = path.read_text(encoding='utf-8')
        for part in BLOCK.split(text):
            if BLOCK.fullmatch(part):
                continue
            for pat in (MARK_BEFORE_TAG, MARK_BEFORE_TEXT, MARK_BEFORE_QUOTE):
                for m in pat.finditer(part):
                    err(rel(path), 'hyphen where a question mark was lost: ...%s' % part[max(0, m.start() - 30):m.end() + 10].strip())
        for m in STEM.finditer(text):
            if RUN_ON.search(re.sub(r'<[^>]+>', '', m.group(2))):
                err(rel(path), 'question stem has two sentences run together: ...%s' % re.sub(r'<[^>]+>', '', m.group(2))[-60:])
            if STEM_MARK.search(m.group(2)):
                err(rel(path), 'question stem still ends with a spaced hyphen: ...%s' % re.sub(r'<[^>]+>', '', m.group(2))[-50:])
        if 'css2-family=' in text:
            err(rel(path), 'broken Google Fonts URL (css2-family)')


# ------------------------------------------------------------------ JSON-LD
def check_json_ld():
    for path in html_files():
        text = path.read_text(encoding='utf-8')
        for m in re.finditer(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', text, re.S):
            try:
                json.loads(m.group(1))
            except ValueError as exc:
                err(rel(path), 'invalid JSON-LD: %s' % exc)


# ------------------------------------------------------------------ cross-page course data
def check_course_data():
    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    compare = (ROOT / 'compare.html').read_text(encoding='utf-8')
    llms = (ROOT / 'llms.txt').read_text(encoding='utf-8')
    for c in COURSES:
        slug = c['slug']
        row = re.search(r'\{ title:"[^"]*", code:"%s", slug:"%s".*?\}' % (re.escape(c['code']), slug), index)
        if not row:
            err('index.html', 'missing course entry %s' % slug)
        else:
            r = row.group(0)
            for key, val in (('rating', c['rating']), ('ratings', c['reviews']), ('q', c['questions'])):
                m = re.search(r'\b%s:([\d.]+)' % key, r)
                if not m or abs(float(m.group(1)) - val) > 1e-9:
                    err('index.html', '%s %s differs from data/courses.json (%s)' % (slug, key, val))
            if c['udemy_url'] not in r:
                err('index.html', '%s Udemy URL differs from data/courses.json' % slug)
        row = re.search(r"\{ name:'[^']*', code:'%s', slug:'%s'.*?\}" % (re.escape(c['code']), slug), compare)
        if not row:
            err('compare.html', 'missing course entry %s' % slug)
        else:
            r = row.group(0)
            for key, val in (('questions', c['questions']), ('rating', c['rating']), ('reviews', c['reviews'])):
                m = re.search(r'\b%s:([\d.]+)' % key, r)
                if not m or abs(float(m.group(1)) - val) > 1e-9:
                    err('compare.html', '%s %s differs from data/courses.json (%s)' % (slug, key, val))
            if c['udemy_url'] not in r:
                err('compare.html', '%s Udemy URL differs from data/courses.json' % slug)
            has_df = 'CIS-DF' in re.search(r"prereq:'(.*?)'", r).group(1)
            if has_df != c['requires_df']:
                err('compare.html', '%s prerequisite column disagrees with requires_df' % slug)
        if not re.search(r'luckyx\.dev/courses/%s\.html\): %d questions' % (slug, c['questions']), llms):
            err('llms.txt', '%s question count differs from data/courses.json (%d)' % (slug, c['questions']))

        page = ROOT / 'courses' / ('%s.html' % slug)
        text = page.read_text(encoding='utf-8')
        m = re.search(r'aria-label="Rating: ([\d.]+) out of 5 stars, (\d+) reviews"', text)
        if not m or abs(float(m.group(1)) - c['rating']) > 1e-9 or int(m.group(2)) != c['reviews']:
            err(rel(page), 'visible rating differs from data/courses.json')
        if '(%d reviews)' % c['reviews'] not in text:
            err(rel(page), 'visible review count missing or wrong')
        ld = re.search(r'"aggregateRating": \{\s*"@type": "AggregateRating",\s*"ratingValue": "([\d.]+)",\s*"reviewCount": "(\d+)"', text)
        if not ld or abs(float(ld.group(1)) - c['rating']) > 1e-9 or int(ld.group(2)) != c['reviews']:
            err(rel(page), 'JSON-LD aggregateRating differs from visible rating')
        if '%d questions' % c['questions'] not in text:
            err(rel(page), 'question count %d not shown' % c['questions'])
        if text.count(c['udemy_url']) < 2:
            err(rel(page), 'Udemy link missing or differs from data/courses.json')


# ------------------------------------------------------------------ links and images
URL_ATTR = re.compile(r'\b(?:href|src)="([^"]+)"')


def check_links():
    sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
    for path in html_files():
        text = path.read_text(encoding='utf-8')
        text = re.sub(r'<script\b[^>]*>.*?</script>', '', text, flags=re.S | re.I)
        for m in URL_ATTR.finditer(text):
            url = unescape(m.group(1)).strip()
            if (not url or url.startswith(('#', 'http://', 'https://', 'mailto:', 'tel:', 'data:', 'javascript:', '//'))
                    or '${' in url or "'+" in url or '+\'' in url):
                continue
            parsed = urlparse(url)
            target = unquote(parsed.path)
            base = ROOT if target.startswith('/') else path.parent
            dest = (base / target.lstrip('/')).resolve()
            if dest.is_dir():
                dest = dest / 'index.html'
            if not dest.exists():
                err(rel(path), 'broken link %s' % url)
    for loc in re.findall(r'<loc>https://luckyx\.dev(/[^<]*)</loc>', sitemap):
        dest = ROOT / loc.lstrip('/')
        if dest.is_dir() or loc.endswith('/'):
            dest = dest / 'index.html'
        if not dest.exists():
            err('sitemap.xml', 'URL has no file: %s' % loc)


def check_article_count():
    count = len([p for p in (ROOT / 'blog').glob('*.html') if p.name != 'index.html'])
    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    m = re.search(r'View all (\d+) study guides', index)
    if not m or int(m.group(1)) != count:
        err('index.html', 'study guide count says %s, blog has %d articles' % (m.group(1) if m else 'nothing', count))
    blog_index = (ROOT / 'blog' / 'index.html').read_text(encoding='utf-8')
    for path in sorted((ROOT / 'blog').glob('*.html')):
        if path.name != 'index.html' and ('/blog/%s' % path.name) not in blog_index:
            err('blog/index.html', 'no card links to %s' % path.name)
    llms = (ROOT / 'llms.txt').read_text(encoding='utf-8')
    for path in sorted((ROOT / 'blog').glob('*.html')):
        if path.name != 'index.html' and ('/blog/%s' % path.name) not in llms:
            err('llms.txt', 'article not listed: %s' % path.name)


def check_generators():
    """The generated parts must match what the scripts produce, so hand edits do not drift."""
    import subprocess
    for script in ('fix_course_pages.py', 'enhance_course_pages.py', 'inject_article_cta.py', 'render_compare.py', 'apply_coupons.py',
                   'mark_affiliate_links.py', 'add_consent.py'):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts' / script), '--check'], capture_output=True, text=True)
        if result.returncode != 0:
            err('scripts/' + script, 'output is out of date, run it without --check. ' + result.stdout.strip().replace('\n', ' | ')[:160])


def main():
    check_article_count()
    check_generators()
    check_stale()
    check_marks()
    check_json_ld()
    check_course_data()
    check_links()
    if errors:
        for e in errors:
            print(e)
        print('\n%d problem(s)' % len(errors))
        return 1
    print('check_site: all checks passed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
