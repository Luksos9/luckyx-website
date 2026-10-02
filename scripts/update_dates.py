#!/usr/bin/env python3
"""Sets sitemap <lastmod> and each article's dateModified from git history.

A page's date is the date of the last commit that changed it, ignoring housekeeping commits that
touch every page without changing its content. Run it after committing content changes.

    python3 scripts/update_dates.py          # apply
    python3 scripts/update_dates.py --check  # exit 1 if any date is out of step with git
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_SUBJECTS = ('Update dates', 'Consent:', 'Untrack')


def last_change(rel):
    out = subprocess.run(['git', 'log', '--format=%cs%x09%s', '--', rel], cwd=ROOT, capture_output=True, text=True).stdout
    rows = [line.split('\t', 1) for line in out.splitlines() if line]
    for date, subject in rows:
        if not subject.startswith(SKIP_SUBJECTS):
            return date
    return rows[0][0] if rows else None


def url_to_file(url_path):
    if url_path in ('', '/'):
        return 'index.html'
    if url_path.endswith('/'):
        return url_path.lstrip('/') + 'index.html'
    return url_path.lstrip('/')


def main():
    check = '--check' in sys.argv
    stale = []

    sitemap = ROOT / 'sitemap.xml'
    text = sitemap.read_text(encoding='utf-8')

    def fix_entry(m):
        loc, old = m.group(1), m.group(2)
        rel = url_to_file(loc.replace('https://luckyx.dev', ''))
        date = last_change(rel) if (ROOT / rel).exists() else None
        if date and date != old:
            stale.append('sitemap %s %s -> %s' % (rel, old, date))
            return m.group(0).replace('<lastmod>%s</lastmod>' % old, '<lastmod>%s</lastmod>' % date)
        return m.group(0)

    new = re.sub(r'<loc>(https://luckyx\.dev[^<]*)</loc>\s*<lastmod>([^<]*)</lastmod>', fix_entry, text)
    if new != text and not check:
        sitemap.write_text(new, encoding='utf-8')

    for path in sorted((ROOT / 'blog').glob('*.html')):
        if path.name == 'index.html':
            continue
        body = path.read_text(encoding='utf-8')
        m = re.search(r'"dateModified": "([\d-]+)"', body)
        published = re.search(r'"datePublished": "([\d-]+)"', body)
        if not m:
            continue
        date = last_change('blog/' + path.name)
        if published and date < published.group(1):
            date = published.group(1)
        if date and date != m.group(1):
            stale.append('%s dateModified %s -> %s' % (path.name, m.group(1), date))
            if not check:
                path.write_text(body.replace('"dateModified": "%s"' % m.group(1), '"dateModified": "%s"' % date, 1), encoding='utf-8')

    for line in stale:
        print(('out of date: ' if check else 'updated ') + line)
    print('%d date(s) %s' % (len(stale), 'out of date' if check else 'updated'))
    return 1 if (check and stale) else 0


if __name__ == '__main__':
    sys.exit(main())
