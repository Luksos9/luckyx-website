#!/usr/bin/env python3
"""
Generate 15 real quiz questions per course from CSV files.
Reads CSVs from 'All my 18 Courses live' and produces quiz HTML + JS
for each of the 18 course landing pages.

Features:
- Per-option explanations (Explanation 1-6 columns)
- Collapsible overall explanation toggle
- Multi-select support (checkboxes + submit)
"""

import csv
import os
import re
import json
import random
import html as html_module

# Base paths
BASE = r"C:\Users\lukas\OneDrive\Dokumenty\Lucky X Udemy Business"
CSV_BASE = os.path.join(BASE, "All my 18 Courses live")
HTML_BASE = os.path.join(BASE, "Lucky X Website", "courses")

# Course mapping: html_file -> (csv_folder, quiz_code)
COURSES = {
    "cad.html": ("Pass ServiceNow Certified Application Developer CAD 2026 Mar", "CAD"),
    "cas-pa.html": ("Pass ServiceNow CAS-Performance Analytics PA 2026 March", "CAS-PA"),
    "cis-csm.html": ("Pass ServiceNow CIS Customer Service Management CSM 2026 Mar", "CSM"),
    "cis-data-foundations.html": ("Pass ServiceNow CIS Data Foundations CMDBCSDM Exam 2026 Mar", "DF"),
    "cis-discovery.html": ("Pass ServiceNow CIS-Discovery CIS-DISCO Exam 2026 Mar Zurich", "Discovery"),
    "cis-event-management.html": ("Pass ServiceNow CIS - Event Management CIS-EM Exam 2026 Mar", "EM"),
    "cis-fsm.html": ("Pass ServiceNow CIS Field Service Mgmt FSM Exam 2026 Mar", "FSM"),
    "cis-grc-irm.html": ("Pass ServiceNow CIS Risk and Compliance GRC IRM R&C 2026 Mar", "GRC"),
    "cis-ham.html": ("Pass ServiceNow CIS \u2013 Hardware Asset Management HAM 2026 Mar", "HAM"),
    "cis-hrsd.html": ("Pass ServiceNow CIS-HRSD HR Service Delivery Exam 2026 Mar", "HRSD"),
    "cis-itsm.html": ("Pass Your ServiceNow CIS-ITSM Exam 2026 March", "ITSM"),
    "cis-sam.html": ("Pass ServiceNow CIS - Software Asset Mgmt SAM Exam 2026 Mar", "SAM"),
    "cis-service-mapping.html": ("Pass ServiceNow CIS - Service Mapping SM Exam 2026 March", "SM"),
    "cis-sir.html": ("Pass ServiceNow CIS Security Incident Response SIR 2026 Mar", "SIR"),
    "cis-spm.html": ("Pass ServiceNow CIS Strategic Portfolio Mngment SPM 2026 Mar", "SPM"),
    "cis-tprm.html": ("Pass ServiceNow CIS-Third-Party Risk Management TPRM 2026", "TPRM"),
    "cis-vr.html": ("Pass ServiceNow CIS Vulnerability Response VR Exam 2026 Feb", "VR"),
    "csa.html": ("Pass ServiceNow CSA Certified System Administrator 2026 Mar", "CSA"),
}


def read_all_csvs(folder_path):
    """Read all CSV files from a course folder, return list of question dicts."""
    questions = []
    csv_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.csv')])
    for csv_file in csv_files:
        filepath = os.path.join(folder_path, csv_file)
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    q = row.get('Question', '').strip()
                    if not q or len(q) < 30:
                        continue
                    qtype = row.get('Question Type', 'multiple-choice').strip().lower()

                    # Collect options and their per-option explanations
                    options = []
                    option_explanations = []
                    for i in range(1, 7):
                        opt = row.get(f'Answer Option {i}', '').strip()
                        exp = row.get(f'Explanation {i}', '').strip()
                        if opt:
                            options.append(opt)
                            option_explanations.append(exp)

                    if len(options) < 2:
                        continue

                    # Parse correct answers
                    correct_raw = row.get('Correct Answers', '').strip()
                    if not correct_raw:
                        continue

                    # Correct answers are 1-based in CSV
                    try:
                        correct_indices = [int(x.strip()) for x in correct_raw.split(',')]
                    except ValueError:
                        continue

                    # Convert to 0-based
                    correct_indices = [x - 1 for x in correct_indices]

                    # Validate indices are within range
                    if any(x < 0 or x >= len(options) for x in correct_indices):
                        continue

                    explanation = row.get('Overall Explanation', '').strip()
                    domain = row.get('Domain', '').strip()

                    # Determine actual type based on correct answers count
                    is_multi = len(correct_indices) > 1

                    # Check if this question has any per-option explanations
                    has_per_opt = any(e for e in option_explanations)

                    questions.append({
                        'question': q,
                        'type': 'multi-select' if is_multi else 'multiple-choice',
                        'options': options,
                        'option_explanations': option_explanations,
                        'correct': correct_indices,
                        'explanation': explanation,
                        'domain': domain,
                        'source_file': csv_file,
                        'has_per_opt': has_per_opt,
                    })
        except Exception as e:
            print(f"  Warning: Error reading {csv_file}: {e}")
    return questions


def select_questions(questions, n=15):
    """Select n questions with good spread across domains and question types.
    Prefer questions with per-option explanations for better quality."""
    if len(questions) <= n:
        return questions[:n]

    # Separate by type
    multi = [q for q in questions if q['type'] == 'multi-select']
    single = [q for q in questions if q['type'] == 'multiple-choice']

    # Prefer questions with per-option explanations AND overall explanation
    def quality_score(q):
        score = 0
        if q['has_per_opt']:
            score += 2
        if q['explanation']:
            score += 1
        return score

    # Sort by quality (best first)
    multi.sort(key=quality_score, reverse=True)
    single.sort(key=quality_score, reverse=True)

    # Filter: prefer questions with explanations
    multi_best = [q for q in multi if q['explanation']]
    single_best = [q for q in single if q['explanation']]

    # Target: 3-5 multi-select, rest single
    target_multi = min(max(3, len(multi_best)), 5)
    target_single = n - target_multi

    # If not enough multi-select with explanations, use what we have
    if len(multi_best) < target_multi:
        target_multi = len(multi_best)
        if len(multi) > len(multi_best) and target_multi < 3:
            extra_multi = [q for q in multi if not q['explanation']]
            multi_best.extend(extra_multi[:3 - target_multi])
            target_multi = min(3, len(multi_best))
        target_single = n - target_multi

    selected = []

    # Select multi-select questions, spread across domains
    if target_multi > 0 and multi_best:
        selected.extend(select_by_domain(multi_best, target_multi))

    # Select single questions, spread across domains
    pool = single_best if len(single_best) >= target_single else single
    selected.extend(select_by_domain(pool, target_single))

    # Shuffle to mix types
    random.seed(42)  # Deterministic for reproducibility
    random.shuffle(selected)

    return selected[:n]


def select_by_domain(questions, n):
    """Select n questions spread across domains."""
    if len(questions) <= n:
        return questions[:n]

    # Group by domain
    by_domain = {}
    for q in questions:
        d = q['domain'] or 'Unknown'
        by_domain.setdefault(d, []).append(q)

    # Round-robin from each domain
    selected = []
    domain_keys = list(by_domain.keys())
    random.seed(42)
    random.shuffle(domain_keys)

    # Shuffle within each domain for variety
    for d in domain_keys:
        random.shuffle(by_domain[d])

    idx = 0
    while len(selected) < n:
        d = domain_keys[idx % len(domain_keys)]
        if by_domain[d]:
            selected.append(by_domain[d].pop(0))
        idx += 1
        # Safety: if all domains exhausted
        if all(len(v) == 0 for v in by_domain.values()):
            break

    return selected[:n]


def escape_html(text):
    """Escape HTML special characters. Unescape first to avoid double-encoding."""
    return html_module.escape(html_module.unescape(text), quote=True)


def clean_explanation(text):
    """Clean explanation text for HTML display."""
    if not text:
        return ""

    # Remove surrounding quotes if present
    text = text.strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]

    # Replace escaped quotes
    text = text.replace('""', '"')

    return escape_html(text)


def format_overall_explanation(text):
    """Format overall explanation with paragraph breaks for readability."""
    if not text:
        return ""

    cleaned = clean_explanation(text)
    if not cleaned:
        return ""

    # Split into paragraphs on common patterns
    # Insert breaks before "Why", "Sources:", "Note:", "Key ", section headers
    result = cleaned
    # Add paragraph breaks before common section markers
    for marker in [
        'Why the other options',
        'Why the Others Are Wrong',
        'Why other options',
        'Why this is',
        'Explanation of',
        'Key Takeaway',
        'Memory Tip',
        'Real-World',
        'Sources:',
        'Source:',
        'Note:',
        'Important:',
        'Domain:',
    ]:
        result = result.replace(marker, f'<br><br><strong>{marker}</strong>')

    return result


def generate_quiz_html(questions, quiz_code, total_q_count):
    """Generate the full quiz section HTML + JS for a course."""
    n = len(questions)
    letters = 'ABCDEF'

    # Build answers array for JS
    answers_js = []
    for q in questions:
        if q['type'] == 'multi-select':
            answers_js.append(q['correct'])  # Array of ints
        else:
            answers_js.append(q['correct'][0])  # Single int

    # Build HTML
    lines = []
    lines.append(f'  <section class="quiz-section" id="free-quiz">')
    lines.append(f'    <h2>Try 15 Free {quiz_code} Questions</h2>')
    lines.append(f'    <p class="quiz-intro">Test your knowledge before you buy — including multiple-choice and multi-select, just like the real exam.</p>')

    for i, q in enumerate(questions):
        is_multi = q['type'] == 'multi-select'
        multi_class = ' quiz-multi' if is_multi else ''
        multi_count = len(q['correct']) if is_multi else 0

        lines.append(f'    <div class="quiz-card{multi_class}" id="qcard{i}">')

        # Question text
        q_text = escape_html(q['question'])
        choose_hint = f' <span class="quiz-choose">(choose {multi_count})</span>' if is_multi else ''
        lines.append(f'      <div class="quiz-q"><span class="quiz-q-num">{i+1}.</span>{q_text}{choose_hint}</div>')

        # Options
        lines.append(f'      <ul class="quiz-opts">')
        for j, opt in enumerate(q['options']):
            opt_text = escape_html(opt)
            # Per-option explanation data attribute
            per_exp = ''
            if j < len(q['option_explanations']) and q['option_explanations'][j]:
                per_exp_text = clean_explanation(q['option_explanations'][j])
                per_exp = f' data-exp="{per_exp_text}"'
            lines.append(f'      <li class="quiz-opt" data-idx="{j}" data-q="{i}"{per_exp}><span class="quiz-opt-letter">{letters[j]}</span><span>{opt_text}</span></li>')
        lines.append(f'      </ul>')

        # Submit button for multi-select
        if is_multi:
            lines.append(f'      <button class="quiz-submit-btn" data-q="{i}" style="display:none">Submit Answer</button>')

        # Per-option explanations container (hidden until answered)
        lines.append(f'      <div class="quiz-opt-explains" id="qoptexp{i}" style="display:none"></div>')

        # Overall explanation - collapsible toggle
        exp_text = format_overall_explanation(q['explanation'])
        if exp_text:
            lines.append(f'      <details class="quiz-overall" id="qexp{i}">')
            lines.append(f'        <summary class="quiz-overall-toggle">Show full explanation</summary>')
            lines.append(f'        <div class="quiz-overall-content">{exp_text}</div>')
            lines.append(f'      </details>')
        else:
            lines.append(f'      <details class="quiz-overall" id="qexp{i}" style="display:none">')
            lines.append(f'        <summary class="quiz-overall-toggle">Show full explanation</summary>')
            lines.append(f'        <div class="quiz-overall-content"></div>')
            lines.append(f'      </details>')

        lines.append(f'    </div>')

    # Score section
    lines.append(f'    <div class="quiz-score" id="quizScore">')
    lines.append(f'      <div class="quiz-score-num" id="quizScoreNum">0/{n}</div>')
    lines.append(f'      <div class="quiz-score-label">Sample Quiz Score</div>')
    lines.append(f'      <div class="quiz-score-msg" id="quizScoreMsg"></div>')
    lines.append(f'      <a href="REFERRAL_LINK_PLACEHOLDER" target="_blank" rel="noopener" class="cp-cta">')
    lines.append(f'        Get all {total_q_count} questions')
    lines.append(f'        <svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>')
    lines.append(f'      </a>')
    lines.append(f'    </div>')
    lines.append(f'  </section>')

    quiz_html = '\n'.join(lines)

    # Build JS
    answers_json = json.dumps(answers_js)

    quiz_js = f"""  // Quiz logic
  const answers = {answers_json};
  let answered = 0, score = 0;
  const multiSelections = {{}};

  function showExplanations(qi, isCorrect) {{
    var card = document.getElementById('qcard' + qi);
    var opts = card.querySelectorAll('.quiz-opt');
    var correct = Array.isArray(answers[qi]) ? answers[qi] : [answers[qi]];
    var expContainer = document.getElementById('qoptexp' + qi);
    var html = '';

    opts.forEach(function(opt, j) {{
      var perExp = opt.getAttribute('data-exp');
      var isCorr = correct.indexOf(j) !== -1;

      if (perExp) {{
        var label = isCorr ? '<span class=\"qoe-correct\">Correct</span>' : '<span class=\"qoe-wrong\">Incorrect</span>';
        html += '<div class=\"quiz-opt-exp ' + (isCorr ? 'qoe-is-correct' : 'qoe-is-wrong') + '\">' +
          '<div class=\"qoe-header\">' + label + ' <span class=\"qoe-letter\">' + 'ABCDEF'[j] + '</span></div>' +
          '<div class=\"qoe-text\">' + perExp + '</div></div>';
      }}
    }});

    if (html) {{
      expContainer.innerHTML = html;
      expContainer.style.display = 'block';
    }}

    // Show overall explanation toggle if it has content
    var overall = document.getElementById('qexp' + qi);
    if (overall && overall.querySelector('.quiz-overall-content').innerHTML.trim()) {{
      overall.style.display = 'block';
    }}
  }}

  document.querySelectorAll('.quiz-opt').forEach(function(opt) {{
    opt.addEventListener('click', function() {{
      var qi = parseInt(this.dataset.q);
      var card = document.getElementById('qcard' + qi);
      if (card.dataset.state) return;
      var idx = parseInt(this.dataset.idx);
      var isMulti = Array.isArray(answers[qi]);

      if (isMulti) {{
        // Multi-select: toggle selection
        if (!multiSelections[qi]) multiSelections[qi] = new Set();
        if (multiSelections[qi].has(idx)) {{
          multiSelections[qi].delete(idx);
          this.classList.remove('selected');
        }} else {{
          multiSelections[qi].add(idx);
          this.classList.add('selected');
        }}
        // Show/hide submit button
        var btn = card.querySelector('.quiz-submit-btn');
        btn.style.display = multiSelections[qi].size > 0 ? 'block' : 'none';
      }} else {{
        // Single answer: immediate check
        var isCorrect = idx === answers[qi];
        if (isCorrect) {{ score++; this.classList.add('correct'); card.dataset.state = 'correct'; }}
        else {{ this.classList.add('wrong'); card.dataset.state = 'wrong'; card.querySelectorAll('.quiz-opt')[answers[qi]].classList.add('correct'); }}
        this.classList.add('selected');
        card.querySelectorAll('.quiz-opt').forEach(function(o) {{ o.setAttribute('disabled',''); }});
        showExplanations(qi, isCorrect);
        answered++;
        checkDone();
      }}
    }});
  }});

  document.querySelectorAll('.quiz-submit-btn').forEach(function(btn) {{
    btn.addEventListener('click', function() {{
      var qi = parseInt(this.dataset.q);
      var card = document.getElementById('qcard' + qi);
      if (card.dataset.state) return;
      var selected = Array.from(multiSelections[qi] || []).sort();
      var correct = answers[qi].slice().sort();
      var isCorrect = selected.length === correct.length && selected.every(function(v, i) {{ return v === correct[i]; }});
      var opts = card.querySelectorAll('.quiz-opt');
      if (isCorrect) {{
        score++;
        card.dataset.state = 'correct';
        selected.forEach(function(i) {{ opts[i].classList.add('correct'); }});
      }} else {{
        card.dataset.state = 'wrong';
        selected.forEach(function(i) {{
          if (correct.indexOf(i) === -1) opts[i].classList.add('wrong');
          else opts[i].classList.add('correct');
        }});
        correct.forEach(function(i) {{ opts[i].classList.add('correct'); }});
      }}
      opts.forEach(function(o) {{ o.setAttribute('disabled',''); }});
      this.style.display = 'none';
      showExplanations(qi, isCorrect);
      answered++;
      checkDone();
    }});
  }});

  function checkDone() {{
    if (answered === answers.length) {{
      var el = document.getElementById('quizScore');
      el.classList.add('show');
      document.getElementById('quizScoreNum').textContent = score + '/' + answers.length;
      var msg = score === answers.length ? 'Perfect score! You are well prepared.' : score >= 10 ? 'Good start! The full test covers all exam domains in depth.' : 'The full practice test will help you master every topic.';
      document.getElementById('quizScoreMsg').textContent = msg;
      if (typeof gtag === 'function') gtag('event', 'quiz_complete', {{ quiz_name: '{quiz_code}', quiz_score: score }});
    }}
  }}"""

    return quiz_html, quiz_js


# New CSS to add for per-option explanations and overall toggle
NEW_CSS = """
/* Per-option explanations */
.quiz-opt-explains { margin-top: 12px; display: flex; flex-direction: column; gap: 6px; }
.quiz-opt-exp { padding: 10px 14px; border-radius: 8px; font-size: 0.88rem; line-height: 1.5; }
.qoe-is-correct { background: rgba(46,160,67,0.07); border-left: 3px solid #2ea043; }
.qoe-is-wrong { background: rgba(215,58,73,0.05); border-left: 3px solid #d73a49; }
.qoe-header { font-weight: 600; margin-bottom: 4px; font-size: 0.82rem; }
.qoe-correct { color: #2ea043; }
.qoe-wrong { color: #d73a49; }
.qoe-letter { color: var(--text-dim); margin-left: 4px; font-weight: 500; }
.qoe-text { color: var(--text-dim); }
/* Collapsible overall explanation */
.quiz-overall { display: none; margin-top: 10px; }
.quiz-overall[style*="block"] { display: block; }
.quiz-overall-toggle { cursor: pointer; font-size: 0.88rem; font-weight: 600; color: var(--orange); padding: 8px 0; list-style: none; display: flex; align-items: center; gap: 6px; }
.quiz-overall-toggle::-webkit-details-marker { display: none; }
.quiz-overall-toggle::before { content: ''; display: inline-block; width: 0; height: 0; border-left: 5px solid var(--orange); border-top: 4px solid transparent; border-bottom: 4px solid transparent; transition: transform 0.2s; }
details.quiz-overall[open] .quiz-overall-toggle::before { transform: rotate(90deg); }
.quiz-overall-content { padding: 12px 16px; background: var(--bg-card); border-radius: 8px; font-size: 0.88rem; color: var(--text-dim); line-height: 1.6; border-left: 3px solid var(--orange); margin-top: 6px; }"""


def get_referral_link(html_content):
    """Extract the existing referral link from the course HTML."""
    match = re.search(r'<a href="(https://www\.udemy\.com/course/[^"]*referralCode=[^"]*)"[^>]*class="cp-cta"', html_content)
    if match:
        return match.group(1)
    return None


def get_total_questions(html_content):
    """Extract the total question count from existing HTML."""
    match = re.search(r'Get all (\d+) questions', html_content)
    if match:
        return match.group(1)
    match = re.search(r'full (\d+)-question', html_content)
    if match:
        return match.group(1)
    return "200+"


def process_course(html_file, csv_folder, quiz_code):
    """Process a single course: read CSVs, select questions, generate HTML, update file."""
    csv_path = os.path.join(CSV_BASE, csv_folder)
    html_path = os.path.join(HTML_BASE, html_file)

    if not os.path.exists(csv_path):
        print(f"  ERROR: CSV folder not found: {csv_path}")
        return False

    if not os.path.exists(html_path):
        print(f"  ERROR: HTML file not found: {html_path}")
        return False

    # Read all CSVs
    questions = read_all_csvs(csv_path)
    with_exp = sum(1 for q in questions if q['has_per_opt'])
    print(f"  Found {len(questions)} questions ({sum(1 for q in questions if q['type']=='multi-select')} multi-select, {with_exp} with per-option explanations)")

    if len(questions) < 15:
        print(f"  WARNING: Only {len(questions)} questions available, using all")

    # Select 15 best questions
    selected = select_questions(questions, 15)
    sel_with_exp = sum(1 for q in selected if q['has_per_opt'])
    print(f"  Selected {len(selected)} questions ({sum(1 for q in selected if q['type']=='multi-select')} multi-select, {sel_with_exp} with per-option explanations)")

    # Read existing HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Get referral link and total count from existing HTML
    referral_link = get_referral_link(html_content)
    total_q = get_total_questions(html_content)

    if not referral_link:
        print(f"  WARNING: Could not find referral link in {html_file}")
        return False

    # Generate new quiz HTML + JS
    quiz_html, quiz_js = generate_quiz_html(selected, quiz_code, total_q)
    quiz_html = quiz_html.replace('REFERRAL_LINK_PLACEHOLDER', referral_link)

    # Find and replace the quiz section
    quiz_section_pattern = r'  <section class="quiz-section" id="free-quiz">.*?</section>'
    match = re.search(quiz_section_pattern, html_content, re.DOTALL)
    if not match:
        print(f"  ERROR: Could not find quiz section in {html_file}")
        return False

    html_content = html_content[:match.start()] + quiz_html + html_content[match.end():]

    # Find and replace the quiz JS
    js_pattern = r'  // Quiz logic\n.*?(?=\n\n  // |</script>)'
    match = re.search(js_pattern, html_content, re.DOTALL)
    if not match:
        print(f"  ERROR: Could not find quiz JS in {html_file}")
        return False

    html_content = html_content[:match.start()] + quiz_js + html_content[match.end():]

    # Remove old quiz CSS that we'll replace (.quiz-explain, .quiz-choose, .quiz-submit-btn, etc.)
    # Remove the old .quiz-explain rules (replaced by per-option + toggle)
    old_explain_css = '.quiz-explain { display: none; margin-top: 12px; padding: 12px 16px; background: var(--bg-card); border-radius: 8px; font-size: 0.9rem; color: var(--text-dim); line-height: 1.6; border-left: 3px solid var(--orange); }'
    html_content = html_content.replace(old_explain_css, '')
    old_explain_show = '.quiz-explain.show { display: block; }'
    html_content = html_content.replace(old_explain_show, '')

    # Remove old per-option CSS if we placed it before (from a previous run of this script)
    if '/* Per-option explanations */' in html_content:
        # Remove everything from /* Per-option explanations */ to end of that CSS block
        old_pattern = r'/\* Per-option explanations \*/.*?\.quiz-overall-content \{[^}]+\}'
        html_content = re.sub(old_pattern, '', html_content, flags=re.DOTALL)

    # Insert new CSS (per-option explanations + overall toggle) after quiz-submit-btn rules
    if '.quiz-opt-explains' not in html_content:
        # Find the right place to insert: after .quiz-submit-btn:active
        insert_after = '.quiz-submit-btn:active { transform: scale(0.97); }'
        idx = html_content.find(insert_after)
        if idx != -1:
            insert_pos = idx + len(insert_after)
            html_content = html_content[:insert_pos] + NEW_CSS + html_content[insert_pos:]
        else:
            # Fallback: insert after .quiz-choose
            insert_after2 = '.quiz-choose { font-weight: 400; color: var(--orange); font-size: 0.85rem; margin-left: 4px; }'
            idx2 = html_content.find(insert_after2)
            if idx2 != -1:
                insert_pos2 = idx2 + len(insert_after2)
                html_content = html_content[:insert_pos2] + NEW_CSS + html_content[insert_pos2:]

    # Add multi-select CSS if not already present
    if '.quiz-choose' not in html_content:
        multi_css = """\n.quiz-choose { font-weight: 400; color: var(--orange); font-size: 0.85rem; margin-left: 4px; }
.quiz-submit-btn { margin-top: 12px; padding: 10px 24px; background: var(--orange); color: #fff; border: none; border-radius: 8px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: background 0.15s, transform 0.1s; }
.quiz-submit-btn:hover { background: #c75400; }
.quiz-submit-btn:active { transform: scale(0.97); }"""
        insert_after = '.quiz-score .cp-cta { margin-top: 16px; font-size: 1rem; padding: 12px 32px; display: inline-flex; }'
        idx = html_content.find(insert_after)
        if idx != -1:
            insert_pos = idx + len(insert_after)
            html_content = html_content[:insert_pos] + multi_css + html_content[insert_pos:]

    # Clean up any double blank lines from CSS removal
    while '\n\n\n' in html_content:
        html_content = html_content.replace('\n\n\n', '\n\n')

    # Write updated HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"  OK Updated {html_file}")
    return True


def main():
    print("=" * 60)
    print("Quiz Generator v2 - Per-Option Explanations + Toggle")
    print("=" * 60)

    success = 0
    failed = 0

    for html_file, (csv_folder, quiz_code) in sorted(COURSES.items()):
        print(f"\nProcessing: {html_file} ({quiz_code})")
        if process_course(html_file, csv_folder, quiz_code):
            success += 1
        else:
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Done! {success} succeeded, {failed} failed")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
