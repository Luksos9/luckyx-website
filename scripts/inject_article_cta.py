#!/usr/bin/env python3
"""Adds a course call to action to study guides that have no Udemy link. Idempotent.

The block sits between <!-- lx:article-cta --> markers, so rerunning replaces it. Course facts
come from data/courses.json.

    python3 scripts/inject_article_cta.py          # apply
    python3 scripts/inject_article_cta.py --check  # exit 1 if any article would change
"""
import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSES = {c['slug']: c for c in json.loads((ROOT / 'data' / 'courses.json').read_text(encoding='utf-8'))}

# article file -> courses it should send readers to
ARTICLES = {
    'best-servicenow-practice-tests-2026': ['csa', 'cis-data-foundations'],
    'cis-df-mandate-explained': ['cis-data-foundations'],
    'csa-to-cta-career-path': ['csa', 'cad'],
    'exam-dumps-vs-practice-tests': ['csa', 'cis-data-foundations'],
    'free-csa-practice-test': ['csa'],
    'free-servicenow-study-resources': ['csa', 'cis-data-foundations'],
    'how-to-pass-cis-discovery-2026': ['cis-discovery', 'cis-service-mapping'],
    'how-to-pass-cis-ham-sam-2026': ['cis-ham', 'cis-sam'],
    'how-to-pass-cis-sir-vr-2026': ['cis-sir', 'cis-vr'],
    'how-to-study-for-servicenow-exams': ['csa', 'cad'],
    'servicenow-certification-cost-2026': ['csa', 'cis-data-foundations'],
    'servicenow-certification-landscape-2026': ['csa', 'cis-data-foundations'],
    'servicenow-certification-path-2026': ['csa', 'cis-data-foundations'],
    'servicenow-micro-certifications-guide': ['csa'],
    'servicenow-salary-guide-2026': ['csa', 'cis-data-foundations'],
    'servicenow-vs-salesforce-certification': ['csa', 'cis-data-foundations'],
    'which-servicenow-certification-first': ['csa', 'cis-data-foundations'],
}

REGION = re.compile(r'<!-- lx:article-cta -->.*?<!-- /lx:article-cta -->', re.S)


def block(slugs):
    parts = ['<!-- lx:article-cta -->', '        <div class="bp-cta-box">']
    for slug in slugs:
        c = COURSES[slug]
        parts.append('          <p><strong>%s</strong>: %d practice questions, with an explanation for every answer option.</p>'
                     % (escape(c['page_title']), c['questions']))
        parts.append('          <a href="%s" target="_blank" rel="sponsored noopener" class="bp-cta-btn">Get the %s practice test</a>'
                     % (escape(c['udemy_url']), escape(c['code'])))
    first = COURSES[slugs[0]]['slug']
    parts.append('          <p style="margin-top:14px"><a href="/courses/%s.html#free-quiz">Try 15 free questions first</a></p>' % first)
    parts.append('        </div>')
    parts.append('<!-- /lx:article-cta -->')
    return '\n'.join(parts)


def process(path, slugs):
    text = path.read_text(encoding='utf-8')
    new_block = block(slugs)
    if REGION.search(text):
        return text, REGION.sub(lambda _m: new_block, text, count=1)
    for anchor in ('<!-- EMAIL CAPTURE -->', '<div class="bp-email-section">', '</article>'):
        i = text.find(anchor)
        if i != -1:
            return text, text[:i] + new_block + '\n\n        ' + text[i:]
    raise ValueError('no anchor in %s' % path.name)


def main():
    check = '--check' in sys.argv
    changed = 0
    for name, slugs in ARTICLES.items():
        path = ROOT / 'blog' / ('%s.html' % name)
        before, after = process(path, slugs)
        if before != after:
            changed += 1
            if not check:
                path.write_text(after, encoding='utf-8')
    print('%d file(s) %s' % (changed, 'need changes' if check else 'updated'))
    return 1 if (check and changed) else 0


if __name__ == '__main__':
    sys.exit(main())
