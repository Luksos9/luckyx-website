#!/usr/bin/env python3
"""Adds the conversion elements to courses/*.html. Idempotent, driven by data/courses.json.

Each generated block sits between <!-- lx:name --> and <!-- /lx:name --> comments, so
running the script again replaces the block instead of duplicating it.

    python3 scripts/enhance_course_pages.py          # apply
    python3 scripts/enhance_course_pages.py --check  # exit 1 if any file would change
"""
import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / 'data' / 'courses.json').read_text(encoding='utf-8'))
BY_SLUG = {c['slug']: c for c in DATA}

CSS = """
.cp-price-note{margin:-22px 0 26px;color:var(--text-dim);font-size:.85rem}
.cp-path{margin-top:22px;padding:16px 18px;border:1px solid var(--border);border-radius:12px;background:var(--bg-raised);font-size:.92rem;line-height:1.6;color:var(--text-dim)}
.cp-path p{margin:0}.cp-path p+p{margin-top:6px}.cp-path strong{color:var(--text)}.cp-path a{color:var(--orange);font-weight:600}
.quiz-buybar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px;margin:14px 0 0;padding:12px 16px;border-radius:12px;border:1px solid rgba(221,92,12,.25);background:rgba(221,92,12,.06);font-size:.9rem;color:var(--text-dim)}
.quiz-buybar a{display:inline-flex;padding:9px 16px;border-radius:10px;background:var(--orange);color:#fff;font-weight:600;font-size:.88rem;text-decoration:none;white-space:nowrap}
.quiz-buybar a:hover{background:#c75400;text-decoration:none}
.quiz-gate-alt{margin-top:12px;font-size:.88rem;color:var(--text-dim)}
.quiz-gate-alt a{color:var(--orange);font-weight:600}
.cp-faq{margin-top:48px}.cp-faq h2{font-size:1.3rem;font-weight:600;margin-bottom:16px}
.cp-faq details{border:1px solid var(--border);border-radius:12px;background:var(--bg-raised);margin-bottom:10px}
.cp-faq summary{cursor:pointer;padding:14px 18px;font-weight:600;font-size:.95rem;list-style:none}
.cp-faq summary::-webkit-details-marker{display:none}
.cp-faq summary::after{content:"+";float:right;color:var(--orange)}
.cp-faq details[open] summary::after{content:"\\2212"}
.cp-faq details p{margin:0;padding:0 18px 16px;color:var(--text-dim);font-size:.92rem;line-height:1.65}
.cp-faq details a{color:var(--orange);font-weight:600}
.cp-related{margin-top:6px}.cp-related a{display:inline-block;margin:4px 6px 0 0;padding:6px 12px;border:1px solid var(--border);border-radius:999px;font-size:.82rem}
@media (max-width:720px){.quiz-gate-email-input{flex:0 0 auto;width:100%}}
""".strip()


def region(name, body):
    return '<!-- lx:%s -->\n%s\n<!-- /lx:%s -->' % (name, body, name)


def put(html, name, body, anchor_re, where='after'):
    """Replace an existing region, or insert body next to the anchor match."""
    block = region(name, body)
    existing = re.compile(r'<!-- lx:%s -->.*?<!-- /lx:%s -->' % (name, name), re.S)
    if existing.search(html):
        return existing.sub(lambda _m: block, html, count=1)
    m = anchor_re.search(html)
    if not m:
        raise ValueError('anchor for %s not found' % name)
    pos = m.end() if where == 'after' else m.start()
    return html[:pos] + '\n' + block + '\n' + html[pos:] if where == 'after' else html[:pos] + block + '\n' + html[pos:]


def related_slugs(course):
    same_track = [c['slug'] for c in DATA if c['track'] == course['track'] and c['slug'] != course['slug']]
    out = []
    for slug in [course['next_slug']] + same_track + ['csa', 'cis-data-foundations']:
        if slug != course['slug'] and slug not in out:
            out.append(slug)
    return out[:3]


def link(slug):
    return '<a href="/courses/%s.html">%s</a>' % (slug, escape(BY_SLUG[slug]['page_title']))


def exam_fee_sentence(course):
    if course['slug'] in ('csa', 'cad'):
        return 'The exam costs $300 for a first attempt and $150 for a retake.'
    if course['slug'] == 'cas-pa':
        return None
    return 'The exam costs $450 for a first attempt and $225 for a retake.'


def faq_items(course):
    n = course['questions']
    code = course['code']
    items = [
        ('How many questions are in the full %s practice test?' % code,
         'The full course has %d questions on Udemy. Every answer option has its own explanation, and the explanations link to official ServiceNow documentation.' % n),
        ('Is there a refund if the course is not right for me?',
         'Yes. Udemy courses come with a 30-day money-back guarantee.'),
        ('Will this practice test guarantee I pass?',
         'No. Practice tests show you where you are weak. They do not replace hands-on work, so pair them with a free ServiceNow Personal Developer Instance.'),
    ]
    fee = exam_fee_sentence(course)
    if fee:
        items.append(('How much does the real %s exam cost?' % code, fee + ' Fees can change, so check ServiceNow University before you register.'))
    if course['requires_df']:
        items.append(('Do I need CIS-DF before %s?' % code,
                      'Yes. From January 1, 2027 you cannot register for this exam without CIS-DF. If you already hold this certification, you must pass CIS-DF by December 31, 2026. See the <a href="/courses/cis-data-foundations.html">CIS-DF practice test</a>.'))
    if course['slug'] == 'cis-data-foundations':
        items.append(('Which certifications require CIS-DF?',
                      'Seven CIS certifications: ITSM, Discovery, HAM, SAM, Service Mapping, SIR, and VR. From January 1, 2027 you cannot register for them without CIS-DF. Holders of those certifications must pass CIS-DF by December 31, 2026.'))
    items.append(('Which certification should I take first?',
                  'Most people start with CSA. If you are unsure, take the <a href="/quiz.html">2-minute recommendation quiz</a> or read the <a href="/blog/which-servicenow-certification-first.html">certification path guide</a>.'))
    return items


def faq_html(course):
    parts = ['<section class="cp-faq" id="faq"><h2>Common questions</h2>']
    for question, answer in faq_items(course):
        parts.append('<details><summary>%s</summary><p>%s</p></details>' % (escape(question), answer))
    parts.append('</section>')
    return '\n'.join(parts)


def faq_json_ld(course):
    def plain(text):
        return re.sub(r'<[^>]+>', '', text)
    data = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}}
            for q, a in faq_items(course)
        ],
    }
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(data, indent=2, ensure_ascii=False)


def bottom_html(course):
    code = course['code']
    lines = ['<div class="cp-bottom">']
    if course['blog']:
        lines.append('  <p>Read the full <a href="/blog/%s.html">%s study guide</a> for domain weights, a study plan, and common mistakes.</p>'
                     % (course['blog'], escape(code)))
    lines.append('  <p>Next step after %s: %s. Not the right exam? Take the <a href="/quiz.html">2-minute quiz</a> or <a href="/compare.html">compare all 18</a>.</p>'
                 % (escape(code), link(course['next_slug'])))
    lines.append('  <p class="cp-related">Related practice tests: %s</p>' % ' '.join(link(s) for s in related_slugs(course)))
    lines.append('  <a href="/#courses">Browse all 18 practice tests &rarr;</a>')
    lines.append('  <p style="margin-top:12px"><a href="/blog/which-servicenow-certification-first.html">Not sure which cert? See the full certification guide &rarr;</a></p>')
    lines.append('</div>')
    return '\n'.join(lines)


def path_html(course):
    lines = ['<div class="cp-path">']
    if course['requires_df']:
        lines.append('  <p><strong>Before you start:</strong> CIS-DF is a prerequisite for this exam from Jan 1, 2027. <a href="/courses/cis-data-foundations.html">See the CIS-DF practice test</a>.</p>')
    lines.append('  <p><strong>Next step:</strong> %s.</p>' % link(course['next_slug']))
    lines.append('</div>')
    return '\n'.join(lines)


def process(path):
    course = BY_SLUG[path.stem]
    html = path.read_text(encoding='utf-8')
    url = course['udemy_url'] + ('&amp;couponCode=' + course['coupon'] if course['coupon'] else '')
    n = course['questions']

    # hero CTA gets a stage so analytics can tell it from the final CTA
    html = re.sub(r'(<a href="[^"]+" target="_blank" rel="[^"]*" class="cp-cta")(>)', r'\1 data-buy-stage="hero"\2', html, count=1) \
        if 'class="cp-cta" data-buy-stage="hero"' not in html else html

    html = put(html, 'price-note', '<p class="cp-price-note">Price is shown at checkout on Udemy. 30-day money-back guarantee.</p>',
               re.compile(r'<div class="cp-price-row">.*?</div>', re.S))
    html = put(html, 'path', path_html(course), re.compile(r'<a href="[^"]+" target="_blank" rel="[^"]*" class="cp-cta" data-buy-stage="hero">.*?</a>', re.S))
    buybar = ('<div class="quiz-buybar"><span>Skip the preview and get all %d questions on Udemy.</span>'
              '<a href="%s" target="_blank" rel="sponsored noopener" data-buy-stage="stepper">Get the full course &rarr;</a></div>' % (n, url))
    html = put(html, 'buybar', buybar, re.compile(r'<div class="quiz-stepper-dots" id="quizProgress">.*?</div>', re.S))
    gate_alt = ('<p class="quiz-gate-alt">Prefer to skip the email? '
                '<a href="%s" target="_blank" rel="sponsored noopener" data-buy-stage="gate">Get all %d questions on Udemy</a>. 30-day money-back guarantee.</p>' % (url, n))
    html = put(html, 'gate-alt', gate_alt, re.compile(r'<p class="quiz-gate-message" id="quizGateMessage"></p>'))

    tail = region('faq', faq_html(course)) + '\n\n  ' + region('bottom', bottom_html(course))
    if '<!-- lx:faq -->' in html:
        html = re.sub(r'<!-- lx:faq -->.*?<!-- /lx:faq -->', lambda _m: region('faq', faq_html(course)), html, count=1, flags=re.S)
        html = re.sub(r'<!-- lx:bottom -->.*?<!-- /lx:bottom -->', lambda _m: region('bottom', bottom_html(course)), html, count=1, flags=re.S)
    else:
        m = re.search(r'<div class="cp-bottom">.*?</div>', html, re.S)
        if not m:
            raise ValueError('cp-bottom not found in %s' % path.name)
        html = html[:m.start()] + tail + html[m.end():]

    html = put(html, 'faq-ld', faq_json_ld(course), re.compile(r'"@type": "BreadcrumbList".*?</script>', re.S))
    html = put(html, 'css', '<style>\n%s\n</style>' % CSS, re.compile(r'<script defer src="/analytics\.js"></script>'), where='before')
    return path.read_text(encoding='utf-8'), html


def main():
    check = '--check' in sys.argv
    changed = 0
    for path in sorted((ROOT / 'courses').glob('*.html')):
        before, after = process(path)
        if before != after:
            changed += 1
            if not check:
                path.write_text(after, encoding='utf-8')
    print('%d file(s) %s' % (changed, 'need changes' if check else 'updated'))
    return 1 if (check and changed) else 0


if __name__ == '__main__':
    sys.exit(main())
