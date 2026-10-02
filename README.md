# luckyx.dev

Static site for Lucky X ServiceNow practice tests. GitHub Pages serves the repository as it is.

## How the pages are made

All pages are plain HTML. The files in `courses/` are edited in place, and the scripts in `scripts/`
rewrite parts of them in a repeatable way. Every script is idempotent: running it twice changes nothing.

`data/courses.json` is the single source for course facts: question count, rating, review count, Udemy
link, coupon, prerequisite, next course and matching study guide.

| Script | What it does |
| --- | --- |
| `scripts/fix_course_pages.py` | Repairs course pages: lost question marks, fonts URL, JSON-LD ratings, retake fee, titles |
| `scripts/enhance_course_pages.py` | Buy bar, FAQ with schema, next step and related courses on course pages |
| `scripts/inject_article_cta.py` | Course call to action in study guides that have no Udemy link |
| `scripts/render_compare.py` | Static table rows in `compare.html` for crawlers and visitors without JavaScript |
| `scripts/apply_coupons.py` | Adds or removes `couponCode` on every Udemy link from `data/courses.json` |
| `scripts/mark_affiliate_links.py` | `rel="sponsored"` on every Udemy referral link |
| `scripts/add_consent.py` | Consent Mode snippet and cookie notice on every page |
| `scripts/update_dates.py` | Sitemap `lastmod` and article `dateModified` from git history |

Ratings and review counts still live in `index.html` and `compare.html` as well. Change them in all
three places (`data/courses.json`, `index.html`, `compare.html`) and `check_site.py` will tell you if one is missed.

## Before every commit

    python3 check_site.py

It fails on expired free-attempt wording, lost question marks, invalid JSON-LD, ratings or question counts
that disagree between pages, broken internal links, sitemap entries without a file, guides missing from the
blog index or `llms.txt`, and generated output that is out of date. When it names a script, run that script.

Run `python3 scripts/update_dates.py` after committing content changes, then commit the result with a
message that starts with `Update dates`.

## New coupon codes

1. Put the code in the `coupon` field of each course in `data/courses.json` (or `null` to remove it).
2. `python3 scripts/apply_coupons.py && python3 scripts/render_compare.py && python3 check_site.py`

## Local preview

    node serve.js        # http://127.0.0.1:8080

## Notes

- Do not regenerate `courses/*.html` from an older source. The pages in `courses/` are the source of truth.
  Earlier generators (`generate-course-pages.js`, `build_preview_funnel.py`, `generate_quizzes.py`) were removed
  because running them would overwrite the current pages. They are in the git history.
- The email gate sits at question 6 of each course preview. Leads go to Kit form 9183962.
