(function () {
  'use strict';

  var campaignKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
  var current = new URLSearchParams(window.location.search);
  var campaign = {};

  campaignKeys.forEach(function (key) {
    var value = current.get(key);
    if (value) campaign[key] = value.slice(0, 100);
  });

  if (Object.keys(campaign).length) {
    sessionStorage.setItem('luckyx_campaign', JSON.stringify(campaign));
  } else {
    try {
      campaign = JSON.parse(sessionStorage.getItem('luckyx_campaign') || '{}');
    } catch (error) {
      campaign = {};
    }
  }

  function pageType() {
    var path = window.location.pathname;
    if (path.indexOf('/courses/') === 0) return 'course';
    if (path.indexOf('/blog/') === 0) return 'blog';
    if (path === '/' || path === '/index.html') return 'home';
    if (path === '/quiz.html') return 'quiz';
    if (path === '/compare.html') return 'compare';
    if (path === '/roadmap.html') return 'roadmap';
    if (path === '/about.html') return 'about';
    return 'other';
  }

  /* An explicit data-track-placement wins. Otherwise the placement comes from where the link sits,
     so every Udemy click says which button sold. */
  function placementFor(link) {
    if (link.dataset.trackPlacement) return link.dataset.trackPlacement;
    if (link.dataset.buyStage) return 'course-' + link.dataset.buyStage;
    if (link.closest('.course-card')) return 'card';
    if (link.closest('.cta-section')) return 'final-cta';
    if (link.closest('.site-footer, .cp-footer')) return 'footer';
    if (link.closest('.hero')) return 'hero';
    if (link.closest('.bp-cta-box, .bp-cta-row')) return 'blog-cta';
    if (link.closest('.bp-article')) return 'blog-inline';
    if (link.closest('.cp-wrap')) return 'course-page';
    return 'other';
  }

  function sendUdemyClick(link) {
    if (typeof window.gtag !== 'function') return;

    var destination;
    try {
      destination = new URL(link.href, window.location.href);
    } catch (error) {
      return;
    }

    if (destination.hostname !== 'udemy.com' && !destination.hostname.endsWith('.udemy.com')) return;

    var parameters = {
      page_path: window.location.pathname,
      page_type: pageType(),
      destination_path: destination.pathname,
      placement: placementFor(link).slice(0, 60),
      has_referral_code: destination.searchParams.has('referralCode') ? 'yes' : 'no'
    };

    /* Course pages describe the quiz state here: cert, answered, score, unlocked. */
    if (typeof window.luckyxClickContext === 'function') {
      try {
        var extra = window.luckyxClickContext() || {};
        Object.keys(extra).forEach(function (key) { parameters[key] = extra[key]; });
      } catch (error) { /* tracking must never break a click */ }
    }

    campaignKeys.forEach(function (key) {
      if (campaign[key]) parameters['session_' + key] = campaign[key];
    });

    window.gtag('event', 'udemy_click', parameters);
  }

  document.addEventListener('click', function (event) {
    var link = event.target.closest && event.target.closest('a[href]');
    if (link) sendUdemyClick(link);
  }, true);
})();
