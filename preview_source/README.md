This folder stores the canonical 15-question course HTML source used by `build_preview_funnel.py`.

Why it exists:
- `courses/*.html` is now generated page 1 output.
- `courses/*-preview-2.html` is generated page 2 output.
- Rebuilding from generated output is fragile, so the funnel build reads from `preview_source/courses/*.html` instead.

Expected workflow:
- Update the rich 15-question source in `preview_source/courses/*.html`.
- Run `python build_preview_funnel.py`.
- Commit both the generated `courses/` pages and any source changes here.
