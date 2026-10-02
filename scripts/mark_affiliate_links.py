#!/usr/bin/env python3
"""Adds rel="sponsored" to every Udemy link that carries a referralCode.

Search engines expect affiliate links to be marked. Idempotent.

    python3 scripts/mark_affiliate_links.py          # apply
    python3 scripts/mark_affiliate_links.py --check  # exit 1 if any link is unmarked
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {'legacy', 'preview_source', 'scripts', 'data', '.git'}
TAG = re.compile(r'<a\b[^<>]*\bhref="https://www\.udemy\.com/course/[^"]*referralCode=[^"]*"[^<>]*>')


def mark(tag):
    m = re.search(r'\brel="([^"]*)"', tag)
    if m:
        values = m.group(1).split()
        if 'sponsored' in values:
            return tag
        return tag[:m.start()] + 'rel="%s"' % ' '.join(['sponsored'] + values) + tag[m.end():]
    return tag[:-1] + ' rel="sponsored noopener">'


def main():
    check = '--check' in sys.argv
    bad = 0
    for path in sorted(ROOT.rglob('*.html')):
        if SKIP & set(path.relative_to(ROOT).parts[:-1]):
            continue
        text = path.read_text(encoding='utf-8')
        new = TAG.sub(lambda m: mark(m.group(0)), text)
        if new != text:
            bad += 1
            print(('unmarked links in ' if check else 'updated ') + str(path.relative_to(ROOT)))
            if not check:
                path.write_text(new, encoding='utf-8')
    print('%d file(s) %s' % (bad, 'need changes' if check else 'updated'))
    return 1 if (check and bad) else 0


if __name__ == '__main__':
    sys.exit(main())
