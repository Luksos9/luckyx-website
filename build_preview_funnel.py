#!/usr/bin/env python3
"""Build the 2-step free preview funnel from the current rich course pages."""

from __future__ import annotations

import ast
import copy
import json
import re
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
COURSES_DIR = ROOT / "courses"
SOURCE_DIR = ROOT / "preview_source" / "courses"

REPLACEMENTS = {
    "â€”": "-",
    "â€“": "-",
    "â€™": "'",
    "â€˜": "'",
    "â€œ": '"',
    "â€\x9d": '"',
    "â€¦": "...",
    "Â ": " ",
    "Â": "",
    "â€”": "—",
    "â€“": "–",
    "â€™": "’",
    "â€˜": "‘",
    "â€œ": "“",
    "â€\x9d": "”",
    "â€¦": "…",
    "Â ": " ",
    "Â": "",
}

MOJIBAKE_MARKERS = ("Â", "Ã", "â€", "â€™", "â€œ", "â€\x9d")

QUIZ_SECTION_RE = re.compile(r'  <section class="quiz-section" id="free-quiz"[^>]*>.*?  </section>', re.S)
QUIZ_SCHEMA_RE = re.compile(r"<!-- Structured Data: Quiz -->\s*<script type=\"application/ld\+json\">.*?</script>", re.S)
QUIZ_CSS_RE = re.compile(r"/\* Quiz section \*/.*?(?=/\* Countdown banner \*/)", re.S)
POPUP_RE = re.compile(r"\n<!-- Preview Exit Popup -->.*?<!-- /Preview Exit Popup -->\n", re.S)
ANSWERS_RE = re.compile(r"\banswers\s*=\s*(\[[\s\S]*?\])(?:;|,STATE|,EXIT|,themeToggle)", re.S)

QUIZ_CSS = """/* Quiz section */
.quiz-section{margin-top:48px}
.quiz-section h2{font-size:1.35rem;font-weight:700;margin-bottom:10px;line-height:1.25}
.quiz-intro{color:var(--text-dim);font-size:.96rem;margin:0;max-width:58ch}
.preview-shell{margin-bottom:20px}
.preview-kicker{display:inline-flex;align-items:center;gap:8px;margin-bottom:14px;padding:6px 12px;border-radius:999px;background:rgba(221,92,12,.08);border:1px solid rgba(221,92,12,.18);color:var(--orange);font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.preview-copy-row{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-bottom:18px}
.preview-step-note{color:var(--text-dim);font-size:.9rem;line-height:1.55;max-width:32ch}
.preview-index{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;list-style:none;margin:0 0 20px;padding:0}
.preview-slot{min-height:58px;padding:10px 6px;border-radius:12px;border:1px solid var(--border);background:var(--bg-raised);text-align:center}
.preview-slot-num{display:block;font-size:.96rem;font-weight:700;color:var(--text);line-height:1.1}
.preview-slot-label{display:block;margin-top:4px;font-size:.68rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:var(--text-dim)}
.preview-slot.is-active{border-color:rgba(221,92,12,.35);background:rgba(221,92,12,.08)}
.preview-slot.is-done{border-color:rgba(46,160,67,.35);background:rgba(46,160,67,.08)}
.preview-slot.is-done .preview-slot-num,.preview-slot.is-done .preview-slot-label{color:#2ea043}
.preview-slot.is-prior{border-style:dashed;background:rgba(255,255,255,.02)}
.quiz-card{background:var(--bg-raised);border:1px solid var(--border);border-radius:14px;padding:20px 20px 18px;margin-bottom:14px;transition:border-color .2s}
.quiz-card[data-state="correct"]{border-color:#2ea043}
.quiz-card[data-state="wrong"]{border-color:#d73a49}
.quiz-q{font-weight:600;font-size:1rem;margin-bottom:14px;line-height:1.5}
.quiz-q-num{color:var(--orange);font-weight:700;margin-right:6px}
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
.preview-result{display:none;margin-top:24px;padding:22px;border-radius:18px;border:1px solid rgba(221,92,12,.22);background:radial-gradient(circle at top right,rgba(221,92,12,.12),transparent 42%),linear-gradient(180deg,rgba(255,255,255,.015),rgba(255,255,255,0))}
.preview-result.show{display:block}
.preview-result-kicker{color:var(--orange);font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.preview-result-head{margin-top:10px;font-size:1.5rem;line-height:1.25;font-weight:700}
.preview-score-row{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin:18px 0 8px}
.preview-score-value{font-size:2.2rem;font-weight:800;color:var(--text);line-height:1}
.preview-score-label{color:var(--text-dim);font-size:.92rem}
.preview-result-copy{color:var(--text-dim);margin-top:8px;max-width:56ch}
.preview-offer-list{list-style:none;margin:16px 0 0;padding:0;display:grid;gap:8px}
.preview-offer-list li{display:flex;gap:10px;align-items:flex-start;color:var(--text-dim)}
.preview-offer-bullet{width:22px;height:22px;flex:0 0 22px;display:inline-flex;align-items:center;justify-content:center;border-radius:50%;background:rgba(221,92,12,.1);color:var(--orange);font-size:.8rem;font-weight:700;margin-top:1px}
.preview-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.preview-secondary-btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;padding:14px 22px;border-radius:12px;border:1px solid var(--border-hover);background:transparent;color:var(--text);font-family:var(--font);font-size:.98rem;font-weight:700;cursor:pointer}
.preview-secondary-btn:hover{background:rgba(221,92,12,.06);border-color:var(--orange)}
.preview-text-link{display:inline-flex;align-items:center;gap:8px;margin-top:14px;border:none;background:none;color:var(--text-dim);font-family:var(--font);font-size:.9rem;font-weight:700;cursor:pointer;padding:0}
.preview-text-link:hover{color:var(--orange);text-decoration:none}
.preview-helper{margin-top:14px;color:var(--text-dim);font-size:.88rem;line-height:1.6}
.preview-email-wrap{display:none;margin-top:18px;padding-top:16px;border-top:1px solid var(--border)}
.preview-email-wrap.show{display:block}
.preview-email-wrap h3{font-size:1.02rem;margin-bottom:6px}
.preview-email-wrap p{color:var(--text-dim);font-size:.92rem}
.preview-lead-form{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
.preview-lead-form input[type="email"]{flex:1 1 240px;min-height:48px;border-radius:12px;border:1px solid var(--border);background:var(--bg-card);color:var(--text);padding:0 14px;font-family:var(--font);font-size:.95rem}
.preview-lead-form input[type="email"]::placeholder{color:var(--text-faint)}
.preview-lead-form input[type="email"]:focus{outline:none;border-color:rgba(221,92,12,.45);box-shadow:0 0 0 3px rgba(221,92,12,.12)}
.preview-lead-form button{min-height:48px;padding:0 18px;border-radius:12px;border:none;background:var(--orange);color:#fff;font-family:var(--font);font-size:.94rem;font-weight:700;cursor:pointer}
.preview-lead-form button:disabled{opacity:.72;cursor:wait}
.preview-lead-note{margin-top:10px;color:var(--text-dim);font-size:.82rem;line-height:1.5}
.preview-exit{position:fixed;inset:0;z-index:1200;display:none;align-items:center;justify-content:center;padding:20px;background:rgba(5,5,7,.74)}
.preview-exit.active{display:flex}
.preview-exit-card{position:relative;width:min(560px,100%);padding:24px;border-radius:20px;border:1px solid var(--border);background:radial-gradient(circle at top right,rgba(221,92,12,.14),transparent 38%),var(--bg-raised);box-shadow:0 24px 70px rgba(0,0,0,.35)}
.preview-exit-close{position:absolute;top:12px;right:12px;width:38px;height:38px;border-radius:50%;border:1px solid var(--border);background:transparent;color:var(--text-dim);cursor:pointer;font-size:1.2rem}
.preview-exit-kicker{color:var(--orange);font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.preview-exit-title{margin-top:10px;font-size:1.45rem;line-height:1.25}
.preview-exit-copy{margin-top:10px;color:var(--text-dim);line-height:1.6}
.preview-exit-link{margin-top:14px;display:inline-flex;align-items:center;gap:8px;font-weight:700}
@media (min-width:720px){.preview-index{grid-template-columns:repeat(10,minmax(0,1fr))}}
@media (min-width:1040px){.quiz-section{width:min(960px,calc(100vw - 72px));max-width:none;position:relative;left:50%;transform:translateX(-50%)}.preview-copy-row{align-items:flex-end}.quiz-card{padding:22px 24px 20px}}
@media (max-width:600px){.cp-title,.cp-price{font-size:1.5rem}.cp-cta,.preview-secondary-btn{width:100%;justify-content:center}.quiz-card{padding:16px}.preview-exit-card{padding:22px 18px}.preview-lead-form{flex-direction:column}.preview-lead-form button{width:100%}}
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


def clone_card(card, local_idx: int, display_number: int) -> str:
    new_card = copy.deepcopy(card)
    new_card["id"] = f"qcard{local_idx}"
    q_num = new_card.select_one(".quiz-q-num")
    if q_num:
        q_num.string = f"{display_number}."
    for opt in new_card.select(".quiz-opt"):
        opt["data-q"] = str(local_idx)
        opt.attrs.pop("disabled", None)
        opt["class"] = [c for c in opt.get("class", []) if c not in {"selected", "correct", "wrong"}]
    btn = new_card.select_one(".quiz-submit-btn")
    if btn:
        btn["data-q"] = str(local_idx)
        btn["style"] = "display:none"
    exp = new_card.select_one(".quiz-opt-explains")
    if exp:
        exp["id"] = f"qoptexp{local_idx}"
        exp["style"] = "display:none"
    overall = new_card.select_one(".quiz-overall")
    if overall:
        overall["id"] = f"qexp{local_idx}"
        overall.attrs.pop("open", None)
        overall.attrs.pop("style", None)
    return str(new_card)


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


JS_TEMPLATE = """<script>
const PREVIEW = __CONFIG__;
const answers = __ANSWERS__;
const STATE = 'luckyx-preview:' + PREVIEW.slug;
const EXIT = 'luckyx-exit-shown:' + PREVIEW.slug;
const themeToggle = document.getElementById('themeToggle');
const quizSection = document.getElementById('free-quiz');
const sel = {};
const done = new Set();
const pageStartedAt = Date.now();
let answered = 0;
let score = 0;
let exitReady = false;
let emailCaptured = false;
let completeSent = false;
let quizSeenAt = 0;
let lastInteractionAt = pageStartedAt;
let interactionCount = 0;
let submitCount = 0;

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('luckyx-theme', next);
  });
}

function evt(name, extra) {
  if (typeof gtag !== 'function') return;
  gtag('event', name, Object.assign({ course_slug: PREVIEW.slug, preview_step: PREVIEW.step }, extra || {}));
}

function readState() {
  try {
    const raw = sessionStorage.getItem(STATE);
    return raw ? JSON.parse(raw) : null;
  } catch (err) {
    return null;
  }
}

function saveState(payload) {
  sessionStorage.setItem(STATE, JSON.stringify(payload));
}

function clearState() {
  sessionStorage.removeItem(STATE);
  sessionStorage.removeItem(EXIT);
}

function markExitReady() {
  exitReady = true;
  if (!quizSeenAt) quizSeenAt = Date.now();
}

function touchInteraction() {
  interactionCount += 1;
  lastInteractionAt = Date.now();
  markExitReady();
}

if ('IntersectionObserver' in window && quizSection) {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        markExitReady();
        obs.disconnect();
      }
    });
  }, { threshold: 0.25 });
  obs.observe(quizSection);
} else if (quizSection) {
  window.addEventListener('scroll', function handleQuizSeen() {
    if (quizSection.getBoundingClientRect().top < window.innerHeight * 0.8) {
      markExitReady();
      window.removeEventListener('scroll', handleQuizSeen);
    }
  }, { passive: true });
}

evt('preview_page_view');

document.querySelectorAll('a.cp-cta[href*="udemy.com"],a.preview-exit-link[href*="udemy.com"]').forEach((link) => {
  link.addEventListener('click', () => {
    let source = 'hero';
    if (link.closest('.preview-result')) source = PREVIEW.step === 1 ? 'step_one_result' : 'final_result';
    else if (link.closest('.preview-exit-card')) source = 'exit_popup';
    evt('preview_buy_click', { cta_source: source });
  });
});

document.querySelectorAll('.quiz-card').forEach((card) => {
  if (card.querySelector('.quiz-submit-btn')) return;
  const qi = parseInt(card.id.replace('qcard', ''), 10);
  const btn = document.createElement('button');
  btn.className = 'quiz-submit-btn';
  btn.dataset.q = qi;
  btn.textContent = 'Submit Answer';
  const opts = card.querySelector('.quiz-opts');
  opts.parentNode.insertBefore(btn, opts.nextSibling);
});

function processSections(container) {
  if (container.dataset.processed) return;
  container.dataset.processed = '1';
  const h5s = Array.from(container.querySelectorAll('h5'));
  if (!h5s.length) return;
  const sections = [];
  h5s.forEach((h5) => {
    const title = h5.textContent.toLowerCase();
    let cls = 'exp-section';
    if (title.includes('correct answer')) cls += ' exp-correct-answer';
    else if (title.includes('source')) cls += ' exp-source';
    else if (title.includes('expert')) cls += ' exp-expert';
    else if (title.includes('why') || title.includes('wrong')) cls += ' exp-wrong';
    else if (title.includes('memory')) cls += ' exp-memory';
    else if (title.includes('real-world') || title.includes('example')) cls += ' exp-realworld';
    sections.push({ cls, h5 });
  });
  for (let i = 0; i < sections.length; i += 1) {
    const section = sections[i];
    const div = document.createElement('div');
    const next = i < sections.length - 1 ? sections[i + 1].h5 : null;
    div.className = section.cls;
    section.h5.parentNode.insertBefore(div, section.h5);
    div.appendChild(section.h5);
    while (div.nextSibling && div.nextSibling !== next) div.appendChild(div.nextSibling);
  }
}

function updateSlots() {
  const prior = readState();
  document.querySelectorAll('.preview-slot').forEach((slot) => {
    const globalIndex = parseInt(slot.dataset.slot, 10);
    slot.classList.remove('is-done', 'is-active', 'is-prior');
    if (PREVIEW.step === 2 && globalIndex <= PREVIEW.questionCount) {
      slot.classList.add(prior && prior.page1Answered === PREVIEW.questionCount ? 'is-done' : 'is-prior');
      return;
    }
    if (globalIndex >= PREVIEW.questionStart && globalIndex <= PREVIEW.questionEnd) {
      const local = globalIndex - PREVIEW.questionStart;
      slot.classList.add(done.has(local) ? 'is-done' : 'is-active');
    }
  });
}

function showExplanations(qi) {
  const card = document.getElementById('qcard' + qi);
  const opts = card.querySelectorAll('.quiz-opt');
  const correct = Array.isArray(answers[qi]) ? answers[qi] : [answers[qi]];
  opts.forEach((opt, index) => {
    const per = opt.getAttribute('data-exp');
    if (!per || opt.querySelector('.quiz-opt-exp-inline')) return;
    const ok = correct.indexOf(index) !== -1;
    const txt = per.replace(/^(CORRECT|INCORRECT):\\s*/i, '');
    const div = document.createElement('div');
    const icon = ok ? '\\u2713' : '\\u2717';
    div.className = 'quiz-opt-exp-inline ' + (ok ? 'qoe-is-correct' : 'qoe-is-wrong');
    div.innerHTML = '<div class="qoe-header">' +
      (ok ? '<span class="qoe-correct">' + icon + ' Correct</span>' : '<span class="qoe-wrong">' + icon + ' Incorrect</span>') +
      ' <span class="qoe-letter">Option ' + 'ABCDEFG'[index] + '</span></div><div class="qoe-text">' + txt + '</div>';
    opt.appendChild(div);
  });
  const overall = document.getElementById('qexp' + qi);
  if (!overall) return;
  const content = overall.querySelector('.quiz-overall-content');
  if (!content || !content.innerHTML.trim()) return;
  processSections(content);
  overall.open = false;
  overall.removeAttribute('open');
  overall.style.display = 'block';
}

document.querySelectorAll('.quiz-overall').forEach((detail) => {
  detail.addEventListener('toggle', function () {
    if (!this.open) return;
    document.querySelectorAll('.quiz-overall').forEach((other) => {
      if (other !== this) other.open = false;
    });
  });
});

document.querySelectorAll('.quiz-opt').forEach((opt) => {
  opt.addEventListener('click', function () {
    touchInteraction();
    const qi = parseInt(this.dataset.q, 10);
    const card = document.getElementById('qcard' + qi);
    if (card.dataset.state) return;
    const idx = parseInt(this.dataset.idx, 10);
    const multi = Array.isArray(answers[qi]);
    if (!sel[qi]) sel[qi] = new Set();
    if (multi) {
      if (sel[qi].has(idx)) {
        sel[qi].delete(idx);
        this.classList.remove('selected');
      } else {
        sel[qi].add(idx);
        this.classList.add('selected');
      }
    } else {
      card.querySelectorAll('.quiz-opt').forEach((other) => other.classList.remove('selected'));
      sel[qi] = new Set([idx]);
      this.classList.add('selected');
    }
    const btn = card.querySelector('.quiz-submit-btn');
    if (btn) btn.style.display = sel[qi].size > 0 ? 'block' : 'none';
  });
});

function pageOneCopy(s) {
  if (s === PREVIEW.questionCount) return 'Perfect page 1. Continue to questions 6-10, then decide if you want the full ' + PREVIEW.totalQuestionCount + '-question bank.';
  if (s >= 3) return 'Solid start. Finish questions 6-10 to see a fuller slice of the exam before you buy.';
  return 'This is exactly where the full course helps: more reps, more sourced explanations, and less guessing under pressure.';
}

function finalCopy(s) {
  if (s === PREVIEW.totalPreviewQuestions) return 'Perfect free preview. The full course is still the fastest way to stress-test the rest of the blueprint before exam day.';
  if (s >= 7) return 'Strong free preview. The full course helps close the last gaps before you sit the exam.';
  return 'The free preview exposed real gaps. The full course is built to fix them with more exam-style repetition and richer explanations.';
}

function showResult() {
  const box = document.getElementById('previewResult');
  const scoreValue = document.getElementById('previewScoreValue');
  const scoreLabel = document.getElementById('previewScoreLabel');
  const copyEl = document.getElementById('previewResultCopy');
  const helper = document.getElementById('previewHelper');
  const emailWrap = document.getElementById('previewEmailWrap');
  const continueBtn = document.getElementById('previewContinueBtn');
  const backLink = document.getElementById('previewBackLink');
  box.classList.add('show');
  box.scrollIntoView({ behavior: 'smooth', block: 'start' });
  if (PREVIEW.step === 1) {
    saveState({ page1Answered: answered, page1Score: score, savedAt: Date.now() });
    scoreValue.textContent = score + '/' + PREVIEW.questionCount;
    scoreLabel.textContent = 'Page 1 of 2 complete';
    copyEl.textContent = pageOneCopy(score);
    helper.textContent = 'You have finished questions 1-5. Questions 6-10 are next.';
    if (continueBtn) continueBtn.hidden = false;
    if (emailWrap) emailWrap.classList.remove('show');
    if (backLink) backLink.hidden = true;
    return;
  }
  const prior = readState();
  if (prior && prior.page1Answered === PREVIEW.questionCount) {
    const total = prior.page1Score + score;
    scoreValue.textContent = total + '/' + PREVIEW.totalPreviewQuestions;
    scoreLabel.textContent = '10-question free preview complete';
    copyEl.textContent = finalCopy(total);
    helper.textContent = 'You have now seen 10 free questions. The full course keeps the same answer breakdown style across the rest of the bank.';
  } else {
    scoreValue.textContent = score + '/' + PREVIEW.questionCount;
    scoreLabel.textContent = 'Page 2 complete';
    copyEl.textContent = 'You completed questions 6-10 only. Start from page 1 if you want the full 10-question preview before deciding.';
    helper.textContent = 'Page 1 contains questions 1-5 and sets up the full 10-question score.';
    if (backLink) backLink.hidden = false;
  }
  if (emailWrap) emailWrap.classList.add('show');
  if (!completeSent) {
    completeSent = true;
    evt('preview_complete', {
      page_score: score,
      combined_score: prior && prior.page1Answered === PREVIEW.questionCount ? prior.page1Score + score : null
    });
  }
}

function submitAnswer() {
  touchInteraction();
  submitCount += 1;
  const qi = parseInt(this.dataset.q, 10);
  const card = document.getElementById('qcard' + qi);
  if (card.dataset.state) return;
  const selected = Array.from(sel[qi] || []).sort((a, b) => a - b);
  const correct = (Array.isArray(answers[qi]) ? answers[qi].slice() : [answers[qi]]).sort((a, b) => a - b);
  const opts = card.querySelectorAll('.quiz-opt');
  const ok = selected.length === correct.length && selected.every((value, index) => value === correct[index]);
  if (ok) {
    score += 1;
    card.dataset.state = 'correct';
    selected.forEach((index) => opts[index].classList.add('correct'));
  } else {
    card.dataset.state = 'wrong';
    selected.forEach((index) => {
      if (correct.indexOf(index) === -1) opts[index].classList.add('wrong');
      else opts[index].classList.add('correct');
    });
    correct.forEach((index) => opts[index].classList.add('correct'));
  }
  opts.forEach((opt) => opt.setAttribute('disabled', ''));
  this.style.display = 'none';
  answered += 1;
  done.add(qi);
  updateSlots();
  showExplanations(qi);
  if (answered === answers.length) showResult();
}

document.querySelectorAll('.quiz-submit-btn').forEach((btn) => btn.addEventListener('click', submitAnswer));

const continueBtn = document.getElementById('previewContinueBtn');
if (continueBtn) {
  continueBtn.addEventListener('click', () => {
    saveState({ page1Answered: answered, page1Score: score, savedAt: Date.now() });
    evt('preview_continue', { page_score: score });
    window.location.href = PREVIEW.page2Url + '#free-quiz';
  });
}

const retakeBtn = document.getElementById('previewRetakeBtn');
if (retakeBtn) {
  retakeBtn.addEventListener('click', () => {
    clearState();
    window.location.href = PREVIEW.page1Url + '#free-quiz';
  });
}

function handleLead(form) {
  const input = form.querySelector('input[type="email"]');
  const btn = form.querySelector('button');
  const email = input.value.trim().toLowerCase();
  const ok = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email) && email.length <= 254;
  const defaultText = btn.dataset.defaultText || btn.textContent;
  if (!ok) {
    btn.textContent = 'Use a valid email';
    btn.style.background = '#c43030';
    setTimeout(() => {
      btn.textContent = defaultText;
      btn.style.background = '';
    }, 2500);
    return;
  }
  btn.textContent = 'Sending...';
  btn.disabled = true;
  fetch('https://app.convertkit.com/forms/' + PREVIEW.convertKitFormId + '/subscriptions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ email_address: email })
  })
    .then((response) => {
      if (response.ok || response.status === 200 || response.status === 201) {
        emailCaptured = true;
        input.disabled = true;
        btn.textContent = 'Check your inbox';
        btn.style.background = '#1f7a50';
        evt('preview_email_submit', { email_source: form.dataset.source || form.id || 'unknown' });
        return;
      }
      throw new Error('lead fail');
    })
    .catch(() => {
      btn.textContent = 'Try again';
      btn.style.background = '#c43030';
      btn.disabled = false;
      setTimeout(() => {
        btn.textContent = defaultText;
        btn.style.background = '';
      }, 2500);
    });
}

['previewLeadForm', 'exitLeadForm'].forEach((id) => {
  const form = document.getElementById(id);
  if (!form) return;
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    handleLead(form);
  });
});

(function () {
  const overlay = document.getElementById('exitPopup');
  const closeBtn = document.getElementById('exitPopupClose');
  if (!overlay || !closeBtn) return;

  function hide() {
    overlay.classList.remove('active');
    overlay.setAttribute('aria-hidden', 'true');
  }

  function canShow() {
    const now = Date.now();
    const engaged = submitCount >= 1 || answered >= 1 || interactionCount >= 4;
    return exitReady &&
      engaged &&
      !emailCaptured &&
      !sessionStorage.getItem(EXIT) &&
      now - pageStartedAt > 30000 &&
      now - (quizSeenAt || pageStartedAt) > 15000 &&
      now - lastInteractionAt > 10000;
  }

  function show() {
    if (!canShow()) return;
    sessionStorage.setItem(EXIT, '1');
    overlay.classList.add('active');
    overlay.setAttribute('aria-hidden', 'false');
    evt('preview_exit_popup_shown');
  }

  document.addEventListener('mouseout', (event) => {
    if (event.clientY < 5 && event.relatedTarget === null) show();
  });
  closeBtn.addEventListener('click', hide);
  overlay.addEventListener('click', (event) => {
    if (event.target === overlay) hide();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') hide();
  });
})();

updateSlots();
__EXTRA__
</script>"""

COUNTDOWN_JS = """
// CIS-DF Mandate Countdown
(function(){const deadline=new Date('2027-01-01T00:00:00').getTime(),d=document.getElementById('cdDays'),h=document.getElementById('cdHrs'),m=document.getElementById('cdMin'),s=document.getElementById('cdSec');if(!d)return;const pad=n=>n<10?'0'+n:n;function tick(){const diff=deadline-Date.now();if(diff<=0){d.textContent='0';h.textContent='00';m.textContent='00';s.textContent='00';return}d.textContent=Math.floor(diff/86400000);h.textContent=pad(Math.floor(diff%86400000/3600000));m.textContent=pad(Math.floor(diff%3600000/60000));s.textContent=pad(Math.floor(diff%60000/1000))}tick();setInterval(tick,1000)})();
"""


def quiz_schema(title: str, code: str, slug: str, cards: list, answers: list) -> str:
    parts = []
    for card, answer in zip(cards, answers):
        opts = option_texts(card)
        if isinstance(answer, list):
            accepted = " | ".join(opts[i] for i in answer)
            wrong = [i for i in range(len(opts)) if i not in answer]
        else:
            accepted = opts[answer]
            wrong = [i for i in range(len(opts)) if i != answer]
        parts.append({
            "@type": "Question",
            "name": question_text(card),
            "acceptedAnswer": {"@type": "Answer", "text": accepted},
            "suggestedAnswer": [{"@type": "Answer", "text": opts[i]} for i in wrong],
        })
    body = {
        "@context": "https://schema.org",
        "@type": "Quiz",
        "name": f"10 Free {title} Preview Questions",
        "description": f"Start page 1 of a 10-question free preview for the {title} practice test.",
        "url": f"https://luckyx.dev/courses/{slug}.html#free-quiz",
        "educationalAlignment": {
            "@type": "AlignmentObject",
            "alignmentType": "assesses",
            "targetName": f"ServiceNow {code} Certification",
        },
        "hasPart": parts,
    }
    return "<!-- Structured Data: Quiz -->\n<script type=\"application/ld+json\">\n" + json.dumps(body, indent=2) + "\n</script>"


def progress_slots(step: int) -> str:
    slots = []
    for idx in range(1, 11):
        if step == 1:
            label = "Live now" if idx <= 5 else "Page 2"
        else:
            label = "Page 1" if idx <= 5 else "Live now"
        slots.append(
            f'      <li class="preview-slot" data-slot="{idx}"><span class="preview-slot-num">{idx}</span><span class="preview-slot-label">{label}</span></li>'
        )
    return "\n".join(slots)


def result_block(total_q: int, udemy: str, step: int, page1_url: str) -> str:
    continue_btn = (
        '      <button type="button" class="preview-secondary-btn" id="previewContinueBtn">Continue to questions 6-10</button>\n'
        if step == 1
        else ""
    )
    email_block = ""
    if step == 2:
        email_block = """
      <div class="preview-email-wrap" id="previewEmailWrap">
        <h3>Want updates before you buy?</h3>
        <p>Get blueprint changes, new question drops, and roadmap tips for this certification.</p>
        <form class="preview-lead-form" id="previewLeadForm" data-source="inline">
          <input type="email" name="email" placeholder="you@email.com" autocomplete="email" required>
          <button type="submit" data-default-text="Email me updates">Email me updates</button>
        </form>
        <p class="preview-lead-note">No spam. Only exam updates, new questions, and roadmap tips.</p>
      </div>"""
    back_link = (
        f'      <a href="{page1_url}#free-quiz" class="preview-text-link" id="previewBackLink" hidden>Go back to page 1 first</a>\n'
        if step == 2
        else ""
    )
    return f"""    <div class="preview-result" id="previewResult">
      <div class="preview-result-kicker">{'Page 1 complete' if step == 1 else 'Free preview complete'}</div>
      <h3 class="preview-result-head">{'Keep going or get the full course' if step == 1 else 'Now decide if you want the full bank'}</h3>
      <div class="preview-score-row">
        <div class="preview-score-value" id="previewScoreValue">0/{5 if step == 1 else 10}</div>
        <div class="preview-score-label" id="previewScoreLabel">{'Page 1 of 2' if step == 1 else '10-question free preview'}</div>
      </div>
      <p class="preview-result-copy" id="previewResultCopy"></p>
      <ul class="preview-offer-list">
        <li><span class="preview-offer-bullet">1</span><span>Get all {total_q} exam-style questions on Udemy.</span></li>
        <li><span class="preview-offer-bullet">2</span><span>Keep the same per-option reasoning and sourced Zurich explanations across the full bank.</span></li>
        <li><span class="preview-offer-bullet">3</span><span>Lifetime access with free future updates.</span></li>
      </ul>
      <div class="preview-actions">
        <a href="{udemy}" target="_blank" rel="noopener" class="cp-cta">Get all {total_q} questions
          <svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
{continue_btn}      </div>
      <p class="preview-helper" id="previewHelper"></p>
{email_block}
      <button type="button" class="preview-text-link" id="previewRetakeBtn">Retake free preview</button>
{back_link}    </div>"""


def quiz_section(title: str, total_q: int, udemy: str, slug: str, step: int, cards_html: list[str]) -> str:
    intro = (
        "Page 1 of 2: questions 1-5. Rich explanations, multiple-choice, and multi-select - just like the real exam."
        if step == 1
        else "Page 2 of 2: questions 6-10. Finish the full free preview, then decide if you want the complete bank."
    )
    note = (
        f"You are seeing the first half of a 10-question preview before the full {total_q}-question course."
        if step == 1
        else "These are the last 5 questions in the free preview. The full course keeps going with the same depth."
    )
    return f"""  <section class="quiz-section" id="free-quiz" data-preview-step="{step}">
    <div class="preview-shell">
      <div class="preview-kicker">10-question free preview</div>
      <h2>10 Free {title} Preview Questions</h2>
      <div class="preview-copy-row">
        <p class="quiz-intro">{intro}</p>
        <p class="preview-step-note">{note}</p>
      </div>
      <ol class="preview-index" id="previewIndex">
{progress_slots(step)}
      </ol>
    </div>
{chr(10).join(cards_html)}
{result_block(total_q, udemy, step, f"/courses/{slug}.html")}
  </section>"""


def exit_popup(title: str, total_q: int, udemy: str) -> str:
    return f"""
<!-- Preview Exit Popup -->
<div class="preview-exit" id="exitPopup" aria-hidden="true">
  <div class="preview-exit-card" role="dialog" aria-modal="true" aria-labelledby="exitPopupTitle">
    <button type="button" class="preview-exit-close" id="exitPopupClose" aria-label="Close popup">&times;</button>
    <div class="preview-exit-kicker">Before you go</div>
    <h3 class="preview-exit-title" id="exitPopupTitle">Get {title} updates and new question drops</h3>
    <p class="preview-exit-copy">I will send blueprint changes, new sample questions, and exam roadmap tips for this cert. Or skip the inbox and get the full {total_q}-question course now.</p>
    <form class="preview-lead-form" id="exitLeadForm" data-source="exit">
      <input type="email" name="email" placeholder="you@email.com" autocomplete="email" required>
      <button type="submit" data-default-text="Send me updates">Send me updates</button>
    </form>
    <p class="preview-lead-note">No spam. Unsubscribe anytime.</p>
    <a href="{udemy}" target="_blank" rel="noopener" class="preview-exit-link">Go straight to the full course on Udemy</a>
  </div>
</div>
<!-- /Preview Exit Popup -->
"""


def page_config(slug: str, title: str, total_q: int, step: int) -> dict:
    return {
        "slug": slug,
        "courseTitle": title,
        "step": step,
        "questionCount": 5,
        "questionStart": 1 if step == 1 else 6,
        "questionEnd": 5 if step == 1 else 10,
        "page1Url": f"/courses/{slug}.html",
        "page2Url": f"/courses/{slug}-preview-2.html",
        "totalPreviewQuestions": 10,
        "totalQuestionCount": total_q,
        "convertKitFormId": "9183962",
    }


def script_block(config: dict, answers: list, countdown: bool) -> str:
    return JS_TEMPLATE.replace("__CONFIG__", json.dumps(config)).replace("__ANSWERS__", json.dumps(answers)).replace("__EXTRA__", COUNTDOWN_JS if countdown else "")


def course_meta(raw: str) -> tuple[str, str, str, int]:
    soup = BeautifulSoup(raw, "html.parser")
    title = soup.select_one(".cp-title").get_text(" ", strip=True)
    code = soup.select_one(".cp-code").get_text(" ", strip=True)
    udemy = soup.select_one("a.cp-cta")["href"]
    score_cta = soup.select_one("#quizScore .cp-cta")
    total_match = re.search(r"Get all (\d+) questions", score_cta.get_text(" ", strip=True)) if score_cta else None
    if not total_match:
        total_match = re.search(r"(\d+) practice questions", raw)
    if not total_match:
        raise ValueError("Could not determine total question count.")
    return title, code, udemy, int(total_match.group(1))


def ensure_source_snapshot(files: list[Path]) -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    for path in files:
        source_path = SOURCE_DIR / path.name
        if source_path.exists():
            continue
        try:
            raw = subprocess.check_output(
                ["git", "show", f"HEAD:{path.relative_to(ROOT).as_posix()}"],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
            )
        except subprocess.CalledProcessError as exc:
            raise ValueError(f"Could not bootstrap source snapshot for {path.name}.") from exc
        if raw.count('class="quiz-card') < 10:
            raise ValueError(f"Source snapshot bootstrap for {path.name} did not contain 10+ quiz cards.")
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
        raise ValueError(f"{source_path.name}: expected at least 10 preview source questions.")
    return raw, list(cards[:5]), list(cards[5:10]), list(answers[:5]), list(answers[5:10]), "cdDays" in raw


def render_page(raw: str, slug: str, title: str, code: str, udemy: str, total_q: int, step: int, cards: list, answers: list, countdown: bool) -> str:
    html_cards = [clone_card(card, idx, (1 if step == 1 else 6) + idx) for idx, card in enumerate(cards)]
    output = normalize_text(raw)
    output = QUIZ_CSS_RE.sub(QUIZ_CSS + "\n", output, count=1)
    output = QUIZ_SECTION_RE.sub(lambda _: quiz_section(title, total_q, udemy, slug, step, html_cards), output, count=1)
    output = POPUP_RE.sub("\n", output)
    if step == 1:
        output = QUIZ_SCHEMA_RE.sub(lambda _: quiz_schema(title, code, slug, cards, answers), output, count=1)
        output = re.sub(r'<meta name="robots" content="[^"]+">', '<meta name="robots" content="index, follow">', output, count=1)
    else:
        output = QUIZ_SCHEMA_RE.sub("<!-- Structured Data: Quiz removed on page 2 preview -->", output, count=1)
        output = re.sub(r"<title>(.*?)</title>", r"<title>\1 | Free Preview Page 2</title>", output, count=1)
        output = re.sub(r'<meta name="description" content="([^"]*)">', lambda m: f'<meta name="description" content="{m.group(1)} Page 2 of the 10-question free preview.">', output, count=1)
        output = re.sub(r'<meta name="robots" content="[^"]+">', '<meta name="robots" content="noindex, follow">', output, count=1)
    insert_at = output.rfind("<script>")
    output = output[:insert_at] + exit_popup(title, total_q, udemy) + output[insert_at:]
    return replace_last_script(output, script_block(page_config(slug, title, total_q, step), answers, countdown))


def validate(path: Path, step: int) -> None:
    raw = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")
    cards = soup.select("#free-quiz .quiz-card")
    if len(cards) != 5:
        raise ValueError(f"{path.name}: expected 5 quiz cards.")
    if len(extract_answers(raw)) != 5:
        raise ValueError(f"{path.name}: expected 5 answers.")
    expected_nums = [f"{n}." for n in range(1, 6)] if step == 1 else [f"{n}." for n in range(6, 11)]
    actual_nums = [card.select_one(".quiz-q-num").get_text(strip=True) for card in cards]
    if actual_nums != expected_nums:
        raise ValueError(f"{path.name}: unexpected quiz numbering {actual_nums}.")
    quiz = soup.select_one("#free-quiz")
    if not quiz or quiz.get("data-preview-step") != str(step):
        raise ValueError(f"{path.name}: preview step marker is incorrect.")
    if step == 1:
        if "Page 1 of 2: questions 1-5." not in raw:
            raise ValueError(f"{path.name}: page 1 intro copy missing.")
    else:
        if "Page 2 of 2: questions 6-10." not in raw:
            raise ValueError(f"{path.name}: page 2 intro copy missing.")
        robots = soup.find("meta", attrs={"name": "robots"})
        canonical = soup.find("link", attrs={"rel": "canonical"})
        expected_canonical = f"https://luckyx.dev/courses/{path.stem[:-10]}.html"
        if not robots or robots.get("content", "").strip().lower() != "noindex, follow":
            raise ValueError(f"{path.name}: preview page is missing noindex, follow.")
        if not canonical or canonical.get("href") != expected_canonical:
            raise ValueError(f"{path.name}: preview canonical is incorrect.")
    if any(marker in raw for marker in MOJIBAKE_MARKERS):
        raise ValueError(f"{path.name}: mojibake remains in output.")


def main() -> None:
    files = sorted(path for path in COURSES_DIR.glob("*.html") if not path.name.endswith("-preview-2.html"))
    if not files:
        raise SystemExit("No course pages found.")
    ensure_source_snapshot(files)
    for path in files:
        raw, cards1, cards2, answers1, answers2, countdown = source_data(path)
        title, code, udemy, total_q = course_meta(raw)
        page1 = render_page(raw, path.stem, title, code, udemy, total_q, 1, cards1, answers1, countdown)
        page2 = render_page(raw, path.stem, title, code, udemy, total_q, 2, cards2, answers2, countdown)
        preview2 = path.with_name(f"{path.stem}-preview-2.html")
        path.write_text(page1, encoding="utf-8", newline="\n")
        preview2.write_text(page2, encoding="utf-8", newline="\n")
        validate(path, 1)
        validate(preview2, 2)
        print(f"Built preview funnel: {path.name} + {preview2.name}")


if __name__ == "__main__":
    main()
