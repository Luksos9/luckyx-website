#!/usr/bin/env python3
"""Idempotent repairs for courses/*.html.

courses/*.html is the source of truth. This script edits those files in place and
can be run repeatedly. Course facts (ratings, review counts, retake fees) come
from data/courses.json.

    python3 scripts/fix_course_pages.py          # apply
    python3 scripts/fix_course_pages.py --check  # exit 1 if any file would change
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSES = {c['slug']: c for c in json.loads((ROOT / 'data' / 'courses.json').read_text(encoding='utf-8'))}

BLOCK = re.compile(r'(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>)', re.S | re.I)
LD_JSON = re.compile(r'(<script type="application/ld\+json">\s*)(.*?)(\s*</script>)', re.S)

# A "?" was replaced by "-" somewhere upstream. Real hyphens are always inside a word,
# so a hyphen glued to a word and followed by a tag, whitespace plus a capital letter,
# or "(Choose ...)" is a lost question mark.
LOOKBEHIND = r"(?<=[A-Za-z0-9)’'\"\]])"
MARK_BEFORE_TAG = re.compile(LOOKBEHIND + r"-(?=\s*<)")
MARK_BEFORE_TEXT = re.compile(LOOKBEHIND + r"-(?=\s+(?:\(?(?:[Cc]hoose|[Ss]elect)\b|[A-Z(“\"‘]))")


MARK_BEFORE_QUOTE = re.compile(LOOKBEHIND + r"-(?=[\"\u201d)])")


def repair_marks_text(text):
    return MARK_BEFORE_QUOTE.sub('?', MARK_BEFORE_TEXT.sub('?', MARK_BEFORE_TAG.sub('?', text)))


def repair_marks_str(value):
    """Same repair for a JSON string value, where the string end also ends the sentence."""
    return MARK_BEFORE_QUOTE.sub('?', MARK_BEFORE_TEXT.sub('?', re.sub(LOOKBEHIND + r'-$', '?', value)))


def repair_marks_json(node):
    if isinstance(node, str):
        return repair_marks_str(node)
    if isinstance(node, list):
        return [repair_marks_json(item) for item in node]
    if isinstance(node, dict):
        return {key: repair_marks_json(item) for key, item in node.items()}
    return node


def repair_marks(html):
    parts = BLOCK.split(html)
    return ''.join(p if BLOCK.fullmatch(p) else repair_marks_text(p) for p in parts)


def fix_fonts(html):
    return html.replace('/css2-family=', '/css2?family=')


def sentence_prefix(text, limit=200):
    """Longest run of whole sentences that fits the limit."""
    sentences = re.findall(r'.+?[.!?](?:\s+|$)', text.strip() + ' ')
    out = ''
    for s in sentences:
        if len((out + s).strip()) > limit:
            break
        out += s
    return out.strip() or text.strip()[:limit].rsplit(' ', 1)[0]


META_OVERRIDES = {
    'cis-data-foundations': 'CIS-Data Foundations is a prerequisite for 7 CIS certifications from Jan 1, 2027. '
                            '470 practice questions cover CMDB health, CSDM, and data quality.',
}


def fix_meta_description(html, slug):
    og = re.search(r'<meta property="og:description" content="(.*?)">', html)
    if not og:
        return html
    desc = META_OVERRIDES.get(slug) or sentence_prefix(og.group(1))
    return re.sub(r'(<meta name="description" content=")(.*?)(">)',
                  lambda m: m.group(1) + desc + m.group(3), html, count=1)


def fix_stale_claims(html, course):
    html = html.replace('First attempt is free through June 2026. ', '')
    html = html.replace('CIS-Data Foundations is now mandatory for 7 CIS certifications.',
                        'CIS-Data Foundations is a prerequisite for 7 CIS certifications from Jan 1, 2027.')
    html = re.sub(
        r'(<div class="countdown-headline">).*?(</div>)',
        r'\1CIS-DF becomes a prerequisite for 7 CIS certifications on Jan 1, 2027. '
        r'Existing holders of those certifications must pass it by Dec 31, 2026.\2',
        html, flags=re.S)
    fee = course['retake_fee_usd']
    anchor = ('A failed exam attempt costs $%d to retake.' % fee) if fee else 'A failed exam attempt means paying a retake fee.'
    html = re.sub(r'<p class="quiz-final-anchor">.*?</p>', '<p class="quiz-final-anchor">%s</p>' % anchor, html)
    return html


def fix_rating_count(html, course):
    label = '(%d reviews)' % course['reviews']
    return re.sub(r'<span class="cp-rating-count"></span>',
                  '<span class="cp-rating-count">%s</span>' % label, html)


def fix_json_ld(html, course):
    def edit(match):
        head, body, tail = match.groups()
        try:
            data = json.loads(body)
        except ValueError:
            return match.group(0)
        kind = data.get('@type')
        if kind == 'Course':
            data.pop('numberOfCredits', None)
            if isinstance(data.get('hasCourseInstance'), dict):
                data['hasCourseInstance'].pop('courseWorkload', None)
            data['aggregateRating'] = {
                '@type': 'AggregateRating',
                'ratingValue': ('%.2f' % course['rating']).rstrip('0').rstrip('.'),
                'reviewCount': str(course['reviews']),
                'bestRating': '5',
                'worstRating': '1',
            }
        elif kind == 'Quiz':
            data = repair_marks_json(data)
        else:
            return match.group(0)
        return head + json.dumps(data, indent=2, ensure_ascii=False) + tail
    return LD_JSON.sub(edit, html)


def process(path):
    slug = path.stem
    course = COURSES[slug]
    html = path.read_text(encoding='utf-8')
    new = html
    new = repair_marks(new)
    new = fix_fonts(new)
    new = fix_stale_claims(new, course)
    new = fix_meta_description(new, slug)
    new = fix_rating_count(new, course)
    new = fix_json_ld(new, course)
    return html, new


def main():
    check = '--check' in sys.argv
    changed = 0
    for path in sorted((ROOT / 'courses').glob('*.html')):
        before, after = process(path)
        if before != after:
            changed += 1
            if not check:
                path.write_text(after, encoding='utf-8')
            print(('would change ' if check else 'updated ') + path.name)
    print('%d file(s) %s' % (changed, 'need changes' if check else 'updated'))
    return 1 if (check and changed) else 0


if __name__ == '__main__':
    sys.exit(main())
