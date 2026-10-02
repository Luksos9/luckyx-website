/* Cookie notice for Google Analytics. Pages set analytics_storage to "denied" before the GA tag loads
   (see scripts/add_consent.py). Accepting grants it. The choice is kept in localStorage. */
(function () {
  'use strict';
  var KEY = 'luckyx-consent';

  function read() {
    try { return localStorage.getItem(KEY); } catch (error) { return null; }
  }

  function save(value) {
    try { localStorage.setItem(KEY, value); } catch (error) { /* private mode: the choice lasts for this page only */ }
    if (typeof window.gtag === 'function') {
      window.gtag('consent', 'update', { analytics_storage: value === 'granted' ? 'granted' : 'denied' });
    }
  }

  function injectStyle() {
    if (document.getElementById('lxConsentStyle')) return;
    var style = document.createElement('style');
    style.id = 'lxConsentStyle';
    style.textContent =
      '#lxConsent{position:fixed;left:16px;right:16px;bottom:16px;z-index:3000;max-width:560px;margin:0 auto;padding:14px 16px;' +
      'display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;border-radius:14px;border:1px solid rgba(221,92,12,.35);' +
      'background:var(--bg-raised,#f6f3ee);color:var(--text,#1a1a1a);box-shadow:0 12px 40px rgba(0,0,0,.25);font:14px/1.5 var(--font,system-ui,sans-serif)}' +
      '#lxConsent p{margin:0;flex:1 1 240px}#lxConsent a{color:var(--orange,#dd5c0c);text-decoration:underline}' +
      '#lxConsent button{font:600 13px var(--font,system-ui,sans-serif);padding:9px 16px;border-radius:10px;cursor:pointer;border:1px solid rgba(221,92,12,.45);' +
      'background:transparent;color:var(--orange,#dd5c0c)}#lxConsent button.lx-accept{background:var(--orange,#dd5c0c);color:#fff;border-color:var(--orange,#dd5c0c)}' +
      '#lxConsent button:focus-visible{outline:2px solid var(--orange,#dd5c0c);outline-offset:2px}';
    document.head.appendChild(style);
  }

  function hide() {
    var box = document.getElementById('lxConsent');
    if (box) box.remove();
  }

  function show() {
    if (document.getElementById('lxConsent')) return;
    injectStyle();
    var box = document.createElement('div');
    box.id = 'lxConsent';
    box.setAttribute('role', 'region');
    box.setAttribute('aria-label', 'Cookie notice');
    box.innerHTML =
      '<p>Lucky X uses Google Analytics cookies to see which pages help visitors. No analytics cookies are set unless you accept. ' +
      '<a href="/privacy.html">Privacy policy</a></p>' +
      '<button type="button" class="lx-decline">Decline</button>' +
      '<button type="button" class="lx-accept">Accept</button>';
    box.querySelector('.lx-accept').addEventListener('click', function () { save('granted'); hide(); });
    box.querySelector('.lx-decline').addEventListener('click', function () { save('denied'); hide(); });
    document.body.appendChild(box);
  }

  window.luckyxConsent = { open: show };

  var stored = read();
  if (stored !== 'granted' && stored !== 'denied') {
    if (document.body) show(); else document.addEventListener('DOMContentLoaded', show);
  }
})();
