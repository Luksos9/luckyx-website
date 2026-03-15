#!/usr/bin/env python3
"""
inject_crosssell.py
Replaces the generic .cp-bottom "Browse all" with a targeted cross-sell link
to the recommended next cert, on all 18 page-1 course HTML files.
Safe to re-run: sentinel comment prevents double-injection.
"""

import os
import re
import glob

COURSES_DIR = os.path.join(os.path.dirname(__file__), 'courses')
SENTINEL    = '<!-- END CROSSSELL -->'

# Recommended next cert for each course slug.
# Based on the common ServiceNow cert progression path.
NEXT_COURSE = {
    'csa':                  ('cis-data-foundations',  'CIS-Data Foundations / CSDM'),
    'cis-data-foundations': ('cis-itsm',              'CIS-IT Service Management'),
    'cis-itsm':             ('cis-discovery',         'CIS-Discovery / RISCO'),
    'cis-discovery':        ('cis-service-mapping',   'CIS-Service Mapping'),
    'cis-service-mapping':  ('cis-event-management',  'CIS-Event Management'),
    'cis-event-management': ('cis-sir',               'CIS-Security Incident Response'),
    'cis-sir':              ('cis-vr',                'CIS-Vulnerability Response'),
    'cis-vr':               ('cis-grc-irm',           'CIS-GRC / IRM'),
    'cis-grc-irm':          ('cis-tprm',              'CIS-Third-Party Risk Mgmt'),
    'cis-tprm':             ('cis-ham',               'CIS-Hardware Asset Mgmt'),
    'cis-ham':              ('cis-sam',               'CIS-Software Asset Mgmt'),
    'cis-sam':              ('cis-csm',               'CIS-Customer Service Mgmt'),
    'cis-csm':              ('cis-fsm',               'CIS-Field Service Mgmt'),
    'cis-fsm':              ('cis-spm',               'CIS-Strategic Portfolio Mgmt'),
    'cis-spm':              ('cis-hrsd',              'CIS-HR Service Delivery'),
    'cis-hrsd':             ('cad',                   'Certified Application Developer'),
    'cad':                  ('cas-pa',                'CAS-Performance Analytics'),
    'cas-pa':               None,   # last in chain — falls back to generic browse link
}

# CSS to inject (into the existing style block)
CROSSSELL_CSS = """.cp-next-label { font-size: 0.78rem; color: var(--text-faint); text-transform: uppercase; letter-spacing: .06em; margin-bottom: 12px; }
.cp-next-link { display: inline-flex; align-items: center; gap: 8px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 12px 18px; color: var(--text); font-weight: 600; font-size: 0.9rem; text-decoration: none; transition: border-color .18s, background .18s; margin-bottom: 14px; }
.cp-next-link:hover { border-color: var(--orange); background: rgba(221,92,12,.06); }
.cp-next-arrow { color: var(--orange); font-size: 1rem; }
.cp-next-browse { font-size: 0.82rem; color: var(--text-faint); margin-top: 4px; }
.cp-next-browse a { color: var(--text-dim); }
/* END CROSSSELL */"""


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def save(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def get_slug(content):
    """Extract slug from const PREVIEW = {...}."""
    m = re.search(r'"slug"\s*:\s*"([^"]+)"', content)
    return m.group(1) if m else None


def make_crosssell_html(slug):
    """Return replacement .cp-bottom HTML block."""
    entry = NEXT_COURSE.get(slug)

    if entry:
        next_slug, next_name = entry
        next_block = (
            '<a class="cp-next-link" href="/courses/{slug}.html">'
            '{name}'
            '<span class="cp-next-arrow">&rarr;</span>'
            '</a>\n'
            '  <p class="cp-next-browse">or <a href="/#courses">browse all 18 practice tests</a></p>'
        ).format(slug=next_slug, name=next_name)
    else:
        # Last course in chain or unknown — show generic browse link only
        next_block = '<a href="/#courses">Browse all 18 practice tests &rarr;</a>'

    return (
        '<div class="cp-bottom">\n'
        '  <p class="cp-next-label">Many students also study:</p>\n'
        '  {next_block}\n'
        '</div>\n'
        '<!-- END CROSSSELL -->'
    ).format(next_block=next_block)


def main():
    # Only page-1 files (no "-preview-2" in filename)
    all_html = sorted(glob.glob(os.path.join(COURSES_DIR, '*.html')))
    page1 = [f for f in all_html if '-preview-2' not in os.path.basename(f)]
    print('Found %d page-1 HTML files\n' % len(page1))

    injected = skipped = errors = 0

    for path in page1:
        fname = os.path.basename(path)
        content = load(path)

        if SENTINEL in content:
            print('  SKIP  %s  (sentinel found)' % fname)
            skipped += 1
            continue

        slug = get_slug(content)
        if not slug:
            print('  WARN  %s  — could not extract slug' % fname)
            errors += 1
            continue

        # 1. Inject CSS before </style>
        css_marker = '</style>'
        style_pos = content.rfind(css_marker)
        if style_pos == -1:
            print('  WARN  %s  — no </style> found' % fname)
            errors += 1
            continue
        content = content[:style_pos] + CROSSSELL_CSS + '\n' + content[style_pos:]

        # 2. Replace .cp-bottom block
        # Match <div class="cp-bottom"> ... </div> (greedy but stopping at </div>)
        old_block_pat = r'<div class="cp-bottom">.*?</div>'
        new_block = make_crosssell_html(slug)
        new_content, count = re.subn(old_block_pat, new_block, content, flags=re.DOTALL)

        if count == 0:
            print('  WARN  %s  — .cp-bottom not found (slug=%s)' % (fname, slug))
            errors += 1
            continue

        save(path, new_content)
        injected += 1
        next_info = NEXT_COURSE.get(slug)
        print('  OK    %s  -> %s' % (fname, next_info[0] if next_info else '(browse)'))

    print('\nDone. Injected: %d  |  Skipped: %d  |  Errors: %d' % (injected, skipped, errors))


if __name__ == '__main__':
    main()
