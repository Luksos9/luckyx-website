#!/usr/bin/env node
/**
 * LEGACY GENERATOR
 *
 * This file still reflects the older placeholder sample-question flow and is
 * not the source of truth for the current 2-step free preview funnel.
 *
 * Do not use this script to regenerate `courses/*.html` preview pages until it
 * is migrated to the current rich-question pipeline.
 */

const fs = require('fs');
const path = require('path');

console.warn('[legacy] generate-course-pages.js does not support the current 2-step preview funnel. Use build_preview_funnel.py instead.');

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

// 5 sample questions per certification for the free quiz preview
const sampleQuestions = {
  DISCO: [
    { q:"What is the primary function of the MID Server in ServiceNow Discovery?", opts:["To store discovered CI data locally","To act as a proxy between the ServiceNow instance and the network","To replace the CMDB","To manage user authentication"], ans:1, explain:"The MID Server acts as a proxy that facilitates communication between a ServiceNow instance and external applications, data sources, or services on the customer's network." },
    { q:"Which Discovery pattern type is used to discover horizontal applications like web servers?", opts:["Top-Down Pattern","Horizontal Pattern","Service Pattern","Network Pattern"], ans:1, explain:"Horizontal patterns discover applications that run on multiple servers, such as web servers, database servers, and application servers." },
    { q:"What protocol does ServiceNow Discovery primarily use to discover Windows servers?", opts:["SSH","SNMP","WMI","HTTP"], ans:2, explain:"Windows Management Instrumentation (WMI) is the primary protocol used for discovering Windows-based servers and their configurations." },
    { q:"In ServiceNow Discovery, what is a 'shazzam' probe used for?", opts:["Port scanning to identify open services","Classifying discovered devices by OS type","Mapping network topology","Testing credential validity"], ans:0, explain:"Shazzam probes perform port scanning to identify which services are running on discovered devices by checking for open ports." },
    { q:"What is the purpose of Identification Rules in Discovery?", opts:["To authenticate against target devices","To determine which CI a discovered device maps to in the CMDB","To schedule discovery runs","To filter out unwanted network traffic"], ans:1, explain:"Identification Rules define the criteria used to match discovered devices to existing Configuration Items (CIs) in the CMDB, preventing duplicate records." }
  ],
  CAD: [
    { q:"Which scripting context runs on the client side in ServiceNow?", opts:["Business Rule","Script Include","Client Script","Scheduled Job"], ans:2, explain:"Client Scripts execute in the user's web browser (client side) and are used to manage form behavior, field validation, and UI interactions." },
    { q:"What is the correct way to get a value from a form field in a Client Script?", opts:["current.field_name","g_form.getValue('field_name')","gr.getValue('field_name')","document.getElementById('field_name')"], ans:1, explain:"g_form.getValue() is the GlideForm API method used in Client Scripts to retrieve field values from the currently displayed form." },
    { q:"Which Business Rule type runs before the database operation?", opts:["Display","Before","After","Async"], ans:1, explain:"'Before' Business Rules execute before the database operation (insert, update, delete), allowing you to modify record values before they are saved." },
    { q:"What is an Application Scope in ServiceNow?", opts:["A user's security role","A logical grouping that restricts script and table access","A type of UI page","A reporting dashboard"], ans:1, explain:"Application Scope provides a namespace that protects application files and data from being modified by other applications, enabling safe multi-app development." },
    { q:"Which object is used to query database records in server-side scripts?", opts:["g_form","GlideRecord","g_user","GlideAjax"], ans:1, explain:"GlideRecord is the server-side JavaScript API used to perform database operations like querying, inserting, updating, and deleting records." }
  ],
  HAM: [
    { q:"What is the primary purpose of the Hardware Asset Management (HAM) application?", opts:["To manage software licenses","To track the lifecycle of physical hardware assets","To configure network devices","To manage employee onboarding"], ans:1, explain:"HAM tracks hardware assets through their complete lifecycle — from procurement through deployment, maintenance, and retirement/disposal." },
    { q:"Which table stores hardware asset records in ServiceNow?", opts:["cmdb_ci_hardware","alm_hardware","ast_hardware","cmdb_hardware"], ans:1, explain:"The alm_hardware table is the primary table that stores hardware asset records in the ServiceNow Asset Management application." },
    { q:"What is a Stockroom in HAM?", opts:["A virtual container for software licenses","A physical or logical location where assets are stored","A type of asset report","A configuration item class"], ans:1, explain:"A Stockroom represents a physical or logical location where hardware assets are stored, such as a warehouse, IT closet, or shipping dock." },
    { q:"What is the purpose of Model Categories in HAM?", opts:["To classify assets by manufacturer","To group models into categories for lifecycle management and reporting","To define warranty terms","To set depreciation rates"], ans:1, explain:"Model Categories group product models into logical categories (e.g., Computer, Printer, Server) to standardize lifecycle processes and enable category-specific reporting." },
    { q:"Which lifecycle stage indicates an asset is actively being used?", opts:["On Order","In Stock","In Use","Retired"], ans:2, explain:"The 'In Use' lifecycle stage indicates that a hardware asset has been deployed and is actively being used by an end user or for a business function." }
  ],
  GRC: [
    { q:"What does GRC stand for in the ServiceNow context?", opts:["General Resource Configuration","Governance, Risk, and Compliance","Global Risk Control","Group Role Compliance"], ans:1, explain:"GRC stands for Governance, Risk, and Compliance — a framework for managing organizational governance, enterprise risk management, and regulatory compliance." },
    { q:"What is a Policy in ServiceNow GRC?", opts:["A firewall rule","A documented set of rules governing organizational behavior","A type of incident","A workflow activity"], ans:1, explain:"A Policy is a formal document that defines rules, standards, or guidelines that an organization must follow to maintain compliance with regulations or internal standards." },
    { q:"What is the purpose of Risk Assessment in GRC?", opts:["To calculate software license costs","To evaluate the likelihood and impact of identified risks","To assign user roles","To schedule system backups"], ans:1, explain:"Risk Assessment evaluates the likelihood of a risk occurring and its potential impact on the organization, helping prioritize risk response strategies." },
    { q:"Which module manages regulatory requirements in GRC?", opts:["Incident Management","Compliance Management","Change Management","Knowledge Management"], ans:1, explain:"Compliance Management handles regulatory requirements, authority documents, citations, and compliance controls to ensure the organization meets regulatory obligations." },
    { q:"What is an Entity in ServiceNow GRC?", opts:["A database table","A business unit, department, or process subject to governance","A type of user role","An API endpoint"], ans:1, explain:"An Entity represents an organizational unit (business unit, department, process, or vendor) that is subject to governance, risk management, and compliance requirements." }
  ],
  EM: [
    { q:"What is the primary purpose of Event Management in ServiceNow?", opts:["To manage calendar events","To process and correlate IT infrastructure events into actionable alerts","To schedule meetings","To track project milestones"], ans:1, explain:"Event Management processes raw events from monitoring tools, correlates them, and creates actionable alerts that can trigger incident creation or notification workflows." },
    { q:"What is the difference between an Event and an Alert?", opts:["They are the same thing","Events are raw data; Alerts are processed, correlated, and actionable","Alerts come before Events","Events are for hardware; Alerts are for software"], ans:1, explain:"Events are raw monitoring data received from external tools. Alerts are created after events are processed, deduplicated, and correlated into meaningful, actionable items." },
    { q:"Which component receives events from external monitoring tools?", opts:["The CMDB","The MID Server","The Service Catalog","The Knowledge Base"], ans:1, explain:"The MID Server receives events from external monitoring tools via connectors and forwards them to the ServiceNow instance for processing." },
    { q:"What is Event Correlation in ServiceNow?", opts:["Linking events to user profiles","Grouping related events together to reduce noise and identify root causes","Sorting events by date","Assigning events to support groups"], ans:1, explain:"Event Correlation groups related events together using correlation rules, reducing alert noise and helping identify the root cause of infrastructure issues." },
    { q:"What is the function of an Alert Management Rule?", opts:["To delete old events","To define automated actions when alerts meet certain conditions","To create new monitoring tools","To manage user passwords"], ans:1, explain:"Alert Management Rules define automated actions (like creating incidents, sending notifications, or running workflows) that execute when alerts match specified conditions." }
  ],
  FSM: [
    { q:"What is a Work Order in Field Service Management?", opts:["A purchase request","A task that assigns field agents to perform on-site work","A knowledge article","A change request"], ans:1, explain:"A Work Order is the primary record in FSM that defines on-site work to be performed, including the task details, location, required skills, and assigned field agent." },
    { q:"What is the purpose of the Dispatch Map in FSM?", opts:["To display network topology","To visually assign and schedule field agents to work orders based on location","To map database tables","To track inventory shipments"], ans:1, explain:"The Dispatch Map provides a visual interface for dispatchers to view work order locations on a map and optimally assign field agents based on proximity, skills, and availability." },
    { q:"What is a Crew in ServiceNow FSM?", opts:["A support group","A team of field agents assigned to work together on tasks","A type of SLA","A reporting dashboard"], ans:1, explain:"A Crew is a group of field service agents who are assigned to work together, useful for tasks that require multiple technicians or specialized team coordination." },
    { q:"Which feature helps optimize travel routes for field agents?", opts:["Service Mapping","Dynamic Scheduling","Knowledge Management","Change Advisory Board"], ans:1, explain:"Dynamic Scheduling automatically optimizes work order assignments and travel routes for field agents based on location, skills, availability, and priority." },
    { q:"What is the purpose of the FSM Mobile Agent?", opts:["To monitor server health","To enable field technicians to view and update work orders from mobile devices","To manage software deployments","To configure network switches"], ans:1, explain:"The FSM Mobile Agent provides field technicians with a mobile interface to access work order details, update task status, capture signatures, and record parts used while on-site." }
  ],
  SIR: [
    { q:"What is a Security Incident in ServiceNow SIR?", opts:["A routine change request","A record tracking a confirmed or suspected security breach or policy violation","A hardware malfunction","A user access request"], ans:1, explain:"A Security Incident is a record that tracks a confirmed or suspected breach of security policy, unauthorized access, or malicious activity requiring investigation and response." },
    { q:"What are Observables in Security Incident Response?", opts:["Dashboard widgets","Artifacts like IP addresses, URLs, or file hashes associated with a security incident","User satisfaction surveys","Performance metrics"], ans:1, explain:"Observables are threat artifacts (IP addresses, domain names, URLs, file hashes, etc.) associated with a security incident that help analysts investigate and correlate threats." },
    { q:"What is a Security Playbook?", opts:["A user manual","An automated workflow that guides analysts through standardized incident response procedures","A backup script","A penetration testing tool"], ans:1, explain:"A Security Playbook is an automated workflow that defines standardized response procedures for specific types of security incidents, ensuring consistent and efficient response." },
    { q:"Which integration helps enrich threat intelligence in SIR?", opts:["LDAP","SIEM Integration","SMTP","JDBC"], ans:1, explain:"SIEM (Security Information and Event Management) integration feeds enriched security event data into ServiceNow SIR, helping analysts correlate events and prioritize threats." },
    { q:"What is the purpose of the Threat Intelligence module?", opts:["To manage IT budgets","To aggregate and analyze threat data from multiple sources for proactive defense","To schedule backups","To manage software licenses"], ans:1, explain:"Threat Intelligence aggregates threat data from multiple sources (feeds, STIX/TAXII, etc.) to help security teams proactively identify, analyze, and respond to emerging threats." }
  ],
  SPM: [
    { q:"What is Demand Management in SPM?", opts:["Managing customer complaints","A process for capturing, evaluating, and prioritizing business requests for IT resources","Managing server capacity","Tracking employee time off"], ans:1, explain:"Demand Management captures business requests (demands) for IT projects or services, enabling leadership to evaluate, score, and prioritize them against available resources and strategic goals." },
    { q:"What is a Project Portfolio in ServiceNow SPM?", opts:["A collection of documents","A grouped set of projects managed together for strategic alignment and resource optimization","A type of report","A software repository"], ans:1, explain:"A Project Portfolio groups related projects together, enabling portfolio managers to view overall health, resource allocation, budget status, and strategic alignment across multiple projects." },
    { q:"What does Resource Management do in SPM?", opts:["Manages physical server resources","Plans and allocates human resources across projects and demands","Manages software licenses","Controls network bandwidth"], ans:1, explain:"Resource Management in SPM provides visibility into resource capacity and allocation across projects, enabling resource managers to plan staffing and resolve resource conflicts." },
    { q:"What is Investment Funding in SPM?", opts:["A personal savings plan","A mechanism to allocate budget across portfolios, programs, and projects","A type of tax form","A procurement process"], ans:1, explain:"Investment Funding allows organizations to define funding sources, allocate budgets to portfolios and projects, and track spending against approved funding levels." },
    { q:"What is the purpose of the Roadmap view in SPM?", opts:["To display network topology","To visualize project timelines, milestones, and dependencies on a Gantt-style chart","To show driving directions","To display server uptime"], ans:1, explain:"The Roadmap provides a visual Gantt-style timeline showing project schedules, key milestones, dependencies, and resource allocation across the portfolio." }
  ],
  VR: [
    { q:"What is a Vulnerability Group in ServiceNow VR?", opts:["A user security role","A collection of related vulnerabilities grouped for efficient management and remediation","A type of firewall rule","A CI category"], ans:1, explain:"Vulnerability Groups aggregate related vulnerabilities together based on shared characteristics, enabling security teams to manage and remediate them more efficiently as a batch." },
    { q:"What is a Remediation Task?", opts:["A change request","An actionable task assigned to resolve identified vulnerabilities","A knowledge article","A service catalog item"], ans:1, explain:"A Remediation Task is created from a vulnerability record and assigned to the appropriate team or individual to fix the identified security vulnerability within a specified timeframe." },
    { q:"What is the purpose of Exception Management in VR?", opts:["To handle code errors","To manage approved exceptions where vulnerabilities are accepted rather than remediated","To process refund requests","To track server downtime"], ans:1, explain:"Exception Management handles cases where vulnerabilities cannot or should not be remediated immediately, providing a formal process to document, approve, and track accepted risk." },
    { q:"How does scanner integration work in VR?", opts:["It scans physical documents","It imports vulnerability scan results from third-party tools into ServiceNow","It scans barcodes","It monitors network traffic"], ans:1, explain:"Scanner integration imports vulnerability scan data from third-party tools (like Qualys, Tenable, Rapid7) into ServiceNow VR, automatically creating and updating vulnerability records." },
    { q:"What is the VR Dashboard used for?", opts:["Managing user profiles","Providing a visual overview of vulnerability status, trends, and remediation progress","Configuring email settings","Designing forms"], ans:1, explain:"The VR Dashboard provides security leaders with a visual overview of the organization's vulnerability posture, including open vulnerabilities, remediation progress, aging trends, and SLA compliance." }
  ],
  CSM: [
    { q:"What is the primary purpose of Customer Service Management (CSM)?", opts:["To manage internal IT tickets","To provide end-to-end customer service from issue to resolution across departments","To handle payroll","To configure firewalls"], ans:1, explain:"CSM connects customer service with other departments (field service, engineering, operations) to resolve complex customer issues end-to-end, not just manage individual tickets." },
    { q:"What is the Agent Workspace in CSM?", opts:["A physical office space","A configurable UI that gives agents a unified view of customer cases and related information","A code editor","A project management board"], ans:1, explain:"Agent Workspace provides customer service agents with a single-pane interface showing case details, customer information, interaction history, and knowledge articles for efficient case resolution." },
    { q:"What is a Customer Account in CSM?", opts:["A user login","A record representing a company or organization that is a customer","A bank account","A social media profile"], ans:1, explain:"A Customer Account represents an external company or organization that is a customer, storing company details, contacts, contracts, assets, and service history." },
    { q:"What is the Customer Portal?", opts:["An admin console","A self-service web interface where customers can submit and track their cases","A VPN gateway","A development tool"], ans:1, explain:"The Customer Portal is a self-service interface where external customers can submit new cases, track existing cases, browse knowledge articles, and manage their account information." },
    { q:"What are Service Contracts in CSM?", opts:["Employment agreements","Agreements defining the level of service and entitlements for a customer","Software licenses","NDAs"], ans:1, explain:"Service Contracts define the terms, entitlements, and service levels agreed upon with a customer, determining what support they are entitled to receive and under what conditions." }
  ],
  DF: [
    { q:"What is the CMDB in ServiceNow?", opts:["Customer Management Database","Configuration Management Database — a repository of IT infrastructure components and their relationships","Change Management Dashboard Board","Compliance Monitoring Data Backup"], ans:1, explain:"The CMDB (Configuration Management Database) is a centralized repository that stores information about IT infrastructure components (CIs) and the relationships between them." },
    { q:"What does CSDM stand for?", opts:["Customer Service Data Model","Common Service Data Model — a standard framework for organizing CMDB data","Configuration System Database Management","Certified System Design Method"], ans:1, explain:"CSDM (Common Service Data Model) is ServiceNow's recommended framework for organizing and structuring data in the CMDB, providing standardized domains and CI classes." },
    { q:"What is the purpose of Identification and Reconciliation?", opts:["To identify users","To prevent duplicate CIs by matching incoming data against existing CMDB records","To reconcile financial accounts","To identify security threats"], ans:1, explain:"Identification and Reconciliation (IRE) uses identification rules to match incoming CI data against existing records, preventing duplicates and ensuring CMDB data accuracy." },
    { q:"What is CMDB Health in ServiceNow?", opts:["Server uptime metrics","A dashboard and scoring system that measures the completeness, compliance, and accuracy of CMDB data","A backup verification tool","A network monitoring feature"], ans:1, explain:"CMDB Health provides dashboards and KPIs that measure data quality dimensions — completeness (required fields filled), compliance (following CSDM standards), and correctness (accurate relationships)." },
    { q:"What is a CI Class in the CMDB?", opts:["A JavaScript class","A categorization that defines the type of configuration item and its attributes","A CSS stylesheet","A user role"], ans:1, explain:"A CI Class defines a specific type of Configuration Item (e.g., Server, Application, Network Gear) along with its unique attributes and relationships within the CMDB hierarchy." }
  ],
  CSA: [
    { q:"What is a UI Policy in ServiceNow?", opts:["A company's branding guidelines","A rule that dynamically changes form field behavior (visibility, mandatory, read-only) without scripting","A network security policy","A data retention policy"], ans:1, explain:"UI Policies dynamically change form behavior — making fields visible/hidden, mandatory/optional, or read-only — based on conditions, without requiring any scripting." },
    { q:"What is the Service Catalog?", opts:["A list of servers","A self-service portal where users can request IT services and products","A hardware inventory","A knowledge base"], ans:1, explain:"The Service Catalog provides a self-service storefront where end users can browse and request IT services, hardware, software, and other offerings through standardized request forms." },
    { q:"What is an Access Control Rule (ACL)?", opts:["A firewall rule","A security rule that controls which users can read, write, create, or delete records","A network routing rule","A password policy"], ans:1, explain:"ACLs define security permissions that control access to tables, fields, and records based on user roles, conditions, and scripts — determining who can see and modify data." },
    { q:"What are Notifications in ServiceNow?", opts:["Browser pop-ups only","Automated emails triggered by events or conditions on records","Push notifications to mobile phones only","System log entries"], ans:1, explain:"Notifications are automated email messages sent when specific conditions are met on records (e.g., incident assigned, change approved), configured with recipients, conditions, and templates." },
    { q:"What is a Knowledge Base?", opts:["A database backup","A structured collection of articles that provide information and solutions to common issues","A type of report","A training program"], ans:1, explain:"A Knowledge Base is an organized collection of articles (solutions, FAQs, how-tos) that help users resolve issues independently, reducing ticket volume and improving self-service." }
  ],
  SM: [
    { q:"What is Service Mapping in ServiceNow?", opts:["Drawing network diagrams manually","An automated process that discovers and maps relationships between IT components that make up a business service","Creating org charts","Mapping customer journeys"], ans:1, explain:"Service Mapping automatically discovers and visualizes all the IT infrastructure components (servers, applications, databases) and their relationships that support a specific business service." },
    { q:"What is a Top-Down Pattern?", opts:["A coding style","A discovery pattern that starts from an entry point and maps all connected components of a service","A management hierarchy","A data sorting algorithm"], ans:1, explain:"Top-Down Patterns start from a known entry point (like a URL or load balancer) and discover all downstream components — application servers, databases, and infrastructure — that comprise the service." },
    { q:"What are Connection Attributes?", opts:["Database connection strings","Properties that define how service components connect to each other (ports, protocols, process names)","User profile fields","Network cable specifications"], ans:1, explain:"Connection Attributes define the characteristics (ports, protocols, process names) used to identify and map connections between service components during the discovery process." },
    { q:"What is Traffic-Based Discovery?", opts:["Monitoring road traffic","Using network traffic data to discover connections between CIs that traditional probes might miss","Analyzing website visitor traffic","Measuring bandwidth usage"], ans:1, explain:"Traffic-Based Discovery analyzes actual network traffic flow data to identify connections between CIs, discovering relationships that traditional probe-based discovery might not detect." },
    { q:"What does Map Reliability indicate?", opts:["Network uptime","A confidence score showing how complete and accurate a service map is","GPS signal strength","Data backup success rate"], ans:1, explain:"Map Reliability is a health score that indicates the completeness and accuracy of a service map, flagging missing components, stale data, or unresolved connection issues." }
  ],
  SAM: [
    { q:"What is the primary goal of Software Asset Management (SAM)?", opts:["Writing software code","Managing software licenses to ensure compliance and optimize costs","Designing user interfaces","Testing software applications"], ans:1, explain:"SAM manages the full software license lifecycle — tracking entitlements, measuring usage, ensuring compliance with vendor agreements, and optimizing license costs to avoid over/under-licensing." },
    { q:"What is a Software Entitlement?", opts:["A user permission","A record representing the rights to use software as defined by a license agreement","A software feature","A warranty document"], ans:1, explain:"A Software Entitlement records the purchased rights to use software, including the license type, quantity, metrics (per user, per device), and terms from the vendor agreement." },
    { q:"What is Software Normalization?", opts:["Code formatting","The process of standardizing software names and publishers from discovery data into a consistent library","Data encryption","File compression"], ans:1, explain:"Software Normalization maps the varied software names found by discovery (e.g., 'MS Office', 'Microsoft Office 365') to standardized publisher and product names in the software library." },
    { q:"What does License Calculation do in SAM?", opts:["Calculates software development time","Compares installed/used software against purchased entitlements to determine compliance position","Calculates server costs","Estimates project timelines"], ans:1, explain:"License Calculation compares the number of software installations or allocations against purchased entitlements, showing whether the organization is compliant, over-licensed, or under-licensed." },
    { q:"What is the SAM Workspace?", opts:["A physical room","A centralized dashboard for managing software assets, compliance status, and optimization opportunities","A code editor","A testing environment"], ans:1, explain:"The SAM Workspace provides a centralized interface with dashboards, reports, and quick actions for software asset managers to monitor compliance, track spending, and identify optimization opportunities." }
  ],
  PA: [
    { q:"What is a Performance Analytics Indicator?", opts:["A KPI widget only","A metric that tracks and measures business performance data over time","A status light on hardware","A code quality metric"], ans:1, explain:"An Indicator (also called a KPI) is a defined metric that collects, tracks, and measures specific business data points over time, enabling trend analysis and performance monitoring." },
    { q:"What is a Breakdown in Performance Analytics?", opts:["A system failure","A dimension used to segment indicator data into meaningful groups (e.g., by priority, category, group)","A debugging tool","A maintenance window"], ans:1, explain:"A Breakdown segments indicator data into sub-groups based on a field (like priority, category, or assignment group), allowing you to analyze which segments drive overall performance." },
    { q:"What is a Scheduled Data Collection?", opts:["A database backup schedule","A job that runs at defined intervals to collect and store indicator scores and breakdown data","A meeting scheduler","A log rotation policy"], ans:1, explain:"Scheduled Data Collections are jobs that run on a defined schedule to collect current scores for indicators and their breakdowns, building the historical data needed for trend analysis." },
    { q:"What is the Analytics Hub?", opts:["A physical data center","A centralized interface for exploring and analyzing all Performance Analytics data and visualizations","A network monitoring tool","A hardware diagnostics center"], ans:1, explain:"The Analytics Hub is a centralized workspace where users can explore all PA indicators, view trends, compare breakdowns, and create ad-hoc analyses without building custom dashboards." },
    { q:"What is an Interactive Filter in PA dashboards?", opts:["An email spam filter","A dashboard control that lets users dynamically filter the data displayed across multiple widgets","A water filtration system","A code linting tool"], ans:1, explain:"Interactive Filters provide dashboard controls that allow users to dynamically filter the data shown across multiple widgets simultaneously, enabling focused analysis on specific criteria." }
  ],
  HRSD: [
    { q:"What is the Employee Center in HRSD?", opts:["A physical office building","A unified portal where employees access HR services, knowledge, and case management","A payroll system","An org chart viewer"], ans:1, explain:"The Employee Center is a unified self-service portal where employees can access HR services, browse knowledge articles, submit HR cases, and manage their personal HR information." },
    { q:"What are Lifecycle Events in HRSD?", opts:["System logs","Automated workflows triggered by employee milestones like onboarding, transfers, or offboarding","Calendar events","Performance reviews"], ans:1, explain:"Lifecycle Events are automated multi-department workflows triggered by key employee milestones (hire, transfer, promotion, leave, offboarding) that coordinate tasks across HR, IT, Facilities, and other departments." },
    { q:"What is HR Case Management?", opts:["A legal tool","A system for employees to submit, track, and resolve HR inquiries and requests","A project management tool","A recruitment platform"], ans:1, explain:"HR Case Management provides a structured system for employees to submit HR inquiries (benefits questions, policy clarifications, complaints) and for HR agents to track and resolve them." },
    { q:"What are Document Templates in HRSD?", opts:["Word processor files","Pre-configured templates that auto-generate HR documents (offer letters, separation notices) with employee data","Email templates only","Form layouts"], ans:1, explain:"Document Templates are pre-configured templates that automatically populate HR documents (offer letters, policy acknowledgments, separation notices) with employee data from ServiceNow records." },
    { q:"What is Enterprise Onboarding in HRSD?", opts:["Server installation","A cross-departmental process that coordinates all tasks needed to onboard a new employee","A software deployment","A training course"], ans:1, explain:"Enterprise Onboarding coordinates tasks across multiple departments (HR, IT, Facilities, Security, Finance) to ensure new employees receive everything they need — equipment, access, workspace, and orientation." }
  ],
  ITSM: [
    { q:"What is Incident Management in ServiceNow?", opts:["Project planning","The process of restoring normal service operation as quickly as possible after an unplanned interruption","Software development","Asset tracking"], ans:1, explain:"Incident Management focuses on restoring normal service operation as quickly as possible after an unplanned interruption or reduction in quality, minimizing business impact." },
    { q:"What is the difference between an Incident and a Problem?", opts:["They are the same","An Incident is an unplanned interruption; a Problem is the underlying root cause of one or more incidents","Incidents are for hardware; Problems are for software","Problems are more urgent than Incidents"], ans:1, explain:"An Incident is an unplanned interruption to a service. A Problem is the unknown root cause of one or more incidents. Problem Management aims to prevent incidents by finding and fixing root causes." },
    { q:"What is a Change Request?", opts:["A feature request from customers","A formal proposal to modify an IT service, system, or infrastructure component","A bug report","A service catalog item"], ans:1, explain:"A Change Request is a formal record proposing a modification to the IT environment (hardware, software, configuration, process), managed through a controlled approval and implementation process." },
    { q:"What are the types of Changes in ITSM?", opts:["Small, Medium, Large","Normal, Standard, Emergency","Critical, High, Medium, Low","Planned, Unplanned"], ans:1, explain:"The three change types are: Normal (requires full assessment and CAB approval), Standard (pre-approved, low-risk, follows a template), and Emergency (urgent, expedited approval for critical fixes)." },
    { q:"What is a Knowledge Article in ITSM?", opts:["A blog post","A documented solution or information that helps resolve issues and reduce ticket volume","A database schema","A training video"], ans:1, explain:"Knowledge Articles document solutions, workarounds, FAQs, and procedures that help both end users (self-service) and support agents resolve issues faster, reducing repeat tickets." }
  ],
  TPRM: [
    { q:"What is Third-Party Risk Management (TPRM)?", opts:["Managing personal investments","A process for assessing and mitigating risks associated with external vendors and partners","Managing team schedules","Configuring third-party software"], ans:1, explain:"TPRM is the process of identifying, assessing, monitoring, and mitigating risks that arise from an organization's relationships with third-party vendors, suppliers, and business partners." },
    { q:"What is Vendor Tiering in TPRM?", opts:["Organizing vendor product shelves","Classifying vendors by risk level to determine the appropriate depth of risk assessment","Ranking vendors by price","Sorting vendors alphabetically"], ans:1, explain:"Vendor Tiering classifies third-party vendors into risk categories (Critical, High, Medium, Low) based on factors like data access, business impact, and regulatory requirements, determining assessment depth." },
    { q:"What is a Risk Assessment in TPRM?", opts:["A financial audit","A structured evaluation of the risks posed by a vendor relationship across multiple risk domains","A penetration test","A vendor product review"], ans:1, explain:"A Risk Assessment is a structured evaluation examining a vendor across risk domains (security, compliance, financial stability, operational resilience) to identify and quantify risks in the relationship." },
    { q:"What is an Engagement in TPRM?", opts:["A marriage proposal","A formal record representing a specific business relationship or contract with a vendor","A customer survey","A marketing campaign"], ans:1, explain:"An Engagement represents a specific business relationship, contract, or project with a third-party vendor, tracking the scope of the relationship and associated risk assessments." },
    { q:"What is Continuous Monitoring in TPRM?", opts:["24/7 server monitoring","Ongoing surveillance of vendor risk indicators to detect changes in risk posture between formal assessments","Continuous Integration","Real-time network monitoring"], ans:1, explain:"Continuous Monitoring tracks vendor risk indicators (security ratings, news, compliance status) on an ongoing basis between formal assessments, enabling early detection of emerging risks." }
  ]
};

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

function generateQuizHtml(course) {
  const questions = sampleQuestions[course.code] || [];
  const letters = ['A','B','C','D'];
  return questions.map((q, i) => {
    const optsHtml = q.opts.map((opt, j) =>
      `      <li class="quiz-opt" data-idx="${j}" data-q="${i}"><span class="quiz-opt-letter">${letters[j]}</span><span>${opt}</span></li>`
    ).join('\n');
    return `    <div class="quiz-card" id="qcard${i}">
      <div class="quiz-q"><span class="quiz-q-num">${i+1}.</span>${q.q}</div>
      <ul class="quiz-opts">
${optsHtml}
      </ul>
      <div class="quiz-explain" id="qexp${i}">${q.explain}</div>
    </div>`;
  }).join('\n');
}

function generateQuizSchema(course) {
  const questions = sampleQuestions[course.code] || [];
  const canonicalUrl = `https://luckyx.dev/courses/${course.slug}.html`;
  const quizItems = questions.map((q, i) => ({
    "@type": "Question",
    "name": q.q,
    "acceptedAnswer": {
      "@type": "Answer",
      "text": q.opts[q.ans]
    },
    "suggestedAnswer": q.opts.filter((_, j) => j !== q.ans).map(opt => ({
      "@type": "Answer",
      "text": opt
    }))
  }));
  return JSON.stringify({
    "@context": "https://schema.org",
    "@type": "Quiz",
    "name": `Free ${course.title} Sample Questions`,
    "description": `Try 5 free sample questions from the ${course.title} practice test`,
    "url": `${canonicalUrl}#free-quiz`,
    "educationalAlignment": {
      "@type": "AlignmentObject",
      "alignmentType": "assesses",
      "targetName": `ServiceNow ${course.code} Certification`
    },
    "hasPart": quizItems
  }, null, 2);
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

<!-- Structured Data: Quiz -->
<script type="application/ld+json">
${generateQuizSchema(course)}
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

/* Quiz section */
.quiz-section { margin-top: 48px; }
.quiz-section h2 { font-size: 1.3rem; font-weight: 600; margin-bottom: 8px; }
.quiz-intro { color: var(--text-dim); font-size: 0.95rem; margin-bottom: 24px; }
.quiz-card { background: var(--bg-raised); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 16px; transition: border-color 0.2s; }
.quiz-card[data-state="correct"] { border-color: #2ea043; }
.quiz-card[data-state="wrong"] { border-color: #d73a49; }
.quiz-q { font-weight: 600; font-size: 1rem; margin-bottom: 16px; line-height: 1.5; }
.quiz-q-num { color: var(--orange); font-weight: 700; margin-right: 6px; }
.quiz-opts { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.quiz-opt { display: flex; align-items: flex-start; gap: 10px; padding: 12px 14px; border-radius: 8px; border: 1px solid var(--border); cursor: pointer; transition: background 0.15s, border-color 0.15s; color: var(--text-dim); font-size: 0.95rem; line-height: 1.5; }
.quiz-opt:hover { background: rgba(221,92,12,0.06); border-color: var(--border-hover); }
.quiz-opt.selected { background: rgba(221,92,12,0.1); border-color: var(--orange); color: var(--text); }
.quiz-opt.correct { background: rgba(46,160,67,0.1); border-color: #2ea043; color: var(--text); }
.quiz-opt.wrong { background: rgba(215,58,73,0.1); border-color: #d73a49; }
.quiz-opt[disabled] { pointer-events: none; }
.quiz-opt-letter { width: 22px; height: 22px; border-radius: 50%; background: var(--bg-card); border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 600; flex-shrink: 0; color: var(--text-dim); }
.quiz-opt.selected .quiz-opt-letter { background: var(--orange); color: #fff; border-color: var(--orange); }
.quiz-opt.correct .quiz-opt-letter { background: #2ea043; color: #fff; border-color: #2ea043; }
.quiz-opt.wrong .quiz-opt-letter { background: #d73a49; color: #fff; border-color: #d73a49; }
.quiz-explain { display: none; margin-top: 12px; padding: 12px 16px; background: var(--bg-card); border-radius: 8px; font-size: 0.9rem; color: var(--text-dim); line-height: 1.6; border-left: 3px solid var(--orange); }
.quiz-explain.show { display: block; }
.quiz-score { margin-top: 24px; padding: 20px; background: var(--bg-raised); border-radius: 12px; border: 1px solid var(--border); text-align: center; display: none; }
.quiz-score.show { display: block; }
.quiz-score-num { font-size: 2rem; font-weight: 800; color: var(--orange); }
.quiz-score-label { color: var(--text-dim); font-size: 0.95rem; margin-top: 4px; }
.quiz-score-msg { margin-top: 12px; font-size: 0.95rem; color: var(--text-dim); }
.quiz-score .cp-cta { margin-top: 16px; font-size: 1rem; padding: 12px 32px; display: inline-flex; }

/* Countdown banner */
.countdown-banner { max-width: 100%; margin: 0 0 24px; padding: 20px 24px; background: linear-gradient(135deg, rgba(221,92,12,0.08), rgba(221,92,12,0.03)); border: 1px solid rgba(221,92,12,0.2); border-radius: 14px; text-align: center; position: relative; overflow: hidden; }
.countdown-banner::before { content: ''; position: absolute; inset: 0; background: linear-gradient(90deg, transparent, rgba(221,92,12,0.04), transparent); animation: cd-shimmer 3s ease-in-out infinite; }
@keyframes cd-shimmer { 0%, 100% { transform: translateX(-100%); } 50% { transform: translateX(100%); } }
.countdown-label { font-size: 0.85rem; font-weight: 600; color: var(--orange); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; position: relative; }
.countdown-headline { font-size: 1.05rem; font-weight: 600; color: var(--text); margin-bottom: 12px; position: relative; line-height: 1.4; }
.countdown-grid { display: flex; justify-content: center; gap: 16px; margin-bottom: 12px; position: relative; }
.countdown-unit { display: flex; flex-direction: column; align-items: center; min-width: 56px; }
.countdown-num { font-size: 1.8rem; font-weight: 800; color: var(--orange); line-height: 1; font-variant-numeric: tabular-nums; }
.countdown-lbl { font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 4px; }
.countdown-sub { font-size: 0.85rem; color: var(--text-dim); position: relative; line-height: 1.5; }

@media (max-width: 600px) {
  .cp-title { font-size: 1.5rem; }
  .cp-price { font-size: 1.5rem; }
  .cp-cta { width: 100%; justify-content: center; }
  .quiz-card { padding: 16px; }
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

  ${course.code === 'DF' ? `<div class="countdown-banner" id="dfCountdown">
    <div class="countdown-label">CIS-Data Foundations Mandate</div>
    <div class="countdown-headline">Starting Jan 1, 2027 — CIS-DF becomes a prerequisite for 7 CIS certifications</div>
    <div class="countdown-grid">
      <div class="countdown-unit"><span class="countdown-num" id="cdDays">---</span><span class="countdown-lbl">Days</span></div>
      <div class="countdown-unit"><span class="countdown-num" id="cdHrs">--</span><span class="countdown-lbl">Hours</span></div>
      <div class="countdown-unit"><span class="countdown-num" id="cdMin">--</span><span class="countdown-lbl">Min</span></div>
      <div class="countdown-unit"><span class="countdown-num" id="cdSec">--</span><span class="countdown-lbl">Sec</span></div>
    </div>
    <div class="countdown-sub">Pass CIS-DF now and get ahead of the deadline.</div>
  </div>` : ''}

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

  <section class="quiz-section" id="free-quiz">
    <h2>Try 5 Free ${course.code} Questions</h2>
    <p class="quiz-intro">Test your knowledge before you buy. These sample questions are from our full ${course.q}-question practice test.</p>
    ${generateQuizHtml(course)}
    <div class="quiz-score" id="quizScore">
      <div class="quiz-score-num" id="quizScoreNum">0/5</div>
      <div class="quiz-score-label">Sample Quiz Score</div>
      <div class="quiz-score-msg" id="quizScoreMsg"></div>
      <a href="${course.ref}" target="_blank" rel="noopener" class="cp-cta">
        Get all ${course.q} questions
        <svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </a>
    </div>
  </section>

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

  // Quiz logic
  const answers = ${JSON.stringify((sampleQuestions[course.code]||[]).map(q=>q.ans))};
  let answered = 0, score = 0;
  document.querySelectorAll('.quiz-opt').forEach(function(opt) {
    opt.addEventListener('click', function() {
      var qi = parseInt(this.dataset.q);
      var idx = parseInt(this.dataset.idx);
      var card = document.getElementById('qcard' + qi);
      if (card.dataset.state) return;
      var isCorrect = idx === answers[qi];
      if (isCorrect) { score++; this.classList.add('correct'); card.dataset.state = 'correct'; }
      else { this.classList.add('wrong'); card.dataset.state = 'wrong'; card.querySelectorAll('.quiz-opt')[answers[qi]].classList.add('correct'); }
      this.classList.add('selected');
      card.querySelectorAll('.quiz-opt').forEach(function(o) { o.setAttribute('disabled',''); });
      document.getElementById('qexp' + qi).classList.add('show');
      answered++;
      if (answered === answers.length) {
        var el = document.getElementById('quizScore');
        el.classList.add('show');
        document.getElementById('quizScoreNum').textContent = score + '/' + answers.length;
        var msg = score === 5 ? 'Perfect score! You are well prepared.' : score >= 3 ? 'Good start! The full test covers all exam domains in depth.' : 'The full practice test will help you master every topic.';
        document.getElementById('quizScoreMsg').textContent = msg;
        if (typeof gtag === 'function') gtag('event', 'quiz_complete', { quiz_name: '${course.code}', quiz_score: score });
      }
    });
  });

  ${course.code === 'DF' ? `// CIS-DF Mandate Countdown
  (function() {
    var deadline = new Date('2027-01-01T00:00:00').getTime();
    var dEl = document.getElementById('cdDays');
    var hEl = document.getElementById('cdHrs');
    var mEl = document.getElementById('cdMin');
    var sEl = document.getElementById('cdSec');
    if (!dEl) return;
    function pad(n) { return n < 10 ? '0' + n : n; }
    function tick() {
      var now = Date.now();
      var diff = deadline - now;
      if (diff <= 0) { dEl.textContent = '0'; hEl.textContent = '00'; mEl.textContent = '00'; sEl.textContent = '00'; return; }
      dEl.textContent = Math.floor(diff / 86400000);
      hEl.textContent = pad(Math.floor((diff % 86400000) / 3600000));
      mEl.textContent = pad(Math.floor((diff % 3600000) / 60000));
      sEl.textContent = pad(Math.floor((diff % 60000) / 1000));
    }
    tick();
    setInterval(tick, 1000);
  })();` : ''}
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
  `  <url>\n    <loc>https://luckyx.dev/</loc>\n    <lastmod>2026-03-12</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>`,
  `  <url>\n    <loc>https://luckyx.dev/quiz.html</loc>\n    <lastmod>2026-03-12</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.9</priority>\n  </url>`,
  `  <url>\n    <loc>https://luckyx.dev/compare.html</loc>\n    <lastmod>2026-03-12</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.9</priority>\n  </url>`
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
