#!/usr/bin/env python3
"""Puts the default-denied consent snippet before the GA tag and loads consent.js on every page.

Google Analytics stays off until the visitor accepts the notice. Idempotent.

    python3 scripts/add_consent.py          # apply
    python3 scripts/add_consent.py --check  # exit 1 if any page is missing it
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {'legacy', 'preview_source', 'scripts', 'data', '.git'}
GA = '<script async src="https://www.googletagmanager.com/gtag/js?id=G-BLYHHC76GG"></script>'
MARK = '<!-- lx:consent -->'
SNIPPET = """<!-- lx:consent -->
<script>
  /* Consent Mode v2: analytics stays off until the visitor accepts the notice (consent.js). */
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', wait_for_update: 500 });
  try { if (localStorage.getItem('luckyx-consent') === 'granted') gtag('consent', 'update', { analytics_storage: 'granted' }); } catch (e) {}
</script>
<script defer src="/consent.js"></script>
<!-- /lx:consent -->
"""


def pages():
    for path in sorted(ROOT.rglob('*.html')):
        if SKIP & set(path.relative_to(ROOT).parts[:-1]):
            continue
        yield path


def main():
    check = '--check' in sys.argv
    pending = 0
    for path in pages():
        text = path.read_text(encoding='utf-8')
        if GA not in text:
            continue
        if MARK in text:
            continue
        pending += 1
        print(('missing consent snippet: ' if check else 'updated ') + str(path.relative_to(ROOT)))
        if not check:
            path.write_text(text.replace(GA, SNIPPET + GA, 1), encoding='utf-8')
    print('%d file(s) %s' % (pending, 'need changes' if check else 'updated'))
    return 1 if (check and pending) else 0


if __name__ == '__main__':
    sys.exit(main())
