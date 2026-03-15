#!/usr/bin/env python3
"""
inject_quiz_gate.py
Injects quiz-gate.css and quiz-gate.js into all 36 course HTML files.
Safe to re-run: sentinel strings prevent double-injection.
"""

import os
import glob

COURSES_DIR = os.path.join(os.path.dirname(__file__), 'courses')
WEBSITE_DIR = os.path.dirname(__file__)

CSS_FILE = os.path.join(WEBSITE_DIR, 'quiz-gate.css')
JS_FILE  = os.path.join(WEBSITE_DIR, 'quiz-gate.js')

CSS_SENTINEL = '/* END QG */'
JS_SENTINEL  = '// END QG SYSTEM'


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def save(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def inject(html, css_block, js_block):
    """
    Injects CSS before the last </style> and JS before the last </script>.
    Returns (new_html, css_injected, js_injected).
    """
    css_done = js_done = False

    # --- CSS ---
    style_close = html.rfind('</style>')
    if style_close != -1:
        # Insert CSS block (with newline padding) immediately before </style>
        html = html[:style_close] + '\n' + css_block + '\n' + html[style_close:]
        css_done = True

    # --- JS ---
    script_close = html.rfind('</script>')
    if script_close != -1:
        html = html[:script_close] + '\n' + js_block + '\n' + html[script_close:]
        js_done = True

    return html, css_done, js_done


def main():
    css_raw = load(CSS_FILE)
    js_raw  = load(JS_FILE)

    html_files = sorted(glob.glob(os.path.join(COURSES_DIR, '*.html')))
    print(f'Found {len(html_files)} HTML files in courses/\n')

    injected = skipped = errors = 0

    for path in html_files:
        fname = os.path.basename(path)
        content = load(path)

        # Skip if already injected
        if CSS_SENTINEL in content or JS_SENTINEL in content:
            print(f'  SKIP  {fname}  (sentinel found)')
            skipped += 1
            continue

        new_content, css_ok, js_ok = inject(content, css_raw, js_raw)

        if not css_ok:
            print(f'  WARN  {fname}  — no </style> found, CSS not injected')
            errors += 1
        if not js_ok:
            print(f'  WARN  {fname}  — no </script> found, JS not injected')
            errors += 1

        if css_ok or js_ok:
            save(path, new_content)
            injected += 1
            print(f'  OK    {fname}')

    print(f'\nDone. Injected: {injected}  |  Skipped: {skipped}  |  Errors: {errors}')


if __name__ == '__main__':
    main()
