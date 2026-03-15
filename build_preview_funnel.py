#!/usr/bin/env python3
"""Build the 3-tier single-page quiz funnel from the rich course source pages."""

from __future__ import annotations

import ast
import copy
import json
import re
import subprocess
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
COURSES_DIR = ROOT / "courses"
SOURCE_DIR = ROOT / "preview_source" / "courses"
SITEMAP_PATH = ROOT / "sitemap.xml"
TODAY = str(date.today())

QUESTION_COUNTS = {
    "cad": 325,
    "cas-pa": 216,
    "cis-csm": 340,
    "cis-data-foundations": 470,
    "cis-discovery": 173,
    "cis-event-management": 200,
    "cis-fsm": 264,
    "cis-grc-irm": 300,
    "cis-ham": 240,
    "cis-hrsd": 220,
    "cis-itsm": 198,
    "cis-sam": 220,
    "cis-service-mapping": 270,
    "cis-sir": 281,
    "cis-spm": 350,
    "cis-tprm": 180,
    "cis-vr": 213,
    "csa": 392,
}

REPLACEMENTS = {
    "Ă˘â‚¬â€ť": "-",
    "Ă˘â‚¬â€ś": "-",
    "Ă˘â‚¬â„˘": "'",
    "Ă˘â‚¬Ëś": "'",
    "Ă˘â‚¬Ĺ“": '"',
    "Ă˘â‚¬\x9d": '"',
    "Ă˘â‚¬Â¦": "...",
    "Ă‚ ": " ",
    "Ă‚": "",
    "Ă˘â‚¬â€ť": "â€”",
    "Ă˘â‚¬â€ś": "â€“",
    "Ă˘â‚¬â„˘": "â€™",
    "Ă˘â‚¬Ëś": "â€",
    "Ă˘â‚¬Ĺ“": "â€ś",
    "Ă˘â‚¬\x9d": "â€ť",
    "Ă˘â‚¬Â¦": "â€¦",
}

MOJIBAKE_MARKERS = ("Ă‚", "Ă", "Ă˘â‚¬", "Ă˘â‚¬â„˘", "Ă˘â‚¬Ĺ“", "Ă˘â‚¬\x9d")

QUIZ_SECTION_RE = re.compile(r'  <section class="quiz-section" id="free-quiz"[^>]*>.*?  </section>', re.S)
QUIZ_SCHEMA_RE = re.compile(r"<!-- Structured Data: Quiz -->\s*<script type=\"application/ld\+json\">.*?</script>", re.S)
QUIZ_CSS_RE = re.compile(r"/\* Quiz section \*/.*?(?=/\* Countdown banner \*/)", re.S)
POPUP_RE = re.compile(r"\n<!-- Preview Exit Popup -->.*?<!-- /Preview Exit Popup -->\n", re.S)
ANSWERS_RE = re.compile(r"\banswers\s*=\s*(\[[\s\S]*?\])(?:;|,STATE|,themeToggle)", re.S)
COURSE_SCHEMA_RE = re.compile(
    r"(<!-- Structured Data: Course -->\s*<script type=\"application/ld\+json\">\s*)(\{.*?\})(\s*</script>)",
    re.S,
)

LOCK_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/>'
    '<path d="M8 11V8a4 4 0 1 1 8 0v3"/></svg>'
)

QUIZ_CSS = """/* Quiz section */
.quiz-section{margin-top:48px}.quiz-section h2{font-size:1.38rem;font-weight:700;margin-bottom:10px;line-height:1.24}.quiz-intro{margin:0;color:var(--text-dim);font-size:.97rem;line-height:1.65;max-width:62ch}.preview-shell{margin-bottom:28px}.preview-kicker{display:inline-flex;align-items:center;gap:8px;margin-bottom:14px;padding:6px 12px;border-radius:999px;background:rgba(221,92,12,.08);border:1px solid rgba(221,92,12,.18);color:var(--orange);font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase}.preview-status-line{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 18px}.preview-status-pill{display:inline-flex;align-items:center;gap:8px;padding:9px 12px;border-radius:999px;background:rgba(255,255,255,.03);border:1px solid var(--border);color:var(--text-dim);font-size:.84rem}.preview-status-pill strong{color:var(--text)}.preview-progress-wrap{overflow-x:auto;padding-bottom:4px}.preview-progress{display:grid;grid-template-columns:repeat(15,58px);gap:8px;list-style:none;margin:0;padding:0;min-width:max-content}.preview-slot{min-height:60px;padding:9px 6px;border-radius:12px;border:1px solid var(--border);background:var(--bg-raised);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;cursor:default;transition:border-color .18s,background .18s,transform .18s}.preview-slot.is-clickable{cursor:pointer}.preview-slot.is-clickable:hover{transform:translateY(-1px);border-color:var(--border-hover)}.preview-slot.is-current{border-color:rgba(221,92,12,.42);background:rgba(221,92,12,.08)}.preview-slot.is-correct{border-color:rgba(46,160,67,.45);background:rgba(46,160,67,.08)}.preview-slot.is-wrong{border-color:rgba(215,58,73,.45);background:rgba(215,58,73,.08)}.preview-slot.is-email-locked{opacity:.78}.preview-slot.is-locked{opacity:.55}.preview-slot-num{display:block;font-size:.94rem;font-weight:700;line-height:1.1;color:var(--text)}.preview-slot-state{display:block;margin-top:4px;font-size:.63rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--text-dim)}.preview-slot.is-correct .preview-slot-num,.preview-slot.is-correct .preview-slot-state{color:#2ea043}.preview-slot.is-wrong .preview-slot-num,.preview-slot.is-wrong .preview-slot-state{color:#d73a49}.preview-slot-lock{width:16px;height:16px;margin-top:4px;color:var(--text-dim)}.preview-slot-lock svg{width:100%;height:100%;stroke:currentColor;stroke-width:1.6;fill:none}.preview-group-labels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:10px}.preview-group-label{padding:10px 12px;border-radius:12px;border:1px solid var(--border);background:rgba(255,255,255,.02);font-size:.8rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--text-dim);text-align:center}.quiz-tier-heading{margin:26px 0 14px;padding-top:4px;font-size:.85rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--orange)}.quiz-card{background:var(--bg-raised);border:1px solid var(--border);border-radius:14px;padding:20px 20px 18px;margin-bottom:14px;transition:border-color .2s,background .2s}.quiz-card[data-state="correct"]{border-color:#2ea043}.quiz-card[data-state="wrong"]{border-color:#d73a49}.quiz-card.is-email-locked,.quiz-card.is-teaser-locked{background:linear-gradient(180deg,rgba(255,255,255,.018),rgba(255,255,255,.005))}.quiz-q{font-weight:600;font-size:1rem;margin-bottom:14px;line-height:1.5}.quiz-q-num{color:var(--orange);font-weight:700;margin-right:6px}.quiz-answer-shell{position:relative}.quiz-answer-content.quiz-gate-blur{filter:blur(4px);pointer-events:none;user-select:none}.quiz-opts{list-style:none;display:flex;flex-direction:column;gap:6px}.quiz-opt{display:flex;align-items:flex-start;gap:10px;padding:11px 12px;border-radius:12px;border:1px solid var(--border);cursor:pointer;transition:background .15s,border-color .15s;color:var(--text-dim);font-size:.94rem;line-height:1.5;flex-wrap:wrap}.quiz-opt:hover{background:rgba(221,92,12,.06);border-color:var(--border-hover)}.quiz-opt.selected{background:rgba(221,92,12,.1);border-color:var(--orange);color:var(--text)}.quiz-opt.correct{background:rgba(46,160,67,.1);border-color:#2ea043;color:var(--text)}.quiz-opt.wrong{background:rgba(215,58,73,.1);border-color:#d73a49}.quiz-opt[disabled]{pointer-events:none;cursor:default}.quiz-opt-letter{width:22px;height:22px;border-radius:50%;background:var(--bg-card);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:600;flex-shrink:0;color:var(--text-dim)}.quiz-opt.selected .quiz-opt-letter{background:var(--orange);color:#fff;border-color:var(--orange)}.quiz-opt.correct .quiz-opt-letter{background:#2ea043;color:#fff;border-color:#2ea043}.quiz-opt.wrong .quiz-opt-letter{background:#d73a49;color:#fff;border-color:#d73a49}.quiz-choose{font-weight:500;color:var(--orange);font-size:.85rem;margin-left:4px}.quiz-submit-btn{display:none;margin-top:12px;padding:11px 26px;background:var(--orange);color:#fff;border:none;border-radius:10px;font-size:.92rem;font-weight:700;cursor:pointer}.quiz-submit-btn:hover{background:#c75400}.quiz-opt-exp-inline{flex-basis:100%;padding:8px 12px;border-radius:9px;font-size:.86rem;line-height:1.48;margin-top:6px}.quiz-opt-exp-inline.qoe-is-correct{background:rgba(46,160,67,.08);border-left:3px solid #2ea043}.quiz-opt-exp-inline.qoe-is-wrong{background:rgba(215,58,73,.06);border-left:3px solid #d73a49}.qoe-header{font-weight:700;margin-bottom:3px;font-size:.8rem;display:flex;align-items:center;gap:6px}.qoe-correct{color:#2ea043}.qoe-wrong{color:#d73a49}.qoe-letter,.qoe-text{color:var(--text-dim)}.quiz-opt-explains{display:none!important}.quiz-overall{display:none;margin-top:10px}.quiz-overall[style*="block"]{display:block}details.quiz-overall:not([open]) .quiz-overall-content{display:none}.quiz-overall-toggle{cursor:pointer;font-size:.88rem;font-weight:700;color:var(--orange);padding:8px 0 2px;list-style:none;display:flex;align-items:center;gap:6px}.quiz-overall-toggle::-webkit-details-marker{display:none}.quiz-overall-toggle::before{content:'';display:inline-block;width:0;height:0;border-left:5px solid var(--orange);border-top:4px solid transparent;border-bottom:4px solid transparent;transition:transform .2s}details.quiz-overall[open] .quiz-overall-toggle::before{transform:rotate(90deg)}.quiz-overall-content{padding:6px 0 0;background:transparent;border-radius:0;font-size:.88rem;color:var(--text-dim);line-height:1.65;margin-top:6px;border-left:none}.exp-section{margin-bottom:10px;padding:12px 14px;border-radius:11px;border-left:3px solid}.exp-section:last-child,.exp-section p:last-child,.exp-section ul:last-child{margin-bottom:0}.exp-section h5{margin:0 0 6px;font-size:.88rem;font-weight:700}.exp-section p{margin-bottom:5px}.exp-section ul{padding-left:18px;margin-bottom:5px}.exp-section li{margin-bottom:3px}.exp-correct-answer{background:rgba(46,160,67,.05);border-left-color:#2ea043}.exp-correct-answer h5{color:#2ea043}.exp-source{background:rgba(59,130,246,.05);border-left-color:#3b82f6}.exp-source h5,.exp-source a{color:#3b82f6}.exp-expert{background:rgba(139,92,246,.05);border-left-color:#8b5cf6}.exp-expert h5{color:#8b5cf6}.exp-wrong{background:rgba(215,58,73,.04);border-left-color:#d73a49}.exp-wrong h5{color:#d73a49}.exp-memory{background:rgba(217,119,6,.05);border-left-color:#d97706}.exp-memory h5{color:#d97706}.exp-realworld{background:rgba(16,185,129,.05);border-left-color:#10b981}.exp-realworld h5{color:#10b981}.quiz-gate-prompt,.quiz-locked-overlay{position:absolute;inset:14px;display:flex;align-items:center;justify-content:center;border-radius:14px;background:rgba(7,9,13,.56);z-index:4}.quiz-gate-card,.quiz-locked-card{width:min(100%,480px);padding:22px;border-radius:16px;border:1px solid rgba(221,92,12,.32);background:var(--bg-raised);box-shadow:0 18px 45px rgba(0,0,0,.28);text-align:center}.quiz-gate-title,.quiz-locked-title{font-size:1.08rem;font-weight:700;line-height:1.35}.quiz-gate-copy,.quiz-locked-copy{margin-top:10px;color:var(--text-dim);font-size:.92rem;line-height:1.6}.quiz-gate-form{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}.quiz-gate-email-input{flex:1 1 220px;min-height:48px;padding:0 14px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-family:var(--font);font-size:.94rem}.quiz-gate-email-input:focus{outline:none;border-color:rgba(221,92,12,.5);box-shadow:0 0 0 3px rgba(221,92,12,.12)}.quiz-gate-submit,.quiz-locked-cta-btn,.quiz-interstitial .cp-cta,.quiz-secondary-btn{display:inline-flex;align-items:center;justify-content:center;padding:13px 20px;border-radius:12px;border:none;background:var(--orange);color:#fff;font-family:var(--font);font-size:.95rem;font-weight:700;cursor:pointer;text-decoration:none}.quiz-gate-submit:hover,.quiz-locked-cta-btn:hover,.quiz-interstitial .cp-cta:hover,.quiz-secondary-btn:hover{background:#c75400;text-decoration:none}.quiz-secondary-btn{background:transparent;border:1px solid var(--border-hover);color:var(--text)}.quiz-secondary-btn:hover{background:rgba(221,92,12,.06)}.quiz-gate-note{margin-top:12px;color:var(--text-dim);font-size:.82rem;line-height:1.5}.quiz-gate-message{margin-top:10px;font-size:.85rem;color:var(--text-dim);min-height:1.3em}.quiz-gate-message.is-error{color:#ff868f}.quiz-gate-message.is-success{color:#2ea043}.quiz-locked-lock{width:26px;height:26px;margin:0 auto 8px;color:var(--orange)}.quiz-locked-lock svg{width:100%;height:100%;stroke:currentColor;stroke-width:1.7;fill:none}.quiz-interstitial{margin:24px 0;padding:24px;border-radius:18px;border:1px solid rgba(221,92,12,.2);background:radial-gradient(circle at top right,rgba(221,92,12,.1),transparent 44%),linear-gradient(180deg,rgba(255,255,255,.015),rgba(255,255,255,.004))}.quiz-interstitial[hidden]{display:none!important}.quiz-interstitial-kicker{color:var(--orange);font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase}.quiz-interstitial h3{margin-top:10px;font-size:1.32rem;line-height:1.28}.quiz-interstitial-score{font-size:2.15rem;font-weight:800;color:var(--text);line-height:1;margin-top:16px}.quiz-interstitial-copy{margin-top:8px;color:var(--text-dim);max-width:58ch}.quiz-interstitial-anchor{margin-top:12px;color:var(--text);font-size:.92rem}.quiz-interstitial-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}.quiz-cross-sell{margin-top:24px;padding:22px;border-radius:16px;border:1px solid var(--border);background:rgba(255,255,255,.02)}.quiz-cross-sell h3{font-size:1rem;margin-bottom:8px}.quiz-cross-sell p{margin:0;color:var(--text-dim);font-size:.92rem;line-height:1.6}.quiz-cross-sell-links{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}.quiz-cross-sell-links a{display:inline-flex;align-items:center;justify-content:center;padding:12px 18px;border-radius:12px;border:1px solid var(--border-hover);background:transparent;color:var(--text);font-weight:700}.quiz-cross-sell-links a:hover{background:rgba(221,92,12,.06);border-color:var(--orange);text-decoration:none}.quiz-toast{position:fixed;right:18px;bottom:18px;z-index:1002;min-width:220px;max-width:min(360px,calc(100vw - 36px));padding:14px 16px;border-radius:12px;border:1px solid rgba(46,160,67,.35);background:rgba(18,25,21,.96);color:#e8fff0;box-shadow:0 18px 45px rgba(0,0,0,.32);font-size:.9rem;opacity:0;transform:translateY(12px);pointer-events:none;transition:opacity .2s,transform .2s}.quiz-toast.show{opacity:1;transform:translateY(0)}@media (min-width:1040px){.cp-wrap{max-width:960px;padding-left:32px;padding-right:32px}.quiz-card{padding:22px 24px 20px}}@media (max-width:720px){.preview-group-labels{grid-template-columns:1fr}.quiz-gate-form{flex-direction:column}.quiz-gate-submit,.quiz-secondary-btn,.quiz-cross-sell-links a,.quiz-interstitial .cp-cta{width:100%}.quiz-gate-card,.quiz-locked-card{padding:18px}.quiz-interstitial-actions{flex-direction:column}.quiz-card{padding:16px}}
"""
COUNTDOWN_JS = """
// CIS-DF Mandate Countdown
(function(){const deadline=new Date('2027-01-01T00:00:00').getTime(),d=document.getElementById('cdDays'),h=document.getElementById('cdHrs'),m=document.getElementById('cdMin'),s=document.getElementById('cdSec');if(!d)return;const pad=n=>n<10?'0'+n:n;function tick(){const diff=deadline-Date.now();if(diff<=0){d.textContent='0';h.textContent='00';m.textContent='00';s.textContent='00';return}d.textContent=Math.floor(diff/86400000);h.textContent=pad(Math.floor(diff%86400000/3600000));m.textContent=pad(Math.floor(diff%3600000/60000));s.textContent=pad(Math.floor(diff%60000/1000))}tick();setInterval(tick,1000)})();
"""


def normalize_text(raw: str) -> str:
    for _ in range(2):
        before = raw
        for bad, good in REPLACEMENTS.items():
            raw = raw.replace(bad, good)
        if any(marker in raw for marker in MOJIBAKE_MARKERS):
            try:
                repaired = raw.encode("latin1").decode("utf-8")
            except UnicodeEncodeError:
                repaired = raw
            if repaired != raw:
                current_score = sum(raw.count(marker) for marker in MOJIBAKE_MARKERS)
                repaired_score = sum(repaired.count(marker) for marker in MOJIBAKE_MARKERS)
                if repaired_score < current_score:
                    raw = repaired
                    continue
        if raw == before:
            break
    return raw


def extract_answers(raw: str) -> list:
    match = ANSWERS_RE.search(raw)
    if not match:
        raise ValueError("Could not find answers array.")
    return ast.literal_eval(match.group(1))


def replace_last_script(raw: str, new_script: str) -> str:
    start = raw.rfind("<script>")
    if start == -1:
        raise ValueError("Could not find final script block.")
    end = raw.find("</script>", start)
    if end == -1:
        raise ValueError("Could not find end of final script block.")
    return raw[:start] + new_script + raw[end + 9 :]


def new_tag(name: str, text: str | None = None, attrs: dict | None = None):
    soup = BeautifulSoup("", "html.parser")
    tag = soup.new_tag(name)
    if attrs:
        for key, value in attrs.items():
            tag[key] = value
    if text is not None:
        tag.string = text
    return tag


def replace_question_count_phrases(text: str, total_q: int) -> str:
    updated = text
    updated = re.sub(r"\b\d+(?=-question\b)", str(total_q), updated)
    updated = re.sub(r"\b\d+(?= questions\b)", str(total_q), updated)
    updated = re.sub(r"\b\d+(?= practice questions\b)", str(total_q), updated)
    updated = re.sub(r"\b\d+(?= question bank\b)", str(total_q), updated)
    return updated


def question_text(card) -> str:
    quiz_q = copy.deepcopy(card.select_one(".quiz-q"))
    q_num = quiz_q.select_one(".quiz-q-num")
    if q_num:
        q_num.decompose()
    return " ".join(quiz_q.get_text(" ", strip=True).split())


def option_texts(card) -> list[str]:
    texts = []
    for opt in card.select(".quiz-opt"):
        spans = opt.find_all("span")
        text = spans[-1].get_text(" ", strip=True) if spans else opt.get_text(" ", strip=True)
        texts.append(" ".join(text.split()))
    return texts


def question_wrapper(card, global_idx: int):
    question = card.select_one(".quiz-q")
    if not question:
        raise ValueError(f"Question card {global_idx + 1} is missing .quiz-q.")
    shell = new_tag("div", attrs={"class": "quiz-answer-shell"})
    content = new_tag("div", attrs={"class": "quiz-answer-content"})
    move_nodes = []
    seen_question = False
    for child in list(card.children):
        if child is question:
            seen_question = True
            continue
        if seen_question:
            move_nodes.append(child)
    for child in move_nodes:
        content.append(child.extract())
    shell.append(content)
    card.append(shell)
    return shell, content


def gate_prompt_html() -> str:
    return """<div class="quiz-gate-prompt" data-email-overlay>
  <div class="quiz-gate-card">
    <div class="quiz-gate-title">Enter your email to continue with questions 6-10</div>
    <p class="quiz-gate-copy">Free exam updates. No spam. Unsubscribe anytime.</p>
    <form class="quiz-gate-form" id="quizGateForm">
      <input type="email" class="quiz-gate-email-input" id="quizGateEmail" placeholder="you@email.com" autocomplete="email" required>
      <button type="submit" class="quiz-gate-submit" id="quizGateSubmit">Continue with 5 More Questions</button>
    </form>
    <p class="quiz-gate-message" id="quizGateMessage"></p>
  </div>
</div>"""


def gate_note_html() -> str:
    return """<div class="quiz-gate-prompt" data-email-overlay>
  <div class="quiz-gate-card">
    <div class="quiz-gate-title">Questions 6-10 continue after email</div>
    <p class="quiz-gate-copy">Use the form on question 6 to keep going.</p>
  </div>
</div>"""


def locked_overlay_html(total_q: int, udemy: str) -> str:
    return f"""<div class="quiz-locked-overlay">
  <div class="quiz-locked-card">
    <div class="quiz-locked-lock">{LOCK_ICON}</div>
    <div class="quiz-locked-title">This question is part of the full {total_q}-question course.</div>
    <p class="quiz-locked-copy">Keep the teaser here, then move to Udemy for the full question bank.</p>
    <a href="{udemy}" target="_blank" rel="noopener" class="quiz-locked-cta-btn" data-buy-tier="tier3">Get all {total_q} questions on Udemy</a>
  </div>
</div>"""


def interactive_button(global_idx: int):
    return new_tag(
        "button",
        "Submit Answer",
        {"class": "quiz-submit-btn", "data-q": str(global_idx), "type": "button"},
    )


def placeholder_card(global_idx: int, total_q: int, udemy: str) -> str:
    placeholder = BeautifulSoup(
        f"""
<div class="quiz-card is-teaser-locked" id="qcard{global_idx}" data-tier="3" data-question-index="{global_idx}">
  <div class="quiz-q"><span class="quiz-q-num">{global_idx + 1}.</span>Question coming soon.</div>
  <div class="quiz-answer-shell">
    <div class="quiz-answer-content quiz-gate-blur">
      <ul class="quiz-opts">
        <li class="quiz-opt"><span class="quiz-opt-letter">A</span><span>Preview answer option</span></li>
        <li class="quiz-opt"><span class="quiz-opt-letter">B</span><span>Preview answer option</span></li>
        <li class="quiz-opt"><span class="quiz-opt-letter">C</span><span>Preview answer option</span></li>
        <li class="quiz-opt"><span class="quiz-opt-letter">D</span><span>Preview answer option</span></li>
      </ul>
    </div>
    {locked_overlay_html(total_q, udemy)}
  </div>
</div>
""",
        "html.parser",
    )
    return str(placeholder.div)


def build_card(card, global_idx: int, total_q: int, udemy: str) -> str:
    tier = 1 if global_idx < 5 else 2 if global_idx < 10 else 3
    new_card = copy.deepcopy(card)
    new_card["id"] = f"qcard{global_idx}"
    new_card["data-tier"] = str(tier)
    new_card["data-question-index"] = str(global_idx)
    new_card.attrs.pop("hidden", None)
    q_num = new_card.select_one(".quiz-q-num")
    if q_num:
        q_num.string = f"{global_idx + 1}."

    for btn in new_card.select(".quiz-submit-btn"):
        btn.decompose()

    for opt in new_card.select(".quiz-opt"):
        opt.attrs.pop("disabled", None)
        opt["class"] = [c for c in opt.get("class", []) if c not in {"selected", "correct", "wrong"}]
        if tier < 3:
            opt["data-q"] = str(global_idx)
        else:
            opt.attrs.pop("data-q", None)
            opt.attrs.pop("data-exp", None)

    overall = new_card.select_one(".quiz-overall")
    if overall:
        if tier < 3:
            overall["id"] = f"qexp{global_idx}"
            overall.attrs.pop("open", None)
            overall.attrs.pop("style", None)
        else:
            overall.decompose()

    inline = new_card.select_one(".quiz-opt-explains")
    if inline:
        if tier < 3:
            inline["id"] = f"qoptexp{global_idx}"
            inline["style"] = "display:none"
        else:
            inline.decompose()

    shell, content = question_wrapper(new_card, global_idx)
    if tier < 3:
        content_classes = list(content.get("class", []))
        if tier == 2:
            content_classes.append("quiz-gate-blur")
        content["class"] = content_classes
        opts = new_card.select_one(".quiz-opts")
        if opts:
            opts.insert_after(interactive_button(global_idx))
    else:
        content["class"] = list(content.get("class", [])) + ["quiz-gate-blur"]

    if tier == 2:
        new_card["class"] = list(new_card.get("class", [])) + ["is-email-locked"]
        overlay_html = gate_prompt_html() if global_idx == 5 else gate_note_html()
        shell.append(BeautifulSoup(overlay_html, "html.parser"))
    elif tier == 3:
        new_card["class"] = list(new_card.get("class", [])) + ["is-teaser-locked"]
        shell.append(BeautifulSoup(locked_overlay_html(total_q, udemy), "html.parser"))

    return str(new_card)


def quiz_schema(title: str, code: str, slug: str, cards: list, answers: list) -> str:
    parts = []
    for card, answer in zip(cards[:5], answers[:5]):
        opts = option_texts(card)
        if isinstance(answer, list):
            accepted = " | ".join(opts[i] for i in answer)
            wrong = [i for i in range(len(opts)) if i not in answer]
        else:
            accepted = opts[answer]
            wrong = [i for i in range(len(opts)) if i != answer]
        parts.append(
            {
                "@type": "Question",
                "name": question_text(card),
                "acceptedAnswer": {"@type": "Answer", "text": accepted},
                "suggestedAnswer": [{"@type": "Answer", "text": opts[i]} for i in wrong],
            }
        )
    body = {
        "@context": "https://schema.org",
        "@type": "Quiz",
        "name": f"5 Free {title} Practice Questions",
        "description": f"Try 5 free questions from the 15-question preview for the {title} practice test.",
        "url": f"https://luckyx.dev/courses/{slug}.html#free-quiz",
        "educationalAlignment": {
            "@type": "AlignmentObject",
            "alignmentType": "assesses",
            "targetName": f"ServiceNow {code} Certification",
        },
        "hasPart": parts,
    }
    return "<!-- Structured Data: Quiz -->\n<script type=\"application/ld+json\">\n" + json.dumps(body, indent=2) + "\n</script>"


def progress_slots() -> str:
    slots = []
    for idx in range(1, 16):
        slot_class = "preview-slot is-clickable"
        state = "Free"
        lock = ""
        if 6 <= idx <= 10:
            slot_class = "preview-slot"
            state = "Email"
        if idx >= 11:
            slot_class = "preview-slot is-locked"
            state = "Full"
            lock = f'<span class="preview-slot-lock">{LOCK_ICON}</span>'
        slots.append(
            f'        <li class="{slot_class}" data-slot="{idx - 1}"><span class="preview-slot-num">{idx}</span><span class="preview-slot-state">{state}</span>{lock}</li>'
        )
    return "\n".join(slots)


def tier_heading(text: str) -> str:
    return f'    <div class="quiz-tier-heading">{text}</div>'


def tier_one_interstitial(total_q: int, udemy: str) -> str:
    return f"""    <div class="quiz-interstitial" id="tier1Interstitial" hidden>
      <div class="quiz-interstitial-kicker">Questions 1-5 complete</div>
      <h3>You scored <span id="tier1ScoreText">0/5</span> on questions 1-5.</h3>
      <div class="quiz-interstitial-score" id="tier1ScoreValue">0/5</div>
      <p class="quiz-interstitial-copy">You have seen the free section. Continue with questions 6-10 after email, or move straight to the full course.</p>
      <div class="quiz-interstitial-actions">
        <a href="{udemy}" target="_blank" rel="noopener" class="cp-cta" data-buy-tier="tier1">Get all {total_q} questions for $9.99
          <svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
        <button type="button" class="quiz-secondary-btn" id="tier1ContinueBtn">Enter your email to continue</button>
      </div>
    </div>"""


def tier_two_interstitial(total_q: int, udemy: str) -> str:
    return f"""    <div class="quiz-interstitial" id="tier2Interstitial" hidden>
      <div class="quiz-interstitial-kicker">Free preview complete</div>
      <h3>You scored <span id="tier2ScoreText">0/10</span> on the free preview.</h3>
      <div class="quiz-interstitial-score" id="tier2ScoreValue">0/10</div>
      <p class="quiz-interstitial-copy">You have seen 10 preview questions. The full course keeps the same answer breakdown style across the full bank.</p>
      <div class="quiz-interstitial-actions">
        <a href="{udemy}" target="_blank" rel="noopener" class="cp-cta" data-buy-tier="tier2">Get all {total_q} questions for $9.99
          <svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
      </div>
    </div>"""


def final_cta(total_q: int, udemy: str) -> str:
    return f"""    <div class="quiz-interstitial" id="tier3FinalCta">
      <div class="quiz-interstitial-kicker">Full course</div>
      <h3>You've seen 10 of {total_q} questions.</h3>
      <p class="quiz-interstitial-copy">The full course covers the exam blueprint with sourced explanations.</p>
      <p class="quiz-interstitial-anchor">Your first exam attempt is free. Your second costs $350.</p>
      <div class="quiz-interstitial-actions">
        <a href="{udemy}" target="_blank" rel="noopener" class="cp-cta" data-buy-tier="final">Get all {total_q} questions on Udemy
          <svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
      </div>
    </div>"""


def cross_sell_block() -> str:
    return """    <div class="quiz-cross-sell">
      <h3>Many students also study:</h3>
      <p>Keep going with the cert recommendation quiz, or compare all 18 practice tests side by side.</p>
      <div class="quiz-cross-sell-links">
        <a href="/quiz.html">Find your next cert</a>
        <a href="/compare.html">Compare all 18 courses</a>
      </div>
    </div>"""


def quiz_section(total_q: int, udemy: str, cards_html: list[str]) -> str:
    return f"""  <section class="quiz-section" id="free-quiz" data-preview-style="three-tier">
    <div class="preview-shell">
      <div class="preview-kicker">15-question preview</div>
      <h2>15 Free Preview Questions</h2>
      <p class="quiz-intro">Answer 5 questions free. Enter your email to continue with 5 more. The full course has {total_q} questions on Udemy.</p>
      <div class="preview-status-line">
        <span class="preview-status-pill">Answered <strong id="quizStatusAnswered">0 of 10 interactive questions</strong></span>
        <span class="preview-status-pill">Score <strong id="quizStatusScore">0 correct</strong></span>
      </div>
      <div class="preview-progress-wrap">
        <ol class="preview-progress" id="quizProgress">
{progress_slots()}
        </ol>
      </div>
      <div class="preview-group-labels">
        <div class="preview-group-label">Questions 1-5. Free.</div>
        <div class="preview-group-label">Questions 6-10. Email required.</div>
        <div class="preview-group-label">Questions 11-15. Full course.</div>
      </div>
    </div>
{tier_heading("Questions 1-5. Free.")}
{chr(10).join(cards_html[:5])}
{tier_one_interstitial(total_q, udemy)}
{tier_heading("Questions 6-10. Email required.")}
{chr(10).join(cards_html[5:10])}
{tier_two_interstitial(total_q, udemy)}
{tier_heading("Questions 11-15. Full course teaser.")}
{chr(10).join(cards_html[10:15])}
{final_cta(total_q, udemy)}
{cross_sell_block()}
    <div class="quiz-toast" id="quizToast">Questions 6-10 are ready.</div>
  </section>"""


JS_TEMPLATE = """<script>
const QUIZ=__CONFIG__;
const answers=__ANSWERS__;
const STORAGE_EMAIL='luckyx-email:'+QUIZ.slug,STORAGE_ANSWERS='luckyx-answers:'+QUIZ.slug,STORAGE_SCORE='luckyx-score:'+QUIZ.slug;
const themeToggle=document.getElementById('themeToggle'),slots=Array.from(document.querySelectorAll('.preview-slot[data-slot]')),cards=Array.from(document.querySelectorAll('.quiz-card')),interactiveCards=cards.filter((card)=>parseInt(card.dataset.questionIndex,10)<10),tierTwoCards=cards.filter((card)=>card.dataset.tier==='2'),tierOneInterstitial=document.getElementById('tier1Interstitial'),tierTwoInterstitial=document.getElementById('tier2Interstitial'),tier1ContinueBtn=document.getElementById('tier1ContinueBtn'),gateForm=document.getElementById('quizGateForm'),gateEmail=document.getElementById('quizGateEmail'),gateSubmit=document.getElementById('quizGateSubmit'),gateMessage=document.getElementById('quizGateMessage'),toast=document.getElementById('quizToast');
let emailReady=false,storedAnswers={},startEventSent=false,tier1EventSent=false,tier2EventSent=false;const drafts={};
if(themeToggle){themeToggle.addEventListener('click',()=>{const current=document.documentElement.getAttribute('data-theme');const next=current==='light'?'dark':'light';document.documentElement.setAttribute('data-theme',next);localStorage.setItem('luckyx-theme',next);});}
function evt(name,extra){if(typeof gtag!=='function')return;gtag('event',name,Object.assign({cert:QUIZ.code},extra||{}));}
function showToast(message){if(!toast)return;toast.textContent=message;toast.classList.add('show');window.clearTimeout(showToast._timer);showToast._timer=window.setTimeout(()=>toast.classList.remove('show'),2600);}
function readJson(key,fallback){try{const raw=localStorage.getItem(key);return raw?JSON.parse(raw):fallback;}catch(err){return fallback;}}
function normalizeSelection(value){if(!Array.isArray(value))return[];return Array.from(new Set(value.map((item)=>parseInt(item,10)).filter((item)=>Number.isInteger(item)&&item>=0))).sort((a,b)=>a-b);}
function readAnswers(){const parsed=readJson(STORAGE_ANSWERS,{}),out={};if(!parsed||typeof parsed!=='object')return out;Object.keys(parsed).forEach((key)=>{const qi=parseInt(key,10),item=parsed[key];if(!Number.isInteger(qi)||qi<0||qi>=10||!item||typeof item!=='object')return;const selected=normalizeSelection(item.selected);if(!selected.length||typeof item.isCorrect!=='boolean')return;out[qi]={selected,isCorrect:item.isCorrect};});return out;}
function writeAnswers(){localStorage.setItem(STORAGE_ANSWERS,JSON.stringify(storedAnswers));}
function scoreSlice(start,end){let answered=0,correct=0;for(let i=start;i<=end;i+=1){if(!storedAnswers[i])continue;answered+=1;if(storedAnswers[i].isCorrect)correct+=1;}return{answered,correct};}
function saveScoreState(){const tier1=scoreSlice(0,4),tier2Only=scoreSlice(5,9),total=scoreSlice(0,9);localStorage.setItem(STORAGE_SCORE,JSON.stringify({tier1:tier1.correct,tier2:tier2Only.correct,total:total.correct}));}
function correctIndicesFor(qi){return(Array.isArray(answers[qi])?answers[qi].slice():[answers[qi]]).sort((a,b)=>a-b);}
function setMessage(text,cls){if(!gateMessage)return;gateMessage.textContent=text||'';gateMessage.classList.remove('is-error','is-success');if(cls)gateMessage.classList.add(cls);}
function processSections(container){if(!container||container.dataset.processed)return;container.dataset.processed='1';const h5s=Array.from(container.querySelectorAll('h5'));if(!h5s.length)return;const sections=[];h5s.forEach((h5)=>{const title=h5.textContent.toLowerCase();let cls='exp-section';if(title.includes('correct answer'))cls+=' exp-correct-answer';else if(title.includes('source'))cls+=' exp-source';else if(title.includes('expert'))cls+=' exp-expert';else if(title.includes('why')||title.includes('wrong'))cls+=' exp-wrong';else if(title.includes('memory'))cls+=' exp-memory';else if(title.includes('real-world')||title.includes('example'))cls+=' exp-realworld';sections.push({cls,h5});});for(let i=0;i<sections.length;i+=1){const section=sections[i],div=document.createElement('div'),next=i<sections.length-1?sections[i+1].h5:null;div.className=section.cls;section.h5.parentNode.insertBefore(div,section.h5);div.appendChild(section.h5);while(div.nextSibling&&div.nextSibling!==next)div.appendChild(div.nextSibling);}}
function showExplanations(qi){const card=document.getElementById('qcard'+qi);if(!card)return;const opts=card.querySelectorAll('.quiz-opt'),correct=correctIndicesFor(qi);opts.forEach((opt,index)=>{const per=opt.getAttribute('data-exp');if(!per||opt.querySelector('.quiz-opt-exp-inline'))return;const ok=correct.indexOf(index)!==-1,txt=per.replace(/^(CORRECT|INCORRECT):\\s*/i,''),div=document.createElement('div'),icon=ok?'\\u2713':'\\u2717';div.className='quiz-opt-exp-inline '+(ok?'qoe-is-correct':'qoe-is-wrong');div.innerHTML='<div class=\"qoe-header\">'+(ok?'<span class=\"qoe-correct\">'+icon+' Correct</span>':'<span class=\"qoe-wrong\">'+icon+' Incorrect</span>')+' <span class=\"qoe-letter\">Option '+'ABCDEFG'[index]+'</span></div><div class=\"qoe-text\">'+txt+'</div>';opt.appendChild(div);});const overall=document.getElementById('qexp'+qi);if(!overall)return;const content=overall.querySelector('.quiz-overall-content');if(!content||!content.innerHTML.trim())return;processSections(content);overall.open=false;overall.removeAttribute('open');overall.style.display='block';}
document.querySelectorAll('.quiz-overall').forEach((detail)=>{detail.addEventListener('toggle',function(){if(!this.open)return;document.querySelectorAll('.quiz-overall').forEach((other)=>{if(other!==this)other.open=false;});});});
function clearOptionState(opt){opt.classList.remove('selected','correct','wrong');opt.removeAttribute('disabled');}
function renderDraft(qi){const card=document.getElementById('qcard'+qi);if(!card)return;card.removeAttribute('data-state');const selected=drafts[qi]||[];card.querySelectorAll('.quiz-opt').forEach((opt,index)=>{clearOptionState(opt);if(selected.indexOf(index)!==-1)opt.classList.add('selected');if(emailReady||qi<5)opt.removeAttribute('disabled');else opt.setAttribute('disabled','');});const btn=card.querySelector('.quiz-submit-btn');if(btn)btn.style.display=selected.length&&(emailReady||qi<5)?'block':'none';const overall=card.querySelector('.quiz-overall');if(overall){overall.open=false;overall.removeAttribute('open');overall.style.display='';}}
function applyResponse(qi,response){const card=document.getElementById('qcard'+qi);if(!card||!response)return;const correct=correctIndicesFor(qi),opts=card.querySelectorAll('.quiz-opt');card.dataset.state=response.isCorrect?'correct':'wrong';opts.forEach((opt)=>clearOptionState(opt));if(response.isCorrect){response.selected.forEach((index)=>{if(opts[index])opts[index].classList.add('correct');});}else{response.selected.forEach((index)=>{if(!opts[index])return;if(correct.indexOf(index)===-1)opts[index].classList.add('wrong');else opts[index].classList.add('correct');});correct.forEach((index)=>{if(opts[index])opts[index].classList.add('correct');});}opts.forEach((opt)=>opt.setAttribute('disabled',''));const btn=card.querySelector('.quiz-submit-btn');if(btn)btn.style.display='none';showExplanations(qi);}
function currentSlotIndex(){for(let i=0;i<5;i+=1){if(!storedAnswers[i])return i;}if(!emailReady)return 5;for(let i=5;i<10;i+=1){if(!storedAnswers[i])return i;}return-1;}
function updateStatus(){const total=scoreSlice(0,9),answeredLabel=document.getElementById('quizStatusAnswered'),scoreLabel=document.getElementById('quizStatusScore');if(answeredLabel)answeredLabel.textContent=total.answered+' of 10 interactive questions';if(scoreLabel)scoreLabel.textContent=total.correct+' correct';}
function updateSlots(){const current=currentSlotIndex();slots.forEach((slot)=>{const idx=parseInt(slot.dataset.slot,10);slot.classList.remove('is-correct','is-wrong','is-current','is-email-locked','is-clickable');if(idx>=10)return;if(storedAnswers[idx])slot.classList.add(storedAnswers[idx].isCorrect?'is-correct':'is-wrong');else if(idx>=5&&!emailReady)slot.classList.add('is-email-locked');if(idx===current)slot.classList.add('is-current');if(idx<5||(idx<10&&emailReady))slot.classList.add('is-clickable');});}
function updateInterstitials(){const tier1=scoreSlice(0,4),total=scoreSlice(0,9),tier1Text=document.getElementById('tier1ScoreText'),tier1Value=document.getElementById('tier1ScoreValue'),tier2Text=document.getElementById('tier2ScoreText'),tier2Value=document.getElementById('tier2ScoreValue');if(tier1Text)tier1Text.textContent=tier1.correct+'/5';if(tier1Value)tier1Value.textContent=tier1.correct+'/5';if(tierTwoInterstitial&&tier2Text&&tier2Value){tier2Text.textContent=total.correct+'/10';tier2Value.textContent=total.correct+'/10';}if(tierOneInterstitial)tierOneInterstitial.hidden=tier1.answered!==5;if(tierTwoInterstitial)tierTwoInterstitial.hidden=total.answered!==10;}
function persistState(){writeAnswers();saveScoreState();}
function setTierTwoAccess(open){emailReady=!!open;tierTwoCards.forEach((card)=>{card.classList.toggle('is-email-locked',!open);const content=card.querySelector('.quiz-answer-content');if(content)content.classList.toggle('quiz-gate-blur',!open);card.querySelectorAll('[data-email-overlay]').forEach((overlay)=>{overlay.hidden=open;});const qi=parseInt(card.dataset.questionIndex,10);if(!storedAnswers[qi])renderDraft(qi);});updateSlots();}
function maybeSendCompletionEvents(qi){const tier1=scoreSlice(0,4),total=scoreSlice(0,9);if(qi===0&&!startEventSent){startEventSent=true;evt('quiz_start',{tier:1});}if(!tier1EventSent&&tier1.answered===5){tier1EventSent=true;evt('quiz_tier1_complete',{score:tier1.correct});}if(!tier2EventSent&&total.answered===10){tier2EventSent=true;evt('quiz_tier2_complete',{score_total:total.correct});}}
function render(){interactiveCards.forEach((card)=>{const qi=parseInt(card.dataset.questionIndex,10);if(storedAnswers[qi])applyResponse(qi,storedAnswers[qi]);else renderDraft(qi);});updateStatus();updateSlots();updateInterstitials();persistState();}
document.querySelectorAll('.quiz-opt[data-q]').forEach((opt)=>{opt.addEventListener('click',function(){const qi=parseInt(this.dataset.q,10);if(qi>=5&&!emailReady)return;if(storedAnswers[qi])return;const idx=parseInt(this.dataset.idx,10),multi=Array.isArray(answers[qi]),current=drafts[qi]?drafts[qi].slice():[];if(multi){const pos=current.indexOf(idx);if(pos===-1)current.push(idx);else current.splice(pos,1);}else{current.length=0;current.push(idx);}drafts[qi]=normalizeSelection(current);renderDraft(qi);});});
function submitAnswer(){const qi=parseInt(this.dataset.q,10);if(qi>=5&&!emailReady)return;if(storedAnswers[qi])return;const selected=normalizeSelection(drafts[qi]);if(!selected.length)return;const correct=correctIndicesFor(qi),isCorrect=selected.length===correct.length&&selected.every((value,index)=>value===correct[index]);storedAnswers[qi]={selected,isCorrect};delete drafts[qi];render();maybeSendCompletionEvents(qi);}
document.querySelectorAll('.quiz-submit-btn[data-q]').forEach((btn)=>btn.addEventListener('click',submitAnswer));
slots.forEach((slot)=>{slot.addEventListener('click',()=>{const idx=parseInt(slot.dataset.slot,10);if(idx>=10)return;if(idx>=5&&!emailReady){const gateCard=document.getElementById('qcard5');if(gateCard)gateCard.scrollIntoView({behavior:'smooth',block:'start'});return;}const card=document.getElementById('qcard'+idx);if(card)card.scrollIntoView({behavior:'smooth',block:'start'});});});
if(tier1ContinueBtn){tier1ContinueBtn.addEventListener('click',()=>{const gateCard=document.getElementById('qcard5');if(gateCard)gateCard.scrollIntoView({behavior:'smooth',block:'start'});if(gateEmail)window.setTimeout(()=>gateEmail.focus(),250);});}
function handleGateSubmit(event){event.preventDefault();const email=gateEmail.value.trim().toLowerCase(),valid=/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)&&email.length<=254;if(!valid){setMessage('Use a valid email address.','is-error');return;}gateSubmit.disabled=true;gateSubmit.textContent='Sending...';setMessage('');fetch('https://app.convertkit.com/forms/'+QUIZ.convertKitFormId+'/subscriptions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email_address:email,fields:{source:'quiz-gate-'+QUIZ.slug}})}).then((response)=>{if(!response.ok&&response.status!==200&&response.status!==201)throw new Error('gate failed');localStorage.setItem(STORAGE_EMAIL,'1');setTierTwoAccess(true);gateEmail.value='';gateEmail.disabled=true;gateSubmit.textContent='Questions ready';setMessage('Questions 6-10 are ready.','is-success');evt('quiz_email_submit');showToast('Questions 6-10 are ready.');}).catch(()=>{gateSubmit.disabled=false;gateSubmit.textContent='Continue with 5 More Questions';setMessage('That did not go through. Please try again.','is-error');});}
if(gateForm)gateForm.addEventListener('submit',handleGateSubmit);
document.querySelectorAll('a[data-buy-tier],a.cp-cta[href*=\"udemy.com\"]').forEach((link)=>{link.addEventListener('click',()=>{const total=scoreSlice(0,9),tier=link.dataset.buyTier||(link.closest('#tier1Interstitial')?'tier1':'hero');evt('quiz_buy_click',{tier,score:total.correct});});});
storedAnswers=readAnswers();emailReady=localStorage.getItem(STORAGE_EMAIL)==='1'||Object.keys(storedAnswers).some((key)=>parseInt(key,10)>=5);setTierTwoAccess(emailReady);render();evt('quiz_page_view');__EXTRA__
</script>"""


def page_config(slug: str, code: str, total_q: int) -> dict:
    return {"slug": slug, "code": code, "totalQuestionCount": total_q, "convertKitFormId": "9183962"}


def script_block(config: dict, answers: list, countdown: bool) -> str:
    return JS_TEMPLATE.replace("__CONFIG__", json.dumps(config)).replace("__ANSWERS__", json.dumps(answers)).replace("__EXTRA__", COUNTDOWN_JS if countdown else "")


def patch_course_copy(output: str, total_q: int) -> str:
    meta_patterns = [
        r'(<meta name="description" content=")([^"]+)(">)',
        r'(<meta property="og:description" content=")([^"]+)(">)',
        r'(<meta name="twitter:description" content=")([^"]+)(">)',
    ]
    for pattern in meta_patterns:
        output = re.sub(pattern, lambda m: m.group(1) + replace_question_count_phrases(m.group(2), total_q) + m.group(3), output, count=1)
    output = re.sub(r"(<p class=\"cp-desc\">)(.*?)(</p>)", lambda m: m.group(1) + replace_question_count_phrases(" ".join(m.group(2).split()), total_q) + m.group(3), output, count=1, flags=re.S)
    output = re.sub(r"(<div class=\"cp-stat\">\s*<svg[\s\S]*?</svg>\s*)(\d+)( questions)", lambda m: m.group(1) + str(total_q) + m.group(3), output, count=1)
    output = re.sub(r"(<ul class=\"cp-feature-list\">\s*<li>\s*<svg[\s\S]*?</svg>\s*)([\s\S]*?)(\s*</li>)", lambda m: m.group(1) + replace_question_count_phrases(" ".join(m.group(2).split()), total_q) + m.group(3), output, count=1)
    match = COURSE_SCHEMA_RE.search(output)
    if match:
        body = json.loads(match.group(2))
        if body.get("@type") == "Course":
            body["description"] = replace_question_count_phrases(body.get("description", ""), total_q)
            body["numberOfCredits"] = str(total_q)
            replacement = match.group(1) + json.dumps(body, indent=2) + match.group(3)
            output = output[: match.start()] + replacement + output[match.end() :]
    return output


def course_meta(raw: str, slug: str) -> tuple[str, str, str, int]:
    soup = BeautifulSoup(raw, "html.parser")
    title = soup.select_one(".cp-title").get_text(" ", strip=True)
    code = soup.select_one(".cp-code").get_text(" ", strip=True)
    udemy = soup.select_one("a.cp-cta")["href"]
    if slug not in QUESTION_COUNTS:
        raise ValueError(f"Missing question count for {slug}.")
    return title, code, udemy, QUESTION_COUNTS[slug]


def ensure_source_snapshot(files: list[Path]) -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    for path in files:
        source_path = SOURCE_DIR / path.name
        if source_path.exists():
            continue
        try:
            raw = subprocess.check_output(["git", "show", f"HEAD:{path.relative_to(ROOT).as_posix()}"], cwd=ROOT, text=True, encoding="utf-8")
        except subprocess.CalledProcessError as exc:
            raise ValueError(f"Could not bootstrap source snapshot for {path.name}.") from exc
        if raw.count('class="quiz-card') < 10:
            raise ValueError(f"Source snapshot bootstrap for {path.name} did not contain enough quiz cards.")
        source_path.write_text(normalize_text(raw), encoding="utf-8", newline="\n")


def source_data(main_path: Path):
    source_path = SOURCE_DIR / main_path.name
    if not source_path.exists():
        raise ValueError(f"Missing source snapshot for {main_path.name}: {source_path}")
    raw = normalize_text(source_path.read_text(encoding="utf-8"))
    soup = BeautifulSoup(raw, "html.parser")
    cards = soup.select("#free-quiz .quiz-card")
    answers = extract_answers(raw)
    if len(cards) < 10 or len(answers) < 10:
        raise ValueError(f"{source_path.name}: expected at least 10 interactive source questions.")
    return raw, list(cards[:15]), list(answers[:10]), 'id="cdDays"' in raw


def render_page(raw: str, slug: str, title: str, code: str, udemy: str, total_q: int, cards: list, answers: list, countdown: bool) -> str:
    rendered_cards = [build_card(cards[idx], idx, total_q, udemy) if idx < len(cards) else placeholder_card(idx, total_q, udemy) for idx in range(15)]
    output = normalize_text(raw)
    output = QUIZ_CSS_RE.sub(QUIZ_CSS + "\n", output, count=1)
    output = QUIZ_SECTION_RE.sub(lambda _: quiz_section(total_q, udemy, rendered_cards), output, count=1)
    output = QUIZ_SCHEMA_RE.sub(lambda _: quiz_schema(title, code, slug, cards, answers), output, count=1)
    output = POPUP_RE.sub("\n", output)
    output = re.sub(r'<meta name="robots" content="[^"]+">', '<meta name="robots" content="index, follow">', output, count=1)
    output = patch_course_copy(output, total_q)
    return replace_last_script(output, script_block(page_config(slug, code, total_q), answers, countdown))


def cleanup_preview_pages() -> None:
    for path in COURSES_DIR.glob("*-preview-2.html"):
        path.unlink()


def update_sitemap() -> None:
    raw = SITEMAP_PATH.read_text(encoding="utf-8")
    raw = re.sub(r"\s*<url>\s*<loc>https://luckyx\.dev/courses/[^<]+-preview-2\.html</loc>.*?</url>", "", raw, flags=re.S)
    for slug in QUESTION_COUNTS:
        pattern = rf"(<loc>https://luckyx\\.dev/courses/{re.escape(slug)}\\.html</loc>\\s*<lastmod>)([^<]+)(</lastmod>)"
        raw = re.sub(pattern, rf"\g<1>{TODAY}\3", raw)
    raw = re.sub(r"(<loc>https://luckyx\.dev/quiz\.html</loc>\s*<lastmod>)([^<]+)(</lastmod>)", rf"\g<1>{TODAY}\3", raw)
    raw = re.sub(r"(<loc>https://luckyx\.dev/compare\.html</loc>\s*<lastmod>)([^<]+)(</lastmod>)", rf"\g<1>{TODAY}\3", raw)
    raw = re.sub(r"(<loc>https://luckyx\.dev/</loc>\s*<lastmod>)([^<]+)(</lastmod>)", rf"\g<1>{TODAY}\3", raw)
    SITEMAP_PATH.write_text(raw, encoding="utf-8", newline="\n")


def validate(path: Path, slug: str) -> None:
    raw = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")
    cards = soup.select("#free-quiz .quiz-card")
    if len(cards) != 15:
        raise ValueError(f"{path.name}: expected 15 quiz cards.")
    tiers = [card.get("data-tier") for card in cards]
    if tiers[:5] != ["1"] * 5 or tiers[5:10] != ["2"] * 5 or tiers[10:] != ["3"] * 5:
        raise ValueError(f"{path.name}: unexpected tier distribution {tiers}.")
    if len(extract_answers(raw)) != 10:
        raise ValueError(f"{path.name}: expected 10 interactive answers in script.")
    if raw.count('class="preview-slot') < 15:
        raise ValueError(f"{path.name}: progress slots are missing.")
    if 'id="quizGateForm"' not in raw or 'id="tier1Interstitial"' not in raw or 'id="tier2Interstitial"' not in raw:
        raise ValueError(f"{path.name}: gate or interstitial markup is missing.")
    if 'data-preview-style="three-tier"' not in raw:
        raise ValueError(f"{path.name}: three-tier marker is missing.")
    if "15 Free Preview Questions" not in raw:
        raise ValueError(f"{path.name}: new preview heading missing.")
    if re.search(rf"\b{QUESTION_COUNTS[slug]}\b questions", raw) is None:
        raise ValueError(f"{path.name}: expected question count {QUESTION_COUNTS[slug]} not found.")
    if any(marker in raw for marker in MOJIBAKE_MARKERS):
        raise ValueError(f"{path.name}: mojibake remains in output.")


def main() -> None:
    files = sorted(path for path in COURSES_DIR.glob("*.html") if not path.name.endswith("-preview-2.html"))
    if not files:
        raise SystemExit("No course pages found.")
    ensure_source_snapshot(files)
    for path in files:
        raw, cards, answers, countdown = source_data(path)
        title, code, udemy, total_q = course_meta(raw, path.stem)
        page = render_page(raw, path.stem, title, code, udemy, total_q, cards, answers, countdown)
        path.write_text(page, encoding="utf-8", newline="\n")
        validate(path, path.stem)
        print(f"Built 3-tier funnel: {path.name}")
    cleanup_preview_pages()
    update_sitemap()


if __name__ == "__main__":
    main()
