This folder stores the canonical 15-question course HTML source used by `build_preview_funnel.py`.

Why it exists:
- `courses/*.html` is generated single-page output.
- The build now creates one 3-tier funnel per course page.
- Rebuilding from generated output is fragile, so the funnel build reads from `preview_source/courses/*.html` instead.

Expected workflow:
- Update the rich 15-question source in `preview_source/courses/*.html`.
- Run `python build_preview_funnel.py`.
- Commit both the generated `courses/` pages and any source changes here.
