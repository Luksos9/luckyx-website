#!/usr/bin/env node
/**
 * Generates individual SEO-optimized course landing pages
 * from the course data. Run: node generate-course-pages.js
 */

const fs = require('fs');
const path = require('path');

const courses = [
  { title:"CIS-Discovery / RISCO", code:"DISCO", slug:"cis-discovery", desc:"Real exam-style questions with full Discovery and RISCO coverage across all domains", longDesc:"Prepare for the ServiceNow CIS-Discovery certification with 113 real exam-style practice questions. Covers all Discovery and RISCO domains including horizontal discovery, service mapping patterns, MID Server configuration, and credential management. Every answer links to official ServiceNow documentation.", rating:4.9, ratings:261, q:113, badge:"best", price:9.99, orig:84.99, track:"infra", ref:"https://www.udemy.com/course/pass-your-servicenow-cis-discovery-exam-vancouver-2023/?referralCode=752D974C366D4DEBE963", keywords:"CIS-Discovery, RISCO, ServiceNow Discovery practice test, CIS-Discovery exam prep, horizontal discovery, MID Server, credential management" },
  { title:"Certified Application Developer", code:"CAD", slug:"cad", desc:"329 questions covering every CAD exam domain with detailed explanations", longDesc:"Master the ServiceNow Certified Application Developer (CAD) exam with 329 practice questions. Covers scripting, UI policies, business rules, client scripts, flow designer, and application scoping. Each question includes sourced explanations linked to official docs.", rating:4.5, ratings:208, q:329, badge:null, price:9.99, orig:84.99, track:"dev", ref:"https://www.udemy.com/course/pass-your-servicenow-cad-exam/?referralCode=CF61F2B36C7F02F40EFB", keywords:"CAD, Certified Application Developer, ServiceNow CAD practice test, CAD exam prep, ServiceNow scripting, business rules, client scripts" },
  { title:"CIS Hardware Asset Mgmt", code:"HAM", slug:"cis-ham", desc:"Full HAM coverage with per-option reasoning for every question", longDesc:"Prepare for the ServiceNow CIS-HAM certification with 249 practice questions covering hardware asset management lifecycle, asset tasks, stockrooms, model categories, and HAM workspace. Every answer option is explained with links to official documentation.", rating:5.0, ratings:1, q:249, badge:"new", price:9.99, orig:84.99, track:"asset", ref:"https://www.udemy.com/course/pass-servicenow-cis-hardware-asset-management-ham/?referralCode=58ECB1F51A94EC5A7F09", keywords:"CIS-HAM, Hardware Asset Management, ServiceNow HAM practice test, HAM exam prep, asset lifecycle, stockroom management" },
  { title:"CIS Risk & Compliance GRC/IRM", code:"GRC", slug:"cis-grc-irm", desc:"500 questions on Entities, Risk, Compliance, and all IRM exam areas", longDesc:"Ace the ServiceNow CIS-Risk and Compliance (GRC/IRM) exam with 500 practice questions. Covers entity management, risk assessment, compliance management, policy lifecycle, audit management, and all IRM exam domains. Sourced explanations for every answer.", rating:4.0, ratings:null, q:500, badge:null, price:9.99, orig:84.99, track:"risk", ref:"https://www.udemy.com/course/pass-servicenow-cis-risk-and-compliance-grc-irm-rc/?referralCode=BAC69ADCBF13729F4018", keywords:"CIS-RC, GRC, IRM, Risk and Compliance, ServiceNow GRC practice test, IRM exam prep, risk assessment, compliance management" },
  { title:"CIS Event Management", code:"EM", slug:"cis-event-management", desc:"Full CIS-EM exam scope including Event Roles and Alert rules", longDesc:"Prepare for the ServiceNow CIS-Event Management exam with 200 practice questions. Covers event rules, alert management, event correlation, connector setup, and operational intelligence. Each answer includes detailed reasoning and official documentation links.", rating:3.8, ratings:1, q:200, badge:"hot", price:9.99, orig:84.99, track:"infra", ref:"https://www.udemy.com/course/pass-servicenow-cis-event-management-cis-em/?referralCode=CA03695C46AF6880DDE1", keywords:"CIS-EM, Event Management, ServiceNow Event Management practice test, CIS-EM exam prep, alert rules, event correlation" },
  { title:"CIS Field Service Mgmt", code:"FSM", slug:"cis-fsm", desc:"334 FSM questions formatted to match actual exam structure", longDesc:"Pass the ServiceNow CIS-Field Service Management exam with 334 practice questions. Covers work order management, dispatch, scheduling, crew operations, and mobile agent. Every question matches the actual exam format with sourced explanations.", rating:4.5, ratings:31, q:334, badge:null, price:9.99, orig:84.99, track:"service", ref:"https://www.udemy.com/course/pass-servicenow-cis-field-service-mangement-fsm/?referralCode=411E2ADCD2ACF3DE5FC7", keywords:"CIS-FSM, Field Service Management, ServiceNow FSM practice test, FSM exam prep, work order management, dispatch scheduling" },
  { title:"CIS Security Incident Response", code:"SIR", slug:"cis-sir", desc:"All SIR exam topics with clear reasoning per answer choice", longDesc:"Prepare for the ServiceNow CIS-Security Incident Response exam with 251 practice questions. Covers security incidents, threat intelligence, observables, SIEM integration, and security playbooks. Clear reasoning for every answer choice with official doc links.", rating:5.0, ratings:17, q:251, badge:null, price:9.99, orig:84.99, track:"security", ref:"https://www.udemy.com/course/pass-servicenow-cis-security-incident-response-sir/?referralCode=FF6F1DFCBBA2F3C7188D", keywords:"CIS-SIR, Security Incident Response, ServiceNow SIR practice test, SIR exam prep, threat intelligence, security playbooks" },
  { title:"CIS Strategic Portfolio Mgmt", code:"SPM", slug:"cis-spm", desc:"Full SPM coverage with exam-realistic question structure", longDesc:"Master the ServiceNow CIS-Strategic Portfolio Management exam with 200 practice questions. Covers demand management, project portfolios, resource management, and investment funding. Exam-realistic question structure with sourced explanations.", rating:5.0, ratings:13, q:200, badge:"high", price:9.99, orig:84.99, track:"service", ref:"https://www.udemy.com/course/pass-your-servicenow-cis-strategic-portfolio-management-spm/?referralCode=D08240CA36DE435A8CD0", keywords:"CIS-SPM, Strategic Portfolio Management, ServiceNow SPM practice test, SPM exam prep, demand management, project portfolios" },
  { title:"CIS Vulnerability Response", code:"VR", slug:"cis-vr", desc:"213 questions across all Vulnerability Response exam domains", longDesc:"Pass the ServiceNow CIS-Vulnerability Response exam with 213 practice questions. Covers vulnerability groups, remediation tasks, exception management, scanner integration, and VR dashboards. Detailed reasoning for every answer with official doc links.", rating:5.0, ratings:20, q:213, badge:null, price:9.99, orig:84.99, track:"security", ref:"https://www.udemy.com/course/pass-your-servicenow-cis-vulnerability-response-vr-exam/?referralCode=EE503A8EA58C23039100", keywords:"CIS-VR, Vulnerability Response, ServiceNow VR practice test, VR exam prep, vulnerability remediation, scanner integration" },
  { title:"CIS Customer Service Mgmt", code:"CSM", slug:"cis-csm", desc:"348 questions on 30+ CSM topics with per-option explanations", longDesc:"Prepare for the ServiceNow CIS-Customer Service Management exam with 348 practice questions covering 30+ CSM topics. Includes case management, agent workspace, customer portal, and service contracts. Per-option explanations with official documentation links.", rating:4.6, ratings:25, q:348, badge:"high", price:9.99, orig:84.99, track:"service", ref:"https://www.udemy.com/course/pass-your-servicenow-cis-customer-service-management-csm/?referralCode=211B4B7795C55DA7281A", keywords:"CIS-CSM, Customer Service Management, ServiceNow CSM practice test, CSM exam prep, case management, agent workspace" },
  { title:"CIS Data Foundations / CSDM", code:"DF", slug:"cis-data-foundations", desc:"470 questions on CMDB, CSDM, and Data Foundations exam areas", longDesc:"Ace the ServiceNow CIS-Data Foundations exam with 470 practice questions. Covers CMDB health, Common Service Data Model (CSDM), identification and reconciliation, service mapping, and data quality. Every answer sourced to official ServiceNow documentation.", rating:4.9, ratings:144, q:470, badge:null, price:9.99, orig:84.99, track:"data", ref:"https://www.udemy.com/course/pass-servicenow-cis-data-foundations-cmdbcsdm/?referralCode=442CA6D450663B1D42AF", keywords:"CIS-DF, Data Foundations, CMDB, CSDM, ServiceNow CMDB practice test, Data Foundations exam prep, CSDM certification" },
  { title:"CSA System Administrator", code:"CSA", slug:"csa", desc:"Full CSA practice test covering all exam objectives", longDesc:"Pass the ServiceNow CSA (Certified System Administrator) exam with 250 comprehensive practice questions. Covers platform overview, user administration, notifications, reporting, service catalog, knowledge management, and all CSA exam domains. Sourced explanations for every answer.", rating:4.5, ratings:2, q:250, badge:null, price:9.99, orig:84.99, track:"core", ref:"https://www.udemy.com/course/pass-your-servicenow-csa-certified-system-administrator/?referralCode=2AE0DFA7BE468BCA8888", keywords:"CSA, Certified System Administrator, ServiceNow CSA practice test, CSA exam prep, system administrator certification, ServiceNow admin" },
  { title:"CIS Service Mapping", code:"SM", slug:"cis-service-mapping", desc:"217 Service Mapping questions with explanation for every choice", longDesc:"Prepare for the ServiceNow CIS-Service Mapping exam with 217 practice questions. Covers service mapping patterns, top-down discovery, connection attributes, traffic-based discovery, and map reliability. Every answer choice explained with official doc links.", rating:4.2, ratings:27, q:217, badge:null, price:9.99, orig:84.99, track:"infra", ref:"https://www.udemy.com/course/pass-servicenow-cis-service-mapping-sm-exam/?referralCode=E4C8DC2D2F2DDEEA86D5", keywords:"CIS-SM, Service Mapping, ServiceNow Service Mapping practice test, SM exam prep, top-down discovery, traffic-based discovery" },
  { title:"CIS Software Asset Mgmt", code:"SAM", slug:"cis-sam", desc:"250 SAM questions aligned to the latest exam blueprint", longDesc:"Pass the ServiceNow CIS-Software Asset Management exam with 250 practice questions aligned to the latest blueprint. Covers software models, entitlements, license calculations, SAM workspace, and normalization. Detailed explanations sourced to official docs.", rating:4.8, ratings:50, q:250, badge:"high", price:9.99, orig:84.99, track:"asset", ref:"https://www.udemy.com/course/pass-your-servicenow-cis-software-asset-mgmt-sam-exam/?referralCode=627AA3E200F1159EDF94", keywords:"CIS-SAM, Software Asset Management, ServiceNow SAM practice test, SAM exam prep, license management, software normalization" },
  { title:"CAS Performance Analytics", code:"PA", slug:"cas-pa", desc:"PA certification prep covering reports, indicators, and dashboards", longDesc:"Master the ServiceNow CAS-Performance Analytics exam with 218 practice questions. Covers indicators, breakdowns, analytics hubs, dashboards, scheduled data collections, and reporting best practices. Each answer includes sourced explanations.", rating:4.0, ratings:1, q:218, badge:null, price:9.99, orig:84.99, track:"dev", ref:"https://www.udemy.com/course/pass-your-servicenow-cas-pa-exam/?referralCode=A8ACE29CC7E537680674", keywords:"CAS-PA, Performance Analytics, ServiceNow PA practice test, PA exam prep, indicators, dashboards, analytics hub" },
  { title:"CIS HR Service Delivery", code:"HRSD", slug:"cis-hrsd", desc:"220 HRSD questions with reasoning for every answer option", longDesc:"Prepare for the ServiceNow CIS-HR Service Delivery exam with 220 practice questions. Covers employee center, lifecycle events, HR case management, document templates, and enterprise onboarding. Reasoning for every answer option with official doc links.", rating:4.0, ratings:10, q:220, badge:"high", price:9.99, orig:84.99, track:"service", ref:"https://www.udemy.com/course/pass-your-servicenow-cis-hrsd-exam/?referralCode=AE0D8C9891F0CAAD71D1", keywords:"CIS-HRSD, HR Service Delivery, ServiceNow HRSD practice test, HRSD exam prep, employee center, lifecycle events" },
  { title:"CIS IT Service Management", code:"ITSM", slug:"cis-itsm", desc:"ITSM practice test with detailed breakdowns per question", longDesc:"Pass the ServiceNow CIS-ITSM exam with 100 practice questions covering incident management, problem management, change management, and all ITSM exam domains. Each question includes a detailed breakdown explaining why each answer option is correct or incorrect.", rating:4.2, ratings:17, q:100, badge:null, price:9.99, orig:84.99, track:"core", ref:"https://www.udemy.com/course/pass-your-servicenow-cis-itsm-exam/?referralCode=3D0B3C1C48CE64275156", keywords:"CIS-ITSM, IT Service Management, ServiceNow ITSM practice test, ITSM exam prep, incident management, change management" },
  { title:"CIS Third-Party Risk Mgmt", code:"TPRM", slug:"cis-tprm", desc:"Full TPRM coverage with 100+ questions and growing", longDesc:"Prepare for the ServiceNow CIS-Third Party Risk Management exam with 100+ practice questions. Covers third-party lifecycle, risk assessments, vendor tiering, engagements, and compliance tracking. Sourced explanations for every answer with official documentation links.", rating:4.5, ratings:null, q:100, badge:"new", price:9.99, orig:84.99, track:"risk", ref:"https://www.udemy.com/course/pass-servicenow-cis-third-party-risk-management-tprm/?referralCode=D6DDF7F1E21D051B5047", keywords:"CIS-TPRM, Third-Party Risk Management, ServiceNow TPRM practice test, TPRM exam prep, vendor risk assessment, third-party lifecycle" },
];

const badgeLabels = { best:'Bestseller', high:'Highest Rated', hot:'Hot & New', new:'New' };

function stars(r) {
  const f = Math.floor(r);
  const h = (r % 1) >= 0.3 ? 1 : 0;
  return '\u2605'.repeat(f) + (h ? '\u2606' : '') + '\u2606'.repeat(5 - f - h);
}

function heroImgPath(code) {
  const key = code === 'GRC' ? 'rc' : code.toLowerCase();
  return `../Course Hero Image/${key}.webp`;
}

function generatePage(course) {
  const pct = Math.round((1 - course.price / course.orig) * 100);
  const ratingStars = stars(course.rating);
  const ratingsText = course.ratings ? `(${course.ratings} reviews)` : '';
  const badgeHtml = course.badge ? `<span class="cp-badge">${badgeLabels[course.badge]}</span>` : '';
  const canonicalUrl = `https://luckyx.dev/courses/${course.slug}.html`;
  const imgPath = heroImgPath(course.code);

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${course.title} Practice Test 2026 | ServiceNow ${course.code} Exam Prep | Lucky X</title>
<meta name="description" content="${course.longDesc}">
<meta name="keywords" content="${course.keywords}, ServiceNow certification 2026, ServiceNow practice test, Lucky X">
<meta name="author" content="Lucky X">
<meta name="robots" content="index, follow">
<link rel="canonical" href="${canonicalUrl}">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:title" content="${course.title} Practice Test 2026 | Lucky X">
<meta property="og:description" content="${course.longDesc.substring(0, 200)}">
<meta property="og:url" content="${canonicalUrl}">
<meta property="og:site_name" content="Lucky X">
<meta property="og:image" content="https://luckyx.dev/og-image.png">
<meta property="og:locale" content="en_US">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${course.title} Practice Test 2026 | Lucky X">
<meta name="twitter:description" content="${course.longDesc.substring(0, 200)}">
<meta name="twitter:image" content="https://luckyx.dev/og-image.png">
<meta name="twitter:creator" content="@luckyxdev">

<!-- Structured Data: Course -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "${course.title} Practice Test 2026",
  "description": "${course.longDesc.replace(/"/g, '\\"')}",
  "url": "${canonicalUrl}",
  "provider": {
    "@type": "Organization",
    "name": "Lucky X",
    "url": "https://luckyx.dev/",
    "sameAs": ["https://www.udemy.com/user/lucky-x/"]
  },
  "creator": {
    "@type": "Organization",
    "name": "Lucky X"
  },
  "educationalLevel": "Professional Certification",
  "teaches": "ServiceNow ${course.code} Certification",
  "numberOfCredits": "${course.q}",
  "hasCourseInstance": {
    "@type": "CourseInstance",
    "courseMode": "online",
    "courseWorkload": "PT${Math.ceil(course.q * 1.5)}M"
  },
  "offers": {
    "@type": "Offer",
    "price": "${course.price.toFixed(2)}",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "${course.ref}",
    "validFrom": "2026-01-01"
  }${course.ratings ? `,
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "${course.rating}",
    "reviewCount": "${course.ratings}",
    "bestRating": "5",
    "worstRating": "1"
  }` : ''}
}
</script>

<!-- Structured Data: BreadcrumbList -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Lucky X", "item": "https://luckyx.dev/" },
    { "@type": "ListItem", "position": 2, "name": "Practice Tests", "item": "https://luckyx.dev/#courses" },
    { "@type": "ListItem", "position": 3, "name": "${course.title} Practice Test", "item": "${canonicalUrl}" }
  ]
}
</script>

<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<meta name="theme-color" content="#eeebe5">

<script>
  (function() {
    var t = localStorage.getItem('luckyx-theme');
    if (t) document.documentElement.setAttribute('data-theme', t);
    else if (window.matchMedia('(prefers-color-scheme: dark)').matches) document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.setAttribute('data-theme', 'light');
  })();
</script>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<!-- GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-BLYHHC76GG"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-BLYHHC76GG');
</script>

<style>
*,*::before,*::after { margin:0; padding:0; box-sizing:border-box; }
:root {
  --orange: #dd5c0c; --orange-bright: #ff8c42; --orange-deep: #8a3a08;
  --bg: #111114; --bg-raised: #18181c; --bg-card: #1c1c21;
  --border: rgba(255,255,255,0.06); --border-hover: rgba(221,92,12,0.35);
  --text: #e0ddd8; --text-dim: #8a8580; --text-faint: #4a4540;
  --star: #dd5c0c; --font: 'Outfit', sans-serif;
  --card-shadow: 0 2px 12px rgba(0,0,0,0.35);
  --grain-opacity: 0.022;
}
[data-theme="light"] {
  --bg: #eeebe5; --bg-raised: #f7f5f1; --bg-card: #f7f5f1;
  --border: rgba(0,0,0,0.08); --border-hover: rgba(221,92,12,0.4);
  --text: #2a2725; --text-dim: #6b6560; --text-faint: #b0aaa3;
  --card-shadow: 0 2px 16px rgba(0,0,0,0.05);
  --grain-opacity: 0.012;
}
html { scroll-behavior: smooth; }
body {
  background: var(--bg); color: var(--text); font-family: var(--font);
  -webkit-font-smoothing: antialiased; line-height: 1.6;
  transition: background-color 0.5s ease, color 0.4s ease;
}
body::after {
  content: ''; position: fixed; inset: 0; pointer-events: none;
  opacity: var(--grain-opacity); z-index: 9999;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
a { color: var(--orange); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Course page layout */
.cp-wrap { max-width: 720px; margin: 0 auto; padding: 40px 24px 80px; }
.cp-back { display: inline-flex; align-items: center; gap: 6px; color: var(--text-dim); font-size: 0.9rem; margin-bottom: 32px; transition: color 0.2s; }
.cp-back:hover { color: var(--orange); text-decoration: none; }
.cp-back svg { width: 16px; height: 16px; stroke: currentColor; stroke-width: 2; fill: none; }

.cp-hero { position: relative; border-radius: 16px; overflow: hidden; margin-bottom: 32px; aspect-ratio: 16/9; background: var(--bg-card); }
.cp-hero-img { width: 100%; height: 100%; object-fit: cover; }
.cp-badge { position: absolute; top: 16px; left: 16px; background: var(--orange); color: #fff; font-size: 0.75rem; font-weight: 600; padding: 4px 12px; border-radius: 20px; letter-spacing: 0.02em; }

.cp-code { display: inline-block; color: var(--orange); font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px; }
.cp-title { font-size: 2rem; font-weight: 700; line-height: 1.2; margin-bottom: 12px; }
.cp-desc { font-size: 1.05rem; color: var(--text-dim); line-height: 1.7; margin-bottom: 24px; }

.cp-meta { display: flex; flex-wrap: wrap; gap: 16px; align-items: center; margin-bottom: 24px; padding: 20px; background: var(--bg-raised); border-radius: 12px; border: 1px solid var(--border); }
.cp-rating { display: flex; align-items: center; gap: 6px; }
.cp-rating-num { font-weight: 700; font-size: 1.1rem; color: var(--orange); }
.cp-rating-stars { color: var(--star); letter-spacing: 2px; }
.cp-rating-count { color: var(--text-dim); font-size: 0.85rem; }
.cp-stat { display: flex; align-items: center; gap: 6px; color: var(--text-dim); font-size: 0.9rem; }
.cp-stat svg { width: 16px; height: 16px; stroke: currentColor; stroke-width: 2; fill: none; }

.cp-price-row { display: flex; align-items: baseline; gap: 12px; margin-bottom: 32px; }
.cp-price { font-size: 2rem; font-weight: 800; color: var(--text); }
.cp-price-was { font-size: 1rem; color: var(--text-faint); text-decoration: line-through; }
.cp-price-off { font-size: 0.85rem; color: var(--orange); font-weight: 600; }

.cp-cta { display: inline-flex; align-items: center; gap: 10px; background: var(--orange); color: #fff; font-family: var(--font); font-size: 1.1rem; font-weight: 600; padding: 16px 40px; border-radius: 12px; border: none; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; text-decoration: none; }
.cp-cta:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(221,92,12,0.3); text-decoration: none; }
.cp-cta svg { width: 20px; height: 20px; stroke: currentColor; stroke-width: 2; fill: none; }

.cp-features { margin-top: 48px; }
.cp-features h2 { font-size: 1.3rem; font-weight: 600; margin-bottom: 20px; }
.cp-feature-list { list-style: none; }
.cp-feature-list li { padding: 12px 0; border-bottom: 1px solid var(--border); display: flex; align-items: flex-start; gap: 12px; color: var(--text-dim); }
.cp-feature-list li svg { width: 20px; height: 20px; stroke: var(--orange); stroke-width: 2; fill: none; flex-shrink: 0; margin-top: 2px; }

.cp-bottom { margin-top: 48px; text-align: center; padding: 40px 24px; background: var(--bg-raised); border-radius: 16px; border: 1px solid var(--border); }
.cp-bottom p { color: var(--text-dim); margin-bottom: 16px; }
.cp-bottom a { color: var(--orange); font-weight: 600; }

/* Footer */
.cp-footer { text-align: center; padding: 32px 24px; color: var(--text-faint); font-size: 0.8rem; }
.cp-footer a { color: var(--text-dim); }

/* Theme toggle */
.theme-toggle-wrap { position: fixed; top: 16px; right: 16px; z-index: 1001; }
.theme-toggle { width: 36px; height: 36px; border-radius: 50%; border: 1px solid var(--border); background: var(--bg-raised); cursor: pointer; display: flex; align-items: center; justify-content: center; }
.theme-toggle svg { width: 18px; height: 18px; stroke: var(--text-dim); stroke-width: 2; fill: none; }

@media (max-width: 600px) {
  .cp-title { font-size: 1.5rem; }
  .cp-price { font-size: 1.5rem; }
  .cp-cta { width: 100%; justify-content: center; }
}
</style>
</head>
<body>

<div class="theme-toggle-wrap">
  <button class="theme-toggle" id="themeToggle" aria-label="Toggle light/dark mode">
    <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
  </button>
</div>

<main class="cp-wrap">

  <a href="/" class="cp-back">
    <svg viewBox="0 0 24 24"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
    Back to all practice tests
  </a>

  <nav aria-label="Breadcrumb">
    <ol style="display:flex;gap:6px;list-style:none;font-size:0.8rem;color:var(--text-faint);margin-bottom:24px;">
      <li><a href="/" style="color:var(--text-dim)">Lucky X</a> &rsaquo;</li>
      <li><a href="/#courses" style="color:var(--text-dim)">Practice Tests</a> &rsaquo;</li>
      <li style="color:var(--text)">${course.title}</li>
    </ol>
  </nav>

  <div class="cp-hero">
    <img class="cp-hero-img" src="${imgPath}" alt="${course.title} - ServiceNow ${course.code} Certification Practice Test" width="640" height="360" loading="eager">
    ${badgeHtml}
  </div>

  <div class="cp-code">${course.code}</div>
  <h1 class="cp-title">${course.title} — ServiceNow Practice Test 2026</h1>
  <p class="cp-desc">${course.longDesc}</p>

  <div class="cp-meta">
    <div class="cp-rating" aria-label="Rating: ${course.rating} out of 5 stars${course.ratings ? ', ' + course.ratings + ' reviews' : ''}">
      <span class="cp-rating-num">${course.rating.toFixed(1)}</span>
      <span class="cp-rating-stars" aria-hidden="true">${ratingStars}</span>
      <span class="cp-rating-count">${ratingsText}</span>
    </div>
    <div class="cp-stat">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
      ${course.q} questions
    </div>
    <div class="cp-stat">
      <svg viewBox="0 0 24 24"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M12 6v6l4 2"/></svg>
      Lifetime access
    </div>
  </div>

  <div class="cp-price-row">
    <span class="cp-price">$${course.price.toFixed(2)}</span>
    <span class="cp-price-was">$${course.orig.toFixed(2)}</span>
    <span class="cp-price-off">${pct}% off</span>
  </div>

  <a href="${course.ref}" target="_blank" rel="noopener" class="cp-cta">
    Start practicing now
    <svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
  </a>

  <div class="cp-features">
    <h2>What's included</h2>
    <ul class="cp-feature-list">
      <li>
        <svg viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/></svg>
        ${course.q} practice questions matching the ${course.code} exam blueprint
      </li>
      <li>
        <svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
        Every answer sourced to official ServiceNow documentation
      </li>
      <li>
        <svg viewBox="0 0 24 24"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
        Per-option explanations — learn why wrong answers are wrong
      </li>
      <li>
        <svg viewBox="0 0 24 24"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
        Updated for the Zurich release and 2026 exam blueprints
      </li>
      <li>
        <svg viewBox="0 0 24 24"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M12 6v6l4 2"/></svg>
        Lifetime access with free updates — no 30-day expiry
      </li>
      <li>
        <svg viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        Written by an author who passed all 18 ServiceNow exams on the first attempt
      </li>
      <li>
        <svg viewBox="0 0 24 24"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
        30-day money-back guarantee through Udemy
      </li>
    </ul>
  </div>

  <div class="cp-bottom">
    <p>Looking for a different certification?</p>
    <a href="/#courses">Browse all 18 practice tests &rarr;</a>
  </div>

</main>

<footer class="cp-footer">
  <p>&copy; 2026 Lucky X &middot; <a href="/">luckyx.dev</a></p>
</footer>

<script>
  const themeToggle = document.getElementById('themeToggle');
  themeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('luckyx-theme', next);
  });
</script>
</body>
</html>`;
}

// Generate all course pages
const outDir = path.join(__dirname, 'courses');
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

courses.forEach(course => {
  const html = generatePage(course);
  const filePath = path.join(outDir, `${course.slug}.html`);
  fs.writeFileSync(filePath, html, 'utf8');
  console.log(`Generated: courses/${course.slug}.html`);
});

// Generate sitemap
const sitemapEntries = [
  `  <url>\n    <loc>https://luckyx.dev/</loc>\n    <lastmod>2026-03-11</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>`
];

courses.forEach(course => {
  sitemapEntries.push(`  <url>\n    <loc>https://luckyx.dev/courses/${course.slug}.html</loc>\n    <lastmod>2026-03-11</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>`);
});

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapEntries.join('\n')}
</urlset>
`;

fs.writeFileSync(path.join(__dirname, 'sitemap.xml'), sitemap, 'utf8');
console.log('Generated: sitemap.xml');

console.log(`\nDone! Generated ${courses.length} course pages + sitemap.`);
