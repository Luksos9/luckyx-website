#!/usr/bin/env python3
"""Adds or removes &couponCode=... on every Udemy link, from the "coupon" field in data/courses.json.

Set a course's coupon to a code and the code is added to every link for that course (home page,
compare, quiz, course page, blog). Set it to null and the code is removed. Run this first, then
scripts/render_compare.py, then python3 check_site.py. Idempotent.

    python3 scripts/apply_coupons.py          # apply
    python3 scripts/apply_coupons.py --check  # exit 1 if any link is out of step with the data
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {'legacy', 'preview_source', 'scripts', 'data', '.git'}
COURSES = json.loads((ROOT / 'data' / 'courses.json').read_text(encoding='utf-8'))
URL = re.compile(r'(https://www\.udemy\.com/course/[a-z0-9-]+/\?referralCode=[A-Za-z0-9]+)((?:&amp;|&)couponCode=[A-Za-z0-9._-]+)?')
BASE_TO_COUPON = {c['udemy_url']: c['coupon'] for c in COURSES}


def rewrite(text):
    def sub(m):
        base = m.group(1)
        if base not in BASE_TO_COUPON:
            return m.group(0)
        coupon = BASE_TO_COUPON[base]
        if not coupon:
            return base
        in_attribute = text[max(0, m.start() - 6):m.start()] == 'href="'
        return '%s%scouponCode=%s' % (base, '&amp;' if in_attribute else '&', coupon)
    return URL.sub(sub, text)


def main():
    check = '--check' in sys.argv
    changed = 0
    for path in sorted(ROOT.rglob('*.html')):
        if SKIP & set(path.relative_to(ROOT).parts[:-1]):
            continue
        text = path.read_text(encoding='utf-8')
        new = rewrite(text)
        if new != text:
            changed += 1
            print(('out of step: ' if check else 'updated ') + str(path.relative_to(ROOT)))
            if not check:
                path.write_text(new, encoding='utf-8')
    print('%d file(s) %s' % (changed, 'need changes' if check else 'updated'))
    return 1 if (check and changed) else 0


if __name__ == '__main__':
    sys.exit(main())
