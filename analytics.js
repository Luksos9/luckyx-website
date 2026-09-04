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
    if (window.location.pathname.indexOf('/courses/') === 0) return 'course';
    if (window.location.pathname.indexOf('/blog/') === 0) return 'blog';
    if (window.location.pathname.indexOf('roadmap') !== -1) return 'roadmap';
    if (window.location.pathname.indexOf('quiz') !== -1) return 'quiz';
    return window.location.pathname === '/' || window.location.pathname.endsWith('/index.html') ? 'home' : 'other';
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
      placement: (link.dataset.trackPlacement || link.dataset.buyStage || 'link').slice(0, 60),
      has_referral_code: destination.searchParams.has('referralCode') ? 'yes' : 'no'
    };

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
