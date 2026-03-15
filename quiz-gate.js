(function () {
  'use strict';

  var LOCK_KEY     = 'luckyx-email-captured';
  var CK_ENDPOINT  = 'https://app.convertkit.com/forms/9183962/subscriptions';
  var captured     = localStorage.getItem(LOCK_KEY) === '1';

  /* ── Apply 'qg-unlocked' class to <html> early so CSS can suppress email wrap ── */
  if (captured) document.documentElement.classList.add('qg-unlocked');

  /* ── GA4 helper ── */
  function ga4(name, params) {
    try {
      gtag('event', name, Object.assign(
        {},
        (typeof PREVIEW !== 'undefined') ? { course_slug: PREVIEW.slug } : {},
        params || {}
      ));
    } catch (e) {}
  }

  /* ════════════════════════════════════════════════════════════════
     FIX 1 — EMAIL GATE ON "Continue to Q6-10" BUTTON (page 1 only)
     ════════════════════════════════════════════════════════════════ */
  if (typeof PREVIEW !== 'undefined' && PREVIEW.step === 1 && !captured) {
    var origBtn = document.getElementById('previewContinueBtn');
    if (origBtn) {
      /* Clone to strip existing navigation handler (preserves attributes + inner text) */
      var newBtn = origBtn.cloneNode(true);
      origBtn.parentNode.replaceChild(newBtn, origBtn);

      newBtn.addEventListener('click', function () {
        /* Re-check in case another tab captured since page load */
        if (localStorage.getItem(LOCK_KEY) === '1') {
          doNavigate();
          return;
        }
        showModal();
      });
    }
  }

  /* ════════════════════════════════════════════════════════════════
     FIX 2 — GUARANTEE BADGE after hero .cp-cta (all pages)
     ════════════════════════════════════════════════════════════════ */
  (function addGuaranteeBadge() {
    /* Find first .cp-cta NOT inside .preview-result (that's the hero CTA) */
    var allCtas = document.querySelectorAll('a.cp-cta');
    var heroCta = null;
    for (var i = 0; i < allCtas.length; i++) {
      if (!allCtas[i].closest('.preview-result') && !allCtas[i].closest('.preview-exit-card')) {
        heroCta = allCtas[i]; break;
      }
    }
    if (!heroCta) return;
    /* Don't double-inject */
    var next = heroCta.nextElementSibling;
    if (next && next.classList.contains('cp-guarantee')) return;
    var badge = document.createElement('div');
    badge.className = 'cp-guarantee';
    badge.innerHTML =
      '<span class="cp-guarantee-icon">\uD83D\uDEE1\uFE0F</span>' +
      '<span class="cp-guarantee-text">30-day money-back guarantee through Udemy. No questions asked.</span>';
    heroCta.parentNode.insertBefore(badge, heroCta.nextSibling);
  }());

  /* ════════════════════════════════════════════════════════════════
     FIX 4 — ENHANCE FINAL RESULT SECTION (page 2 only)
     Adds "You sampled 10 of N questions" + guarantee note near CTA
     ════════════════════════════════════════════════════════════════ */
  if (typeof PREVIEW !== 'undefined' && PREVIEW.step === 2) {
    var resultBox = document.getElementById('previewResult');
    if (resultBox) {
      /* Enhance if already shown (e.g. page reloaded after completing) */
      if (resultBox.classList.contains('show')) {
        enhanceResultBox(resultBox);
      }
      /* Watch for when result becomes visible */
      if (typeof MutationObserver !== 'undefined') {
        var resObs = new MutationObserver(function () {
          if (resultBox.classList.contains('show')) {
            enhanceResultBox(resultBox);
            resObs.disconnect();
          }
        });
        resObs.observe(resultBox, { attributes: true, attributeFilter: ['class'] });
      }
    }
  }

  function enhanceResultBox(box) {
    if (box.querySelector('.qg-result-note')) return; /* Already enhanced */
    var ctaLink = box.querySelector('a.cp-cta[href*="udemy"]');
    if (!ctaLink) return;

    var qCount = (typeof PREVIEW !== 'undefined') ? PREVIEW.totalQuestionCount : null;

    /* "You just sampled 10 of N questions..." */
    if (qCount) {
      var note = document.createElement('p');
      note.className = 'qg-result-note';
      note.innerHTML =
        'You just sampled <strong>10</strong> of <strong>' + qCount + '</strong> questions. ' +
        'The full course has sourced explanations for every wrong answer across the entire bank.';
      ctaLink.parentNode.insertBefore(note, ctaLink);
    }

    /* Guarantee note after CTA */
    var gNote = document.createElement('p');
    gNote.className = 'qg-guarantee-note';
    gNote.innerHTML = '\uD83D\uDEE1\uFE0F 30-day money-back guarantee through Udemy';
    var refNode = ctaLink.nextSibling;
    /* Skip a #text node if present */
    ctaLink.parentNode.insertBefore(gNote, refNode);
  }

  /* ════════════════════════════════════════════════════════════════
     MODAL IMPLEMENTATION
     ════════════════════════════════════════════════════════════════ */
  function showModal() {
    buildModal();
    var bd = document.getElementById('qgBackdrop');
    if (bd) {
      bd.classList.add('qg-visible');
      var input = document.getElementById('qgEmail');
      if (input) setTimeout(function () { input.focus(); }, 80);
      ga4('quiz_gate_shown');
    }
  }

  function buildModal() {
    if (document.getElementById('qgBackdrop')) return;
    var bd = document.createElement('div');
    bd.id = 'qgBackdrop';
    bd.className = 'qg-backdrop';
    bd.setAttribute('role', 'dialog');
    bd.setAttribute('aria-modal', 'true');
    bd.setAttribute('aria-labelledby', 'qgTitle');
    bd.innerHTML =
      '<div class="qg-modal">' +
        '<button class="qg-close" aria-label="Close">\u2715</button>' +
        '<span class="qg-icon">\uD83D\uDD13</span>' +
        '<h3 class="qg-title" id="qgTitle">Unlock 5 more questions \u2014 free</h3>' +
        '<p class="qg-sub">One email gets you questions\u00a06\u201310 on every ServiceNow cert on this site.</p>' +
        '<form class="qg-form">' +
          '<input class="qg-input" id="qgEmail" type="email" ' +
            'placeholder="you@email.com" autocomplete="email" required />' +
          '<button class="qg-submit" type="submit">Unlock Questions \u2192</button>' +
        '</form>' +
        '<p class="qg-fine">No spam. Unsubscribe anytime.</p>' +
      '</div>';
    document.body.appendChild(bd);

    bd.querySelector('.qg-close').addEventListener('click', function () {
      bd.classList.remove('qg-visible');
    });
    bd.addEventListener('click', function (e) {
      if (e.target === bd) bd.classList.remove('qg-visible');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && bd.classList.contains('qg-visible')) {
        bd.classList.remove('qg-visible');
      }
    });

    bd.querySelector('.qg-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var email = (document.getElementById('qgEmail').value || '').trim();
      if (!email) return;
      var btn = bd.querySelector('.qg-submit');
      btn.textContent = 'Unlocking\u2026';
      btn.disabled = true;
      ga4('quiz_gate_email_submitted', { email: email });

      fetch(CK_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json; charset=utf-8' },
        body: JSON.stringify({ email_address: email })
      })
      .then(function () { doNavigate(); })
      .catch(function () { doNavigate(); }); /* Unlock on network error — intent shown */
    });
  }

  function doNavigate() {
    localStorage.setItem(LOCK_KEY, '1');
    captured = true;
    document.documentElement.classList.add('qg-unlocked');
    ga4('quiz_gate_unlocked');
    ga4('generate_lead', { currency: 'USD', value: 0 });
    /* Replicate original continue-button behavior */
    if (typeof persistPageState === 'function') persistPageState();
    if (typeof evt === 'function') evt('preview_continue', { page_score: typeof score !== 'undefined' ? score : 0 });
    window.location.href = PREVIEW.page2Url + '#free-quiz';
  }

}());
// END QG SYSTEM
