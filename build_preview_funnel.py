#!/usr/bin/env python3
"""Build the guided 15-question quiz funnel from the rich course source pages."""

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
.quiz-section{margin-top:48px}
.quiz-section h2{font-size:1.38rem;font-weight:700;margin-bottom:10px;line-height:1.24}
.quiz-intro{margin:0;color:var(--text-dim);font-size:.97rem;line-height:1.65;max-width:62ch}
.preview-shell{margin-bottom:22px}
.preview-kicker{display:inline-flex;align-items:center;gap:8px;margin-bottom:14px;padding:6px 12px;border-radius:999px;background:rgba(221,92,12,.08);border:1px solid rgba(221,92,12,.18);color:var(--orange);font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.quiz-stepper-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin:18px 0 12px}
.quiz-stepper-label{font-size:1rem;font-weight:700;color:var(--text)}
.quiz-stepper-tier{display:inline-flex;align-items:center;margin-top:7px;padding:6px 10px;border-radius:999px;border:1px solid var(--border);background:rgba(255,255,255,.02);font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--text-dim)}
.quiz-stepper-tier[data-state="free"]{color:#2ea043;border-color:rgba(46,160,67,.28);background:rgba(46,160,67,.08)}
.quiz-stepper-tier[data-state="locked"]{color:var(--orange);border-color:rgba(221,92,12,.28);background:rgba(221,92,12,.08)}
.quiz-stepper-tier[data-state="open"]{color:#3b82f6;border-color:rgba(59,130,246,.28);background:rgba(59,130,246,.08)}
.quiz-stepper-score{font-size:.9rem;color:var(--text-dim);white-space:nowrap;padding-top:2px}
.quiz-stepper-dots{display:grid;grid-template-columns:repeat(15,minmax(0,1fr));gap:8px}
.preview-dot{height:10px;border-radius:999px;border:1px solid var(--border);background:var(--bg-card);opacity:.55;transition:border-color .18s,background .18s,box-shadow .18s,opacity .18s}
.preview-dot.is-available{opacity:1}
.preview-dot.is-locked{opacity:.38}
.preview-dot.is-correct{background:#2ea043;border-color:#2ea043;opacity:1}
.preview-dot.is-wrong{background:#d73a49;border-color:#d73a49;opacity:1}
.preview-dot.is-current{border-color:var(--orange);box-shadow:0 0 0 3px rgba(221,92,12,.14)}
.quiz-card-stack{position:relative}
.quiz-card{background:var(--bg-raised);border:1px solid var(--border);border-radius:16px;padding:20px 20px 18px;margin-bottom:14px;transition:border-color .2s,background .2s}
.quiz-card[hidden]{display:none!important}
.quiz-card[data-state="correct"]{border-color:#2ea043}
.quiz-card[data-state="wrong"]{border-color:#d73a49}
.quiz-card.is-email-locked{background:linear-gradient(180deg,rgba(255,255,255,.018),rgba(255,255,255,.005))}
.quiz-q{font-weight:600;font-size:1rem;margin-bottom:14px;line-height:1.5}
.quiz-q-num{color:var(--orange);font-weight:700;margin-right:6px}
.quiz-answer-shell{position:relative}
.quiz-answer-content.quiz-gate-blur{filter:blur(4px);pointer-events:none;user-select:none}
.quiz-opts{list-style:none;display:flex;flex-direction:column;gap:6px}
.quiz-opt{display:flex;align-items:flex-start;gap:10px;padding:11px 12px;border-radius:12px;border:1px solid var(--border);cursor:pointer;transition:background .15s,border-color .15s;color:var(--text-dim);font-size:.94rem;line-height:1.5;flex-wrap:wrap}
.quiz-opt:hover{background:rgba(221,92,12,.06);border-color:var(--border-hover)}
.quiz-opt.selected{background:rgba(221,92,12,.1);border-color:var(--orange);color:var(--text)}
.quiz-opt.correct{background:rgba(46,160,67,.1);border-color:#2ea043;color:var(--text)}
.quiz-opt.wrong{background:rgba(215,58,73,.1);border-color:#d73a49}
.quiz-opt[disabled]{pointer-events:none;cursor:default}
.quiz-opt-letter{width:22px;height:22px;border-radius:50%;background:var(--bg-card);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:600;flex-shrink:0;color:var(--text-dim)}
.quiz-opt.selected .quiz-opt-letter{background:var(--orange);color:#fff;border-color:var(--orange)}
.quiz-opt.correct .quiz-opt-letter{background:#2ea043;color:#fff;border-color:#2ea043}
.quiz-opt.wrong .quiz-opt-letter{background:#d73a49;color:#fff;border-color:#d73a49}
.quiz-choose{font-weight:500;color:var(--orange);font-size:.85rem;margin-left:4px}
.quiz-submit-btn{display:none;margin-top:12px;padding:11px 26px;background:var(--orange);color:#fff;border:none;border-radius:10px;font-size:.92rem;font-weight:700;cursor:pointer}
.quiz-submit-btn:hover{background:#c75400}
.quiz-opt-exp-inline{flex-basis:100%;padding:8px 12px;border-radius:9px;font-size:.86rem;line-height:1.48;margin-top:6px}
.quiz-opt-exp-inline.qoe-is-correct{background:rgba(46,160,67,.08);border-left:3px solid #2ea043}
.quiz-opt-exp-inline.qoe-is-wrong{background:rgba(215,58,73,.06);border-left:3px solid #d73a49}
.qoe-header{font-weight:700;margin-bottom:3px;font-size:.8rem;display:flex;align-items:center;gap:6px}
.qoe-correct{color:#2ea043}
.qoe-wrong{color:#d73a49}
.qoe-letter,.qoe-text{color:var(--text-dim)}
.quiz-opt-explains{display:none!important}
.quiz-overall{display:none;margin-top:10px}
.quiz-overall[style*="block"]{display:block}
details.quiz-overall:not([open]) .quiz-overall-content{display:none}
.quiz-overall-toggle{cursor:pointer;font-size:.88rem;font-weight:700;color:var(--orange);padding:8px 0 2px;list-style:none;display:flex;align-items:center;gap:6px}
.quiz-overall-toggle::-webkit-details-marker{display:none}
.quiz-overall-toggle::before{content:'';display:inline-block;width:0;height:0;border-left:5px solid var(--orange);border-top:4px solid transparent;border-bottom:4px solid transparent;transition:transform .2s}
details.quiz-overall[open] .quiz-overall-toggle::before{transform:rotate(90deg)}
.quiz-overall-content{padding:6px 0 0;background:transparent;border-radius:0;font-size:.88rem;color:var(--text-dim);line-height:1.65;margin-top:6px;border-left:none}
.exp-section{margin-bottom:10px;padding:12px 14px;border-radius:11px;border-left:3px solid}
.exp-section:last-child,.exp-section p:last-child,.exp-section ul:last-child{margin-bottom:0}
.exp-section h5{margin:0 0 6px;font-size:.88rem;font-weight:700}
.exp-section p{margin-bottom:5px}
.exp-section ul{padding-left:18px;margin-bottom:5px}
.exp-section li{margin-bottom:3px}
.exp-correct-answer{background:rgba(46,160,67,.05);border-left-color:#2ea043}
.exp-correct-answer h5{color:#2ea043}
.exp-source{background:rgba(59,130,246,.05);border-left-color:#3b82f6}
.exp-source h5,.exp-source a{color:#3b82f6}
.exp-expert{background:rgba(139,92,246,.05);border-left-color:#8b5cf6}
.exp-expert h5{color:#8b5cf6}
.exp-wrong{background:rgba(215,58,73,.04);border-left-color:#d73a49}
.exp-wrong h5{color:#d73a49}
.exp-memory{background:rgba(217,119,6,.05);border-left-color:#d97706}
.exp-memory h5{color:#d97706}
.exp-realworld{background:rgba(16,185,129,.05);border-left-color:#10b981}
.exp-realworld h5{color:#10b981}
.quiz-gate-prompt{position:absolute;inset:14px;display:flex;align-items:center;justify-content:center;border-radius:14px;background:rgba(7,9,13,.56);z-index:4}
.quiz-gate-card{width:min(100%,520px);padding:22px;border-radius:16px;border:1px solid rgba(221,92,12,.32);background:var(--bg-raised);box-shadow:0 18px 45px rgba(0,0,0,.28);text-align:center}
.quiz-gate-title{font-size:1.08rem;font-weight:700;line-height:1.35}
.quiz-gate-copy{margin-top:10px;color:var(--text-dim);font-size:.92rem;line-height:1.6}
.quiz-gate-form{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.quiz-gate-email-input{flex:1 1 220px;min-height:48px;padding:0 14px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-family:var(--font);font-size:.94rem}
.quiz-gate-email-input:focus{outline:none;border-color:rgba(221,92,12,.5);box-shadow:0 0 0 3px rgba(221,92,12,.12)}
.quiz-gate-submit,.quiz-nav-next,.quiz-final .cp-cta,.quiz-secondary-btn{display:inline-flex;align-items:center;justify-content:center;padding:13px 20px;border-radius:12px;border:none;font-family:var(--font);font-size:.95rem;font-weight:700;cursor:pointer;text-decoration:none}
.quiz-nav-next,.quiz-gate-submit,.quiz-final .cp-cta{background:var(--orange);color:#fff}
.quiz-nav-next:hover,.quiz-gate-submit:hover,.quiz-final .cp-cta:hover{background:#c75400;text-decoration:none}
.quiz-nav-next[disabled],.quiz-gate-submit[disabled],.quiz-secondary-btn[disabled]{cursor:not-allowed;opacity:.45}
.quiz-secondary-btn{background:transparent;border:1px solid var(--border-hover);color:var(--text)}
.quiz-secondary-btn:hover{background:rgba(221,92,12,.06)}
.quiz-gate-message{margin-top:10px;font-size:.85rem;color:var(--text-dim);min-height:1.3em}
.quiz-gate-message.is-error{color:#ff868f}
.quiz-gate-message.is-success{color:#2ea043}
.quiz-nav{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:18px;padding:16px 18px;border-radius:16px;border:1px solid var(--border);background:rgba(255,255,255,.02)}
.quiz-nav-meta{flex:1;color:var(--text-dim);font-size:.9rem;line-height:1.5;text-align:center}
.quiz-final{margin-top:22px;padding:24px;border-radius:18px;border:1px solid rgba(221,92,12,.2);background:radial-gradient(circle at top right,rgba(221,92,12,.1),transparent 44%),linear-gradient(180deg,rgba(255,255,255,.015),rgba(255,255,255,.004))}
.quiz-final[hidden],.quiz-cross-sell[hidden]{display:none!important}
.quiz-final-kicker{color:var(--orange);font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.quiz-final h3{margin-top:10px;font-size:1.32rem;line-height:1.28}
.quiz-final-score{font-size:2.15rem;font-weight:800;color:var(--text);line-height:1;margin-top:16px}
.quiz-final-copy{margin-top:8px;color:var(--text-dim);max-width:58ch}
.quiz-final-anchor{margin-top:12px;color:var(--text);font-size:.92rem}
.quiz-final-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.quiz-cross-sell{margin-top:22px;padding:22px;border-radius:16px;border:1px solid var(--border);background:rgba(255,255,255,.02)}
.quiz-cross-sell h3{font-size:1rem;margin-bottom:8px}
.quiz-cross-sell p{margin:0;color:var(--text-dim);font-size:.92rem;line-height:1.6}
.quiz-cross-sell-links{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}
.quiz-cross-sell-links a{display:inline-flex;align-items:center;justify-content:center;padding:12px 18px;border-radius:12px;border:1px solid var(--border-hover);background:transparent;color:var(--text);font-weight:700}
.quiz-cross-sell-links a:hover{background:rgba(221,92,12,.06);border-color:var(--orange);text-decoration:none}
.quiz-toast{position:fixed;right:18px;bottom:18px;z-index:1002;min-width:220px;max-width:min(360px,calc(100vw - 36px));padding:14px 16px;border-radius:12px;border:1px solid rgba(46,160,67,.35);background:rgba(18,25,21,.96);color:#e8fff0;box-shadow:0 18px 45px rgba(0,0,0,.32);font-size:.9rem;opacity:0;transform:translateY(12px);pointer-events:none;transition:opacity .2s,transform .2s}
.quiz-toast.show{opacity:1;transform:translateY(0)}
@media (min-width:1040px){.cp-wrap{max-width:960px;padding-left:32px;padding-right:32px}.quiz-card{padding:22px 24px 20px}}
@media (max-width:720px){.quiz-stepper-head,.quiz-nav,.quiz-final-actions,.quiz-cross-sell-links,.quiz-gate-form{flex-direction:column;align-items:stretch}.quiz-stepper-score,.quiz-nav-meta{text-align:left}.quiz-nav-next,.quiz-secondary-btn,.quiz-gate-submit,.quiz-final .cp-cta,.quiz-cross-sell-links a{width:100%}.quiz-card,.quiz-final,.quiz-cross-sell{padding:18px}.quiz-stepper-dots{gap:6px}}
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


def class_tokens(tag) -> list[str]:
    tokens = tag.get("class", [])
    return tokens.split() if isinstance(tokens, str) else list(tokens)


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
    shell = new_tag("div", attrs={"class": ["quiz-answer-shell"]})
    content = new_tag("div", attrs={"class": ["quiz-answer-content"]})
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
    <div class="quiz-gate-title">Enter your email to continue with questions 6-15</div>
    <p class="quiz-gate-copy">Free exam updates. No spam. Unsubscribe anytime.</p>
    <form class="quiz-gate-form" id="quizGateForm">
      <input type="email" class="quiz-gate-email-input" id="quizGateEmail" placeholder="you@email.com" autocomplete="email" required>
      <button type="submit" class="quiz-gate-submit" id="quizGateSubmit">Continue with 10 More Questions</button>
    </form>
    <p class="quiz-gate-message" id="quizGateMessage"></p>
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
<div class="quiz-card is-email-locked" id="qcard{global_idx}" data-tier="2" data-question-index="{global_idx}" hidden>
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
    <div class="quiz-gate-prompt">
      <div class="quiz-gate-card">
        <div class="quiz-gate-title">Question coming soon.</div>
        <p class="quiz-gate-copy">The full {total_q}-question course is already live on Udemy.</p>
        <a href="{udemy}" target="_blank" rel="noopener" class="quiz-gate-submit" data-buy-stage="final">Get all {total_q} questions on Udemy</a>
      </div>
    </div>
  </div>
</div>
""",
        "html.parser",
    )
    return str(placeholder.div)


def build_card(card, global_idx: int, total_q: int, udemy: str) -> str:
    tier = 1 if global_idx < 5 else 2
    new_card = copy.deepcopy(card)
    new_card["id"] = f"qcard{global_idx}"
    new_card["data-tier"] = str(tier)
    new_card["data-question-index"] = str(global_idx)
    if global_idx:
        new_card["hidden"] = ""
    else:
        new_card.attrs.pop("hidden", None)
    q_num = new_card.select_one(".quiz-q-num")
    if q_num:
        q_num.string = f"{global_idx + 1}."

    for btn in new_card.select(".quiz-submit-btn"):
        btn.decompose()

    for opt in new_card.select(".quiz-opt"):
        opt.attrs.pop("disabled", None)
        opt["class"] = [c for c in opt.get("class", []) if c not in {"selected", "correct", "wrong"}]
        opt["data-q"] = str(global_idx)

    overall = new_card.select_one(".quiz-overall")
    if overall:
        overall["id"] = f"qexp{global_idx}"
        overall.attrs.pop("open", None)
        overall.attrs.pop("style", None)

    inline = new_card.select_one(".quiz-opt-explains")
    if inline:
        inline.decompose()

    shell, content = question_wrapper(new_card, global_idx)
    content_classes = class_tokens(content)
    if tier == 2:
        content_classes.append("quiz-gate-blur")
    content["class"] = content_classes
    opts = new_card.select_one(".quiz-opts")
    if opts:
        opts.insert_after(interactive_button(global_idx))
    if tier == 2:
        new_card["class"] = class_tokens(new_card) + ["is-email-locked"]
        if global_idx == 5:
            shell.append(BeautifulSoup(gate_prompt_html(), "html.parser"))

    return str(new_card)


def quiz_schema(title: str, code: str, slug: str, cards: list, answers: list) -> str:
    parts = []
    for card, answer in zip(cards[:15], answers[:15]):
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
        "name": f"15-Question {title} Preview",
        "description": f"Work through a 15-question preview for the {title} practice test.",
        "url": f"https://luckyx.dev/courses/{slug}.html#free-quiz",
        "educationalAlignment": {
            "@type": "AlignmentObject",
            "alignmentType": "assesses",
            "targetName": f"ServiceNow {code} Certification",
        },
        "hasPart": parts,
    }
    return "<!-- Structured Data: Quiz -->\n<script type=\"application/ld+json\">\n" + json.dumps(body, indent=2) + "\n</script>"


def progress_dots() -> str:
    slots = []
    for idx in range(15):
        slots.append(f'        <span class="preview-dot" data-slot="{idx}" title="Question {idx + 1}"></span>')
    return "\n".join(slots)


def final_cta(total_q: int, udemy: str) -> str:
    return f"""    <div class="quiz-final" id="quizFinal" hidden>
      <div class="quiz-final-kicker">Preview complete</div>
      <h3>You scored <span id="quizFinalScoreText">0/15</span> on the 15-question preview.</h3>
      <div class="quiz-final-score" id="quizFinalScoreValue">0/15</div>
      <p class="quiz-final-copy">The full course keeps the same answer breakdown style across all {total_q} questions.</p>
      <p class="quiz-final-anchor">Your first exam attempt is free. Your second costs $350.</p>
      <div class="quiz-final-actions">
        <a href="{udemy}" target="_blank" rel="noopener" class="cp-cta" data-buy-stage="final">Get all {total_q} questions for $9.99
          <svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
      </div>
    </div>"""


def cross_sell_block() -> str:
    return """    <div class="quiz-cross-sell" id="quizCrossSell" hidden>
      <h3>Many students also study:</h3>
      <p>Compare all 18 practice tests, or use the cert quiz to plan what to study next.</p>
      <div class="quiz-cross-sell-links">
        <a href="/quiz.html">Find your next cert</a>
        <a href="/compare.html">Compare all 18 courses</a>
      </div>
    </div>"""


def quiz_section(total_q: int, udemy: str, cards_html: list[str]) -> str:
    return f"""  <section class="quiz-section" id="free-quiz" data-preview-style="guided-15">
    <div class="preview-shell">
      <div class="preview-kicker">15-question preview</div>
      <h2>15 Free Preview Questions</h2>
      <p class="quiz-intro">Answer 5 questions free. Enter your email to continue through question 15. The full course has {total_q} questions on Udemy.</p>
      <div class="quiz-stepper-head">
        <div class="quiz-stepper-copy">
          <div class="quiz-stepper-label" id="quizStepLabel">Question 1 of 15</div>
          <div class="quiz-stepper-tier" data-state="free" id="quizTierLabel">Free</div>
        </div>
        <div class="quiz-stepper-score" id="quizMiniScore">0 correct so far</div>
      </div>
      <div class="quiz-stepper-dots" id="quizProgress">
{progress_dots()}
      </div>
    </div>
    <div class="quiz-card-stack">
{chr(10).join(cards_html)}
    </div>
    <div class="quiz-nav" id="quizNav">
      <button type="button" class="quiz-secondary-btn" id="quizPrevBtn">Previous question</button>
      <div class="quiz-nav-meta" id="quizNavMeta">Choose an answer and submit to continue.</div>
      <button type="button" class="quiz-nav-next" id="quizNextBtn" disabled>Next question</button>
    </div>
{final_cta(total_q, udemy)}
{cross_sell_block()}
    <div class="quiz-toast" id="quizToast">Questions 6-15 are ready.</div>
  </section>"""


JS_TEMPLATE = """<script>
const QUIZ=__CONFIG__;
const answers=__ANSWERS__;
const STORAGE_EMAIL='luckyx-email:'+QUIZ.slug,STORAGE_ANSWERS='luckyx-answers:'+QUIZ.slug,STORAGE_SCORE='luckyx-score:'+QUIZ.slug,STORAGE_CURRENT='luckyx-current:'+QUIZ.slug;
const themeToggle=document.getElementById('themeToggle'),cards=Array.from(document.querySelectorAll('.quiz-card')),dots=Array.from(document.querySelectorAll('.preview-dot[data-slot]')),prevBtn=document.getElementById('quizPrevBtn'),nextBtn=document.getElementById('quizNextBtn'),navMeta=document.getElementById('quizNavMeta'),stepLabel=document.getElementById('quizStepLabel'),tierLabel=document.getElementById('quizTierLabel'),miniScore=document.getElementById('quizMiniScore'),gateForm=document.getElementById('quizGateForm'),gateEmail=document.getElementById('quizGateEmail'),gateSubmit=document.getElementById('quizGateSubmit'),gateMessage=document.getElementById('quizGateMessage'),finalBlock=document.getElementById('quizFinal'),finalScoreText=document.getElementById('quizFinalScoreText'),finalScoreValue=document.getElementById('quizFinalScoreValue'),crossSell=document.getElementById('quizCrossSell'),toast=document.getElementById('quizToast');
let emailReady=false,storedAnswers={},currentIndex=0,startEventSent=false,tier1EventSent=false,tier2EventSent=false;const drafts={};
if(themeToggle){themeToggle.addEventListener('click',()=>{const current=document.documentElement.getAttribute('data-theme');const next=current==='light'?'dark':'light';document.documentElement.setAttribute('data-theme',next);localStorage.setItem('luckyx-theme',next);});}
function evt(name,extra){if(typeof gtag!=='function')return;gtag('event',name,Object.assign({cert:QUIZ.code},extra||{}));}
function showToast(message){if(!toast)return;toast.textContent=message;toast.classList.add('show');window.clearTimeout(showToast._timer);showToast._timer=window.setTimeout(()=>toast.classList.remove('show'),2600);}
function readJson(key,fallback){try{const raw=localStorage.getItem(key);return raw?JSON.parse(raw):fallback;}catch(err){return fallback;}}
function normalizeSelection(value){if(!Array.isArray(value))return[];return Array.from(new Set(value.map((item)=>parseInt(item,10)).filter((item)=>Number.isInteger(item)&&item>=0))).sort((a,b)=>a-b);}
function readAnswers(){const parsed=readJson(STORAGE_ANSWERS,{}),out={};if(!parsed||typeof parsed!=='object')return out;Object.keys(parsed).forEach((key)=>{const qi=parseInt(key,10),item=parsed[key];if(!Number.isInteger(qi)||qi<0||qi>=15||!item||typeof item!=='object')return;const selected=normalizeSelection(item.selected);if(!selected.length||typeof item.isCorrect!=='boolean')return;out[qi]={selected,isCorrect:item.isCorrect};});return out;}
function readCurrent(){const raw=localStorage.getItem(STORAGE_CURRENT),value=parseInt(raw,10);return Number.isInteger(value)?value:null;}
function writeAnswers(){localStorage.setItem(STORAGE_ANSWERS,JSON.stringify(storedAnswers));}
function writeCurrent(){localStorage.setItem(STORAGE_CURRENT,String(currentIndex));}
function scoreSlice(start,end){let answered=0,correct=0;for(let i=start;i<=end;i+=1){if(!storedAnswers[i])continue;answered+=1;if(storedAnswers[i].isCorrect)correct+=1;}return{answered,correct};}
function saveScoreState(){const free5=scoreSlice(0,4),total15=scoreSlice(0,14);localStorage.setItem(STORAGE_SCORE,JSON.stringify({free5:free5.correct,total15:total15.correct}));}
function correctIndicesFor(qi){return(Array.isArray(answers[qi])?answers[qi].slice():[answers[qi]]).sort((a,b)=>a-b);}
function isUnlocked(qi){return qi<5||emailReady;}
function nextPendingIndex(){const max=emailReady?14:5;for(let i=0;i<=max;i+=1){if(!storedAnswers[i])return i;}return max;}
function navigationLimit(){return nextPendingIndex();}
function normalizeCurrent(candidate){const limit=navigationLimit();if(!Number.isInteger(candidate))return limit;if(candidate<0)return 0;if(candidate>limit)return limit;return candidate;}
function setMessage(text,cls){if(!gateMessage)return;gateMessage.textContent=text||'';gateMessage.classList.remove('is-error','is-success');if(cls)gateMessage.classList.add(cls);}
function processSections(container){if(!container||container.dataset.processed)return;container.dataset.processed='1';const h5s=Array.from(container.querySelectorAll('h5'));if(!h5s.length)return;const sections=[];h5s.forEach((h5)=>{const title=h5.textContent.toLowerCase();let cls='exp-section';if(title.includes('correct answer'))cls+=' exp-correct-answer';else if(title.includes('source'))cls+=' exp-source';else if(title.includes('expert'))cls+=' exp-expert';else if(title.includes('why')||title.includes('wrong'))cls+=' exp-wrong';else if(title.includes('memory'))cls+=' exp-memory';else if(title.includes('real-world')||title.includes('example'))cls+=' exp-realworld';sections.push({cls,h5});});for(let i=0;i<sections.length;i+=1){const section=sections[i],div=document.createElement('div'),next=i<sections.length-1?sections[i+1].h5:null;div.className=section.cls;section.h5.parentNode.insertBefore(div,section.h5);div.appendChild(section.h5);while(div.nextSibling&&div.nextSibling!==next)div.appendChild(div.nextSibling);}}
function showExplanations(qi){const card=document.getElementById('qcard'+qi);if(!card)return;const opts=card.querySelectorAll('.quiz-opt'),correct=correctIndicesFor(qi);opts.forEach((opt,index)=>{const per=opt.getAttribute('data-exp');if(!per||opt.querySelector('.quiz-opt-exp-inline'))return;const ok=correct.indexOf(index)!==-1,txt=per.replace(/^(CORRECT|INCORRECT):\\s*/i,''),div=document.createElement('div'),icon=ok?'\\u2713':'\\u2717';div.className='quiz-opt-exp-inline '+(ok?'qoe-is-correct':'qoe-is-wrong');div.innerHTML='<div class=\"qoe-header\">'+(ok?'<span class=\"qoe-correct\">'+icon+' Correct</span>':'<span class=\"qoe-wrong\">'+icon+' Incorrect</span>')+' <span class=\"qoe-letter\">Option '+'ABCDEFG'[index]+'</span></div><div class=\"qoe-text\">'+txt+'</div>';opt.appendChild(div);});const overall=document.getElementById('qexp'+qi);if(!overall)return;const content=overall.querySelector('.quiz-overall-content');if(!content||!content.innerHTML.trim())return;processSections(content);overall.open=false;overall.removeAttribute('open');overall.style.display='block';}
document.querySelectorAll('.quiz-overall').forEach((detail)=>{detail.addEventListener('toggle',function(){if(!this.open)return;document.querySelectorAll('.quiz-overall').forEach((other)=>{if(other!==this)other.open=false;});});});
function clearOptionState(opt){opt.classList.remove('selected','correct','wrong');opt.removeAttribute('disabled');}
function renderDraft(qi){const card=document.getElementById('qcard'+qi);if(!card)return;card.removeAttribute('data-state');const selected=drafts[qi]||[];card.querySelectorAll('.quiz-opt').forEach((opt,index)=>{clearOptionState(opt);if(selected.indexOf(index)!==-1)opt.classList.add('selected');if(isUnlocked(qi))opt.removeAttribute('disabled');else opt.setAttribute('disabled','');});const btn=card.querySelector('.quiz-submit-btn');if(btn)btn.style.display=selected.length&&isUnlocked(qi)?'inline-flex':'none';const overall=card.querySelector('.quiz-overall');if(overall){overall.open=false;overall.removeAttribute('open');overall.style.display='';}}
function applyResponse(qi,response){const card=document.getElementById('qcard'+qi);if(!card||!response)return;const correct=correctIndicesFor(qi),opts=card.querySelectorAll('.quiz-opt');card.dataset.state=response.isCorrect?'correct':'wrong';opts.forEach((opt)=>clearOptionState(opt));if(response.isCorrect){response.selected.forEach((index)=>{if(opts[index])opts[index].classList.add('correct');});}else{response.selected.forEach((index)=>{if(!opts[index])return;if(correct.indexOf(index)===-1)opts[index].classList.add('wrong');else opts[index].classList.add('correct');});correct.forEach((index)=>{if(opts[index])opts[index].classList.add('correct');});}opts.forEach((opt)=>opt.setAttribute('disabled',''));const btn=card.querySelector('.quiz-submit-btn');if(btn)btn.style.display='none';showExplanations(qi);}
function updateHeader(){if(stepLabel)stepLabel.textContent='Question '+(currentIndex+1)+' of 15';if(miniScore){const total=scoreSlice(0,14);miniScore.textContent=total.correct+' correct so far';}if(tierLabel){let label='Free',state='free';if(currentIndex>=5&&!emailReady){label='Email required';state='locked';}else if(currentIndex>=5&&emailReady){label='Preview unlocked';state='open';}tierLabel.textContent=label;tierLabel.dataset.state=state;}}
function updateDots(){const limit=navigationLimit();dots.forEach((dot)=>{const idx=parseInt(dot.dataset.slot,10);dot.classList.remove('is-available','is-locked','is-correct','is-wrong','is-current');dot.classList.add(idx<=limit?'is-available':'is-locked');if(storedAnswers[idx])dot.classList.add(storedAnswers[idx].isCorrect?'is-correct':'is-wrong');if(idx===currentIndex)dot.classList.add('is-current');});}
function updateVisibleCard(){cards.forEach((card)=>{const qi=parseInt(card.dataset.questionIndex,10),active=qi===currentIndex;card.hidden=!active;card.classList.toggle('is-active',active);card.setAttribute('aria-hidden',active?'false':'true');});}
function updateNav(){const answered=!!storedAnswers[currentIndex],complete=scoreSlice(0,14).answered===15,limit=complete?14:navigationLimit();if(prevBtn)prevBtn.disabled=currentIndex===0;if(nextBtn){nextBtn.hidden=currentIndex===14&&complete;nextBtn.disabled=!answered||currentIndex>=limit;nextBtn.textContent='Next question';}if(navMeta){if(currentIndex===5&&!emailReady)navMeta.textContent='Enter your email to continue.';else if(currentIndex===14&&complete)navMeta.textContent='Preview complete. Your score is below.';else if(answered)navMeta.textContent='Ready for the next question.';else navMeta.textContent='Choose an answer and submit to continue.';}}
function updateFinal(){const total=scoreSlice(0,14),complete=total.answered===15;if(finalBlock){finalBlock.hidden=!complete;if(complete){finalScoreText.textContent=total.correct+'/15';finalScoreValue.textContent=total.correct+'/15';}}if(crossSell)crossSell.hidden=!complete;}
function persistState(){writeAnswers();saveScoreState();writeCurrent();}
function setEmailAccess(open){emailReady=!!open;cards.forEach((card)=>{const qi=parseInt(card.dataset.questionIndex,10);if(qi<5)return;card.classList.toggle('is-email-locked',!open);const content=card.querySelector('.quiz-answer-content');if(content)content.classList.toggle('quiz-gate-blur',!open);if(qi===5){card.querySelectorAll('[data-email-overlay]').forEach((overlay)=>{overlay.hidden=open;});}});if(!emailReady&&currentIndex>5)currentIndex=5;}
function maybeSendCompletionEvents(qi){const free5=scoreSlice(0,4),total=scoreSlice(0,14);if(qi===0&&!startEventSent){startEventSent=true;evt('quiz_start',{tier:1});}if(!tier1EventSent&&free5.answered===5){tier1EventSent=true;evt('quiz_tier1_complete',{score:free5.correct});}if(!tier2EventSent&&total.answered===15){tier2EventSent=true;evt('quiz_tier2_complete',{score_total:total.correct});}}
function render(){currentIndex=normalizeCurrent(currentIndex);cards.forEach((card)=>{const qi=parseInt(card.dataset.questionIndex,10);if(storedAnswers[qi])applyResponse(qi,storedAnswers[qi]);else renderDraft(qi);});updateVisibleCard();updateHeader();updateDots();updateNav();updateFinal();persistState();}
function scrollToCurrent(){const card=document.getElementById('qcard'+currentIndex);if(card)card.scrollIntoView({behavior:'smooth',block:'start'});}
document.querySelectorAll('.quiz-opt[data-q]').forEach((opt)=>{opt.addEventListener('click',function(){const qi=parseInt(this.dataset.q,10);if(!isUnlocked(qi)||storedAnswers[qi])return;const idx=parseInt(this.dataset.idx,10),multi=Array.isArray(answers[qi]),current=drafts[qi]?drafts[qi].slice():[];if(multi){const pos=current.indexOf(idx);if(pos===-1)current.push(idx);else current.splice(pos,1);}else{current.length=0;current.push(idx);}drafts[qi]=normalizeSelection(current);render();});});
function submitAnswer(){const qi=parseInt(this.dataset.q,10);if(!isUnlocked(qi)||storedAnswers[qi])return;const selected=normalizeSelection(drafts[qi]);if(!selected.length)return;const correct=correctIndicesFor(qi),isCorrect=selected.length===correct.length&&selected.every((value,index)=>value===correct[index]);storedAnswers[qi]={selected,isCorrect};delete drafts[qi];maybeSendCompletionEvents(qi);render();}
document.querySelectorAll('.quiz-submit-btn[data-q]').forEach((btn)=>btn.addEventListener('click',submitAnswer));
if(prevBtn){prevBtn.addEventListener('click',()=>{if(currentIndex===0)return;currentIndex-=1;render();scrollToCurrent();});}
if(nextBtn){nextBtn.addEventListener('click',()=>{const complete=scoreSlice(0,14).answered===15,limit=complete?14:navigationLimit();if(!storedAnswers[currentIndex]||currentIndex>=limit)return;currentIndex+=1;render();scrollToCurrent();if(currentIndex===5&&!emailReady&&gateEmail)window.setTimeout(()=>gateEmail.focus(),180);});}
function handleGateSubmit(event){event.preventDefault();const email=gateEmail.value.trim().toLowerCase(),valid=/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)&&email.length<=254;if(!valid){setMessage('Use a valid email address.','is-error');return;}gateSubmit.disabled=true;gateSubmit.textContent='Sending...';setMessage('');fetch('https://app.convertkit.com/forms/'+QUIZ.convertKitFormId+'/subscriptions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email_address:email,fields:{source:'quiz-gate-'+QUIZ.slug}})}).then((response)=>{if(!response.ok&&response.status!==200&&response.status!==201)throw new Error('gate failed');localStorage.setItem(STORAGE_EMAIL,'1');setMessage('Questions 6-15 are ready.','is-success');evt('quiz_email_submit');showToast('Questions 6-15 are ready.');gateSubmit.disabled=false;gateSubmit.textContent='Continue with 10 More Questions';setEmailAccess(true);currentIndex=Math.max(currentIndex,5);render();}).catch(()=>{gateSubmit.disabled=false;gateSubmit.textContent='Continue with 10 More Questions';setMessage('That did not go through. Please try again.','is-error');});}
if(gateForm)gateForm.addEventListener('submit',handleGateSubmit);
document.querySelectorAll('a[href*=\"udemy.com\"]').forEach((link)=>{link.addEventListener('click',()=>{const total=scoreSlice(0,14),stage=link.dataset.buyStage||(link.closest('#quizFinal')?'final':'hero');evt('quiz_buy_click',{tier:stage,score:total.correct});});});
storedAnswers=readAnswers();emailReady=localStorage.getItem(STORAGE_EMAIL)==='1'||Object.keys(storedAnswers).some((key)=>parseInt(key,10)>=5);startEventSent=Object.keys(storedAnswers).length>0;tier1EventSent=scoreSlice(0,4).answered===5;tier2EventSent=scoreSlice(0,14).answered===15;currentIndex=readCurrent();setEmailAccess(emailReady);render();evt('quiz_page_view');__EXTRA__
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
    if len(cards) < 15 or len(answers) < 15:
        raise ValueError(f"{source_path.name}: expected at least 15 interactive source questions.")
    return raw, list(cards[:15]), list(answers[:15]), 'id="cdDays"' in raw


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
    if tiers[:5] != ["1"] * 5 or tiers[5:] != ["2"] * 10:
        raise ValueError(f"{path.name}: unexpected tier distribution {tiers}.")
    if len(extract_answers(raw)) != 15:
        raise ValueError(f"{path.name}: expected 15 interactive answers in script.")
    if raw.count('class="preview-dot"') < 15:
        raise ValueError(f"{path.name}: progress dots are missing.")
    if 'id="quizGateForm"' not in raw or 'id="quizPrevBtn"' not in raw or 'id="quizNextBtn"' not in raw or 'id="quizFinal"' not in raw:
        raise ValueError(f"{path.name}: gate, navigation, or final result markup is missing.")
    if 'data-preview-style="guided-15"' not in raw:
        raise ValueError(f"{path.name}: guided preview marker is missing.")
    if "15 Free Preview Questions" not in raw:
        raise ValueError(f"{path.name}: new preview heading missing.")
    if 'preview-progress' in raw or 'tier1Interstitial' in raw or 'tier2Interstitial' in raw:
        raise ValueError(f"{path.name}: stacked three-tier markup still present.")
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
        print(f"Built guided preview: {path.name}")
    cleanup_preview_pages()
    update_sitemap()


if __name__ == "__main__":
    main()
