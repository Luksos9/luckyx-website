#!/usr/bin/env python3
"""Writes the compare table rows into compare.html as static HTML.

The page script rebuilds the same rows in the browser (sorting and filtering). The static copy
is what crawlers and visitors without JavaScript see. The data array in compare.html is the
source, so this script only mirrors it.

    python3 scripts/render_compare.py          # apply
    python3 scripts/render_compare.py --check  # exit 1 if the file would change
"""
import re
import sys
from html import escape
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / 'compare.html'

CERT = re.compile(
    r"\{ name:'(.*?)', code:'(.*?)', slug:'(.*?)', track:'(.*?)', trackKey:'(.*?)', difficulty:(\d), "
    r"questions:(\d+), rating:([\d.]+), reviews:(\d+), prereq:'(.*?)', next:'(.*?)', ref:'(.*?)' \}")


def stars(rating):
    if rating > 4.5:
        full, half = 5, 0
    elif rating > 4.0:
        full, half = 4, 1
    else:
        full, half = int(rating), 0
    out = '★' * full
    if half:
        out += '<span class="cert-half">★</span>'
    return out + '☆' * (5 - full - half)


def dots(level):
    return ''.join('<span class="cert-dot%s"></span>' % (' filled' if i < level else '') for i in range(5))


def row(c):
    name, code, slug, track, _key, diff, questions, rating, _reviews, prereq, nxt, ref = c
    rating = float(rating)
    return ('<tr><td><span class="cert-code">%s</span><br><span class="cert-name">%s</span></td>'
            '<td><span class="cert-track">%s</span></td>'
            '<td><div class="cert-difficulty">%s</div></td>'
            '<td><strong>%s</strong></td>'
            '<td><div class="cert-rating"><span class="cert-rating-num">%.1f</span><span class="cert-stars">%s</span></div></td>'
            '<td><span class="cert-prereq">%s</span></td>'
            '<td><span class="cert-next">%s</span></td>'
            '<td><div class="cert-actions"><a href="/courses/%s.html" class="cert-link">Details</a>'
            '<a href="/courses/%s.html#free-quiz" class="cert-link">Free test</a>'
            '<a href="%s" target="_blank" rel="sponsored noopener" class="cert-link primary" data-track-placement="compare" aria-label="Buy %s on Udemy">Buy</a></div></td></tr>'
            % (escape(code), escape(name, quote=False), escape(track, quote=False), dots(int(diff)), questions, rating, stars(rating),
               escape(prereq, quote=False), escape(nxt, quote=False), slug, slug, escape(ref), escape(code)))


def main():
    text = PATH.read_text(encoding='utf-8')
    certs = CERT.findall(text)
    if len(certs) != 18:
        print('expected 18 certs in compare.html, found %d' % len(certs))
        return 2
    rows = '\n'.join(row(c) for c in certs)
    new = re.sub(r'<!-- lx:rows -->.*?<!-- /lx:rows -->', lambda _m: '<!-- lx:rows -->\n%s\n<!-- /lx:rows -->' % rows, text, flags=re.S)
    if new == text:
        print('compare.html is up to date')
        return 0
    if '--check' in sys.argv:
        print('compare.html static rows are out of date')
        return 1
    PATH.write_text(new, encoding='utf-8')
    print('compare.html static rows updated')
    return 0


if __name__ == '__main__':
    sys.exit(main())
