# The Canonical Software Development Lifecycle: Phases, Steps, and Artifacts — A Senior Architect's Reference

**Audience:** Senior software architects, process engineers, quality and compliance leads.
**Scope:** Every canonical SDLC phase, every granular step, every standard artifact, mapped across Waterfall, V-Model, Iterative, Spiral, Scrum, Kanban, SAFe, DevOps/CD, and regulated SDLCs (FDA GPSV / 21 CFR Part 11, IEC 62304, DO-178C, ISO 26262).
**Primary normative basis:** ISO/IEC/IEEE 12207:2017; ISO/IEC/IEEE 15288:2015; ISO/IEC/IEEE 29148:2018; IEEE Std 1016-2009; IEEE Std 829-2008 (superseded by ISO/IEC/IEEE 29119); SWEBOK v3 (2014) and v4 (2024); PMBOK Guide 7th Ed.; NIST SP 800-218 (SSDF v1.1); NIST SP 800-160 Vol. 1 (replacing the withdrawn SP 800-64 Rev. 2); the Scrum Guide (Nov. 2020); SAFe 6.0; DORA / Accelerate; FDA "General Principles of Software Validation" v2.0 (2002); IEC 62304:2006/A1:2015; RTCA DO-178C (2011); ISO 26262:2018; OWASP SAMM v2; BSIMM.

---

## 0. Phase-Flow Overview

```
                    CROSS-CUTTING (active across ALL phases)
   ┌──────────────────────────────────────────────────────────────────────┐
   │ Project Mgmt │ Risk Mgmt │ Configuration Mgmt │ Quality Assurance    │
   │ Security (SSDF / SAMM) │ Compliance & Audit │ Documentation Mgmt    │
   │ Measurement (DORA / 12207 §6.3.7) │ Supplier / SOUP Management      │
   └──────────────────────────────────────────────────────────────────────┘
                                  ▲   ▲   ▲   ▲   ▲   ▲   ▲   ▲
                                  │   │   │   │   │   │   │   │
   ┌──────┐  ┌────────────┐  ┌──────────┐  ┌──────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────────┐  ┌────────────────┐
   │ 1.   │→│ 2.         │→ │ 3.        │→ │ 4.            │→ │ 5.              │→ │ 6.              │→ │ 7.                  │→ │ 8.             │
   │ INIT │  │ REQUIRE-   │  │ ARCHI-   │  │ IMPLEMEN-     │  │ VERIFICATION &  │  │ RELEASE &       │  │ OPERATIONS &        │  │ RETIREMENT /   │
   │ CONCEPT│ │ MENTS      │  │ TECTURE   │  │ TATION /     │  │ VALIDATION      │  │ DEPLOYMENT      │  │ MAINTENANCE         │  │ DECOMMISSIONING│
   │      │  │            │  │ & DESIGN  │  │ CONSTRUCTION │  │                 │  │                 │  │                     │  │                │
   └──┬───┘  └─────┬──────┘  └────┬─────┘  └──────┬───────┘  └────────┬────────┘  └────────┬────────┘  └─────────┬───────────┘  └───────┬────────┘
      │           │              │               │                    │                    │                     │                       │
      └───────────┴──────────────┴───────────────┴────────────────────┴────────────────────┴─────────────────────┘                       │
                                            FEEDBACK LOOPS (defects, change requests, incidents, RFCs)                                     │
                                                                                                                                            │
      Iterative / Spiral / Agile / DevOps: phases 2–7 cycle continuously; CD collapses 6 into a pipeline.◄──────────────────────────────────┘
      V-Model: phase 5 is mirrored across 2/3/4 (Acceptance ↔ Reqs; System Test ↔ Arch; Integration Test ↔ HLD; Unit Test ↔ LLD).
      Waterfall: strictly sequential; backflow only via formal change control.
```

The phase taxonomy above aligns with the five-phase NIST SDLC originally codified in SP 800-64 Rev. 2 (Initiation → Development/Acquisition → Implementation/Assessment → Operations & Maintenance → Disposal; the publication was withdrawn in May 2019 and superseded by SP 800-160 Vol. 1) and with the eight technical processes of ISO/IEC/IEEE 12207:2017 (Business or Mission Analysis, Stakeholder Needs and Requirements Definition, System/Software Requirements Definition, Architecture Definition, Design Definition, System Analysis, Implementation, Integration, Verification, Transition, Validation, Operation, Maintenance, Disposal).

## 0.1 SDLC Model Comparison Matrix

| Canonical Phase | Waterfall (Royce 1970; DoD-STD-2167A legacy) | V-Model (IABG; STANAG 4159) | Iterative/Incremental (12207 §A.2) | Spiral (Boehm 1988) | Scrum (Scrum Guide 2020) | Kanban (Anderson 2010) | SAFe 6.0 | DevOps / CD (Accelerate; Humble & Farley 2010) |
|---|---|---|---|---|---|---|---|---|
| **1. Initiation/Conception** | Discrete "Concept" phase; charter signed before reqs. | Same as Waterfall; left tip of V. | Front-loaded once per program; per-iteration mini-charters. | Quadrant 1: "Determine objectives, alternatives, constraints" each cycle. | Implicit; precedes Sprint 0. Product Goal established (Scrum Guide, "Commitments"). | Implicit; replaced by service-level expectations and class-of-service definitions. | Strategic Themes, Portfolio Vision, Lean Business Case at Portfolio level (SAFe LPM). | Continuous; lightweight charter, value-stream mapping; "you build it, you run it" charter (DORA/Accelerate Ch. 3). |
| **2. Requirements** | Frozen baseline; SRS produced once per IEEE 830/29148. | Identical to Waterfall; mirrored by Acceptance Test design on right arm. | Re-elaborated each increment. | Quadrant 2 risk-driven elaboration. | Product Backlog (emergent, ordered) + acceptance criteria per PBI; Definition of Ready common practice (not in Scrum Guide). | Replenishment from upstream queue; WIP-limited. | Epics → Capabilities → Features → Stories hierarchy; Benefits Hypothesis on each. | "Shift-left" reqs as code (BDD, executable specs); SSDF PO.1 security reqs. |
| **3. Architecture & Design** | Big Design Up Front (BDUF); HLD + LLD baselined. | Same as Waterfall, paired with Integration/System Test. | Architecture evolves per increment. | Quadrant 3 prototype-driven. | "Just enough" emergent design; ADRs increasingly common. | Design embedded in card lifecycle. | Intentional Architecture + Architectural Runway; Enabler Epics/Features (SAFe "Agile Architecture"). | Architecture as code (IaC); ADRs; threat modeling per SSDF PW.1. |
| **4. Implementation/Construction** | Single coding phase post-design. | Single coding phase. | Per-increment construction. | Spiral arms; iterative coding within each cycle. | Sprint executes; Increment must meet Definition of Done. | Continuous flow; pull-based. | Iterations within a Program Increment (PI) of 8–12 weeks. | Trunk-based development; CI; SBOM generation per CISA/NTIA. |
| **5. Verification & Validation** | Single test phase after coding. | Right arm of V: Unit ↔ LLD, Integration ↔ HLD, System ↔ Reqs, Acceptance ↔ User Needs. | Per-increment V&V. | Quadrant 4 risk-driven verification. | Done = potentially releasable Increment; testing inside Sprint. | Testing inline per pull. | System Demo each iteration; Solution Demo each PI; Inspect & Adapt. | Automated test pyramid + DAST/SAST in pipeline; gated by DORA quality bars. |
| **6. Release & Deployment** | Single big-bang release. | Single release after Acceptance Test. | Periodic releases per increment. | Final spiral arm. | Increment may be released any time during Sprint. | Continuous delivery to stakeholder. | Release on Demand decoupled from PI cadence. | Continuous Deployment; canary/blue-green; release == automated pipeline (DORA Deployment Frequency metric). |
| **7. Operations & Maintenance** | Long tail; corrective/adaptive/perfective/preventive (12207 §6.4.14, ISO/IEC 14764). | Same as Waterfall. | Same plus per-increment maintenance windows. | Ongoing cycles. | Out-of-scope for Scrum Guide; handled by Scrum Team if "you build it, you run it." | Same model as construction; one flow. | DevOps loop within ART; SRE practices. | SRE: SLOs, error budgets, on-call, incident management; runbooks living. |
| **8. Retirement / Decommissioning** | Explicit phase; data archival. | Explicit phase. | Explicit phase. | Explicit phase. | Not addressed in Scrum Guide. | Not addressed. | Lean Portfolio decision; Epic retirement. | Service decommissioning runbook; data destruction certificate. |

Sources per row: Royce, "Managing the Development of Large Software Systems" (1970); ISO/IEC/IEEE 12207:2017 §6; Boehm, "A Spiral Model of Software Development and Enhancement," IEEE Computer 1988; Scrum Guide (Nov. 2020); SAFe 6.0 (scaledagileframework.com); Humble & Farley, *Continuous Delivery* (2010); Forsgren, Humble & Kim, *Accelerate* (2018) and DORA reports 2018-2024.

---

## 1. Phase 1 — Initiation / Conception

### 1.0 Phase Summary
- **Purpose [HIGH]:** Establish business justification, scope, stakeholders, and authority to expend resources. Corresponds to ISO/IEC/IEEE 12207:2017 §6.4.1 *Business or Mission Analysis* and §6.4.2 *Stakeholder Needs and Requirements Definition* (early portion).
- **Typical effort share [MODERATE]:** 3–8 % of total project effort (PMI benchmarks; varies with portfolio governance).
- **Key stakeholders:** Sponsor, business owner, program/portfolio manager, enterprise architect, security officer, compliance lead.
- **Entry criteria:** Strategic objective or unmet need identified; portfolio or product council intake.
- **Exit criteria:** Approved Project Charter (or equivalent funding decision) and a baselined Vision/Scope or Lean Business Case.
- **Primary deliverables:** Project Charter, Business Case, Vision/Scope, Statement of Work (procurement context), preliminary Risk Register, preliminary Stakeholder Register.

### 1.1 Step — Identify Business Need / Opportunity
- **Purpose:** Frame the problem and quantify expected value.
- **Inputs:** Strategic plan, market analysis, enterprise risk register.
- **Activities:** Stakeholder interviews; problem statement; opportunity analysis; high-level options assessment.
- **Outputs:** Opportunity Brief / Concept Paper [MODERATE]; preliminary Problem Statement [MODERATE].
- **Owner:** Business sponsor (R/A); enterprise architect (C); product manager (R).
- **Exit:** Sponsor signs Concept Paper.

### 1.2 Step — Develop Business Case
- **Purpose:** Establish economic, strategic, and risk justification.
- **Inputs:** Opportunity Brief; cost/benefit data; competitive analysis.
- **Activities:** NPV/IRR analysis, ROI modeling, sensitivity analysis, alignment to strategic themes.
- **Outputs:** **Business Case** [HIGH] (PMBOK 7th Ed. *Business Documents*); for SAFe — **Lean Business Case** at Portfolio level (SAFe Epic guidance).
- **Owner:** Sponsor / portfolio analyst.
- **Exit:** Investment decision recorded.

### 1.3 Step — Authorize Project (Charter)
- **Purpose:** Formally authorize project, name PM/owner, allocate funding.
- **Inputs:** Business Case.
- **Activities:** Charter drafting; signature workflow.
- **Outputs:** **Project Charter** [HIGH] (PMBOK Guide 7th Ed.; PMI defines as the document issued by initiator/sponsor that formally authorizes the project and provides PM authority).
- **Owner:** Sponsor (A); PM (R).
- **Exit:** Charter signed; PM appointed.

### 1.4 Step — Define Vision & Scope
- **Purpose:** Articulate product/system vision and bounding scope.
- **Inputs:** Charter; Business Case.
- **Activities:** Vision statement (Moore "elevator pitch" form); in/out-of-scope lists; success measures.
- **Outputs:** **Vision/Scope Document** [MODERATE] (Wiegers, *Software Requirements*, 3rd Ed.); Product Vision (SAFe); Product Goal (Scrum Guide 2020 — "long-term objective for the Scrum Team").
- **Owner:** Product manager / Product Owner.
- **Exit:** Vision baselined; published to stakeholders.

### 1.5 Step — Procurement Definition (when applicable)
- **Purpose:** Define what will be acquired vs. built.
- **Inputs:** Charter, Vision/Scope.
- **Activities:** Make/buy analysis; supplier identification; acquisition planning per ISO/IEC/IEEE 12207:2017 §6.1.1 *Acquisition Process*.
- **Outputs:** **Statement of Work (SOW)** [HIGH, CONDITIONAL: procurement] (FAR Part 37 reference; PMBOK); Request for Proposal (RFP); Acquisition Plan.
- **Owner:** Contracting officer / procurement lead.
- **Exit:** SOW approved.

### 1.6 Step — Initial Risk and Stakeholder Identification
- **Purpose:** Establish baseline risk and stakeholder posture.
- **Inputs:** Charter, Vision/Scope.
- **Activities:** Stakeholder analysis (power/interest); preliminary risk identification.
- **Outputs:** **Stakeholder Register** [HIGH] (PMBOK); preliminary **Risk Register** [HIGH] (PMBOK; ISO 31000); preliminary Communications Plan.
- **Owner:** PM (R/A).
- **Exit:** Registers reviewed by sponsor.

### 1.7 Step — Regulated/Safety Project Initiation [CONDITIONAL: regulated]
- **Purpose:** Establish regulatory framing.
- **Activities:** Determine applicability of FDA QSR, IEC 62304 safety class (A/B/C — IEC 62304:2006 §4.3), DO-178C Design Assurance Level (A–E — DO-178C §2.2.2), ISO 26262 ASIL classification.
- **Outputs:** **Regulatory Strategy** [CONDITIONAL]; **Safety Classification Record** (IEC 62304 §4.3) [CONDITIONAL]; preliminary **Plan for Software Aspects of Certification (PSAC)** [CONDITIONAL: DO-178C §11.1].

### 1.Z Phase 1 Artifact Catalog

| Artifact (aliases) | Purpose | Format | Author Role | Audience | Lifecycle | Confidence | Citation |
|---|---|---|---|---|---|---|---|
| Project Charter | Authorize project; assign PM | Document, 2–10 pp | Sponsor / PM | Sponsor, exec, team | Baselined | [HIGH] | PMBOK 7th Ed., *Project Charter* |
| Business Case | Economic justification | Document + financial model | Sponsor / business analyst | Steering committee | Baselined; revisited at gates | [HIGH] | PMBOK 7th Ed.; ISO 12207:2017 §6.4.1 |
| Lean Business Case (SAFe alias) | Lightweight Epic-level case | Slide / page | Epic Owner | LPM / Portfolio | Living during Epic | [VARIES: SAFe] | SAFe 6.0 Epic guidance |
| Statement of Work (SOW) | Procurement bounding | Contract document | Contracting officer | Supplier, legal | Baselined | [HIGH, CONDITIONAL: procurement] | FAR Part 37; PMBOK |
| Vision / Scope Document | Product framing | Document / wiki | Product manager | All stakeholders | Living | [MODERATE] | Wiegers 3rd Ed. Ch. 5 |
| Product Vision (SAFe) | Aligns ART | Slide / wiki | Product Mgmt | ART, Business Owners | Living | [VARIES: SAFe] | SAFe 6.0 Vision |
| Product Goal (Scrum) | Long-term Scrum objective | One sentence | Product Owner | Scrum Team | Living | [VARIES: Scrum] | Scrum Guide 2020, "Commitments" |
| Stakeholder Register | Identifies all interested parties | Table | PM | PM, sponsor | Living | [HIGH] | PMBOK 7th Ed. |
| Risk Register (initial) | Tracks identified risks | Table / tool | PM / risk lead | All | Living | [HIGH] | PMBOK; ISO 31000:2018 |
| Plan for Software Aspects of Certification (PSAC) | Cert authority agreement plan | Document | Cert lead | FAA/EASA cert authority | Baselined; revised | [CONDITIONAL: DO-178C §11.1] | DO-178C §11.1, §9 |
| Safety Classification Record | Assigns Class A/B/C | Memo / matrix | Safety lead | Regulator, dev team | Baselined | [CONDITIONAL: IEC 62304 §4.3] | IEC 62304:2006 §4.3 |

---

## 2. Phase 2 — Requirements

### 2.0 Phase Summary
- **Purpose [HIGH]:** Elicit, analyze, specify, validate, and manage requirements. Aligns with ISO/IEC/IEEE 29148:2018 *Life cycle processes — Requirements engineering* and ISO/IEC/IEEE 12207:2017 §6.4.2/§6.4.3.
- **Typical effort share [MODERATE]:** 10–20 % (BDUF); decomposed and continuous in Agile/DevOps.
- **Key stakeholders:** Business analyst, product owner, users, architects, QA lead, security/compliance.
- **Entry:** Approved Charter and Vision/Scope.
- **Exit:** Baselined requirements set with traceability initialized; reviewed and signed off (or, in Agile, refined enough to plan next increment).
- **Primary deliverables:** BRS/BRD, StRS/URS, SyRS, SRS, use cases/user stories, acceptance criteria, Requirements Traceability Matrix (RTM).

### 2.1 Step — Elicitation
- **Purpose:** Discover stakeholder needs.
- **Inputs:** Vision/Scope; stakeholder register.
- **Activities:** Interviews, workshops, observation, document analysis, prototyping (29148:2018 §6.2.2).
- **Outputs:** Elicitation notes; preliminary needs list; **Concept of Operations (ConOps / OpsCon)** [HIGH] (29148:2018 Annex A defines ConOps for organization-level, OpsCon for system-level operational concept).
- **Owner:** Business analyst / Product Owner.
- **Exit:** Stakeholder needs documented and reviewed.

### 2.2 Step — Business Requirements Definition
- **Purpose:** Capture WHY at the enterprise level.
- **Inputs:** Vision, ConOps.
- **Activities:** Define business objectives, success metrics, regulatory drivers.
- **Outputs:** **Business Requirements Specification (BRS)** / Business Requirements Document (BRD) [HIGH] (29148:2018 §9.1).
- **Owner:** Business analyst.
- **Exit:** BRS approved by business sponsor.

### 2.3 Step — Stakeholder/User Requirements Definition
- **Purpose:** Capture WHAT users need.
- **Inputs:** BRS; ConOps.
- **Activities:** Identify user classes; capture user needs; develop personas, journey maps; define use cases.
- **Outputs:** **Stakeholder Requirements Specification (StRS)** [HIGH] (29148:2018 §9.2); **User Requirements Specification (URS)** (synonym widely used in pharma/medical and ICH/GAMP literature) [HIGH, CONDITIONAL: regulated]; **Use Cases** [HIGH] (Cockburn/Jacobson; SWEBOK v3 KA-Requirements §2).
- **Owner:** Business analyst / Product Owner.
- **Exit:** StRS reviewed; users sign off (regulated contexts).

### 2.4 Step — System Requirements Definition
- **Purpose:** Capture WHAT the system must do.
- **Inputs:** StRS.
- **Activities:** Functional decomposition; quality attribute analysis; constraints capture.
- **Outputs:** **System Requirements Specification (SyRS)** [HIGH] (29148:2018 §9.3).
- **Owner:** Systems engineer.
- **Exit:** SyRS reviewed and baselined.

### 2.5 Step — Software Requirements Specification
- **Purpose:** Capture WHAT the software must do, verifiably.
- **Inputs:** SyRS.
- **Activities:** Software-specific functional and non-functional requirements; interface specs; data requirements.
- **Outputs:** **Software Requirements Specification (SRS)** [HIGH] (ISO/IEC/IEEE 29148:2018 §9.4, which superseded IEEE 830-1998); **Functional Requirements Document (FRD)** as a sub-section or stand-alone in some industries [MODERATE]; **Interface Requirements Specification** (precursor to ICD) [MODERATE].
- **Owner:** Requirements engineer / business analyst.
- **Exit:** SRS reviewed (peer + sponsor); baselined.

### 2.6 Step — Backlog Construction (Agile/Scrum/SAFe variant)
- **Purpose:** Express requirements as ordered, refinable units of value.
- **Inputs:** Vision, Product Goal, customer feedback.
- **Activities:** Write user stories ("As a … I want … so that …"); define acceptance criteria; refine to "Ready"; estimate.
- **Outputs:** **Product Backlog** [HIGH for Scrum] (Scrum Guide 2020 — single source of work, ordered, emergent, with Product Goal commitment); **User Stories** [HIGH for Agile]; **Acceptance Criteria** [HIGH]; **Definition of Ready (DoR)** [MODERATE — common practice, not in Scrum Guide]; **Epics**, **Capabilities**, **Features** (SAFe hierarchy: Portfolio Epic → Capability → Feature → Story; SAFe 6.0); **Enabler stories/features/epics** for architectural runway, infrastructure, exploration, compliance (SAFe).
- **Owner:** Product Owner (Scrum) / Product Manager (SAFe ART level).
- **Exit:** Top of backlog refined to DoR; PI Planning prerequisites met.

### 2.7 Step — Requirements Validation & Traceability Initialization
- **Purpose:** Verify quality of requirements and establish traceability spine.
- **Inputs:** All requirements artifacts.
- **Activities:** Reviews/inspections (Fagan); verification of 29148 quality criteria (necessary, unambiguous, complete, singular, feasible, verifiable, traceable); build forward/backward links.
- **Outputs:** **Requirements Traceability Matrix (RTM)** [HIGH] (12207:2017 §6.3.1.3 *Project Assessment and Control*; 29148:2018 §5.2.8 — traceability is mandated bi-directional between needs ↔ requirements ↔ design ↔ tests); Requirements Review Records.
- **Owner:** QA / Requirements engineer.
- **Exit:** Bidirectional trace established; review defects closed.

### 2.8 Step — Requirements Baselining and Change Control
- **Purpose:** Freeze requirements as a controlled baseline.
- **Inputs:** Reviewed requirements.
- **Activities:** Baseline under Configuration Management; engage Change Control Board.
- **Outputs:** **Requirements Baseline** [HIGH] (12207:2017 §6.3.5 *Configuration Management*); **Change Control Procedure** (cross-cutting).
- **Exit:** Baseline locked.

### 2.Z Phase 2 Artifact Catalog

| Artifact | Purpose | Format | Author | Audience | Lifecycle | Confidence | Citation |
|---|---|---|---|---|---|---|---|
| ConOps / OpsCon | Operational viewpoint | Document, narrative | BA / systems engineer | All | Baselined | [HIGH] | 29148:2018 Annex A |
| BRS / BRD | Business-level requirements | Document | BA | Sponsor, dev | Baselined | [HIGH] | 29148:2018 §9.1 |
| StRS | Stakeholder requirements | Document | BA | All | Baselined | [HIGH] | 29148:2018 §9.2 |
| URS | User requirements (regulated) | Document | BA / clinical | Regulator | Baselined | [HIGH, CONDITIONAL: regulated] | GAMP 5; 29148 (synonymous use) |
| SyRS | System-level requirements | Document | Systems engineer | Architects, V&V | Baselined | [HIGH] | 29148:2018 §9.3 |
| SRS | Software requirements | Document | Req. engineer | Designers, testers | Baselined | [HIGH] | 29148:2018 §9.4 (supersedes IEEE 830-1998) |
| FRD | Functional reqs (subset) | Document / chapter | BA | Dev / QA | Baselined | [MODERATE] | Industry practice; 29148 functional req. content |
| Use Case | Behavioral spec from actor view | Use case template | BA | Dev / QA | Baselined or living | [HIGH] | SWEBOK v3 KA-Reqs §2; Cockburn |
| User Story | Lightweight req. unit (Agile) | Card / ticket | Product Owner | Scrum Team | Living, retired when Done | [VARIES: Agile/SAFe] | SAFe 6.0 Story; Cohn |
| Acceptance Criteria | Verifiable conditions | Bulleted list on story | Product Owner | Dev / QA | Living | [HIGH for Agile] | SAFe 6.0; Wake INVEST |
| Definition of Ready | Story readiness gate | Checklist | Scrum Team | Scrum Team | Standing | [MODERATE — not in Scrum Guide] | Scrum.org community |
| Epic | Strategic initiative | Hypothesis statement | Epic Owner | Portfolio | Funnel→Done | [VARIES: SAFe/Agile] | SAFe 6.0 Epic |
| Capability (SAFe) | Multi-ART value | Document | Solution Mgmt | Solution Train | PI-spanning | [VARIES: SAFe Large Solution] | SAFe 6.0 |
| Feature (SAFe) | ART-scoped value | Card with benefit hyp. | Product Mgr | ART | Lives ≤1 PI | [VARIES: SAFe] | SAFe 6.0 Features |
| Enabler (SAFe) | Architectural/infra/compliance work | Card | Architect / Owner | ART | Per backlog level | [VARIES: SAFe] | SAFe 6.0 Enablers |
| Product Backlog | Single ordered list of work | Tool list | Product Owner | Scrum Team, stakeholders | Living | [HIGH for Scrum] | Scrum Guide 2020 |
| RTM | Bi-directional traceability | Matrix / tool | QA / RM | V&V, regulator | Living, baselined per release | [HIGH] | 29148 §5.2.8; DO-178C §6.5; IEC 62304 §5.1.1; FDA GPSV §5.2.6 |
| Requirements Baseline | Controlled snapshot | CM record | CM lead | All | Baselined | [HIGH] | 12207:2017 §6.3.5 |
| Software Requirements (DO-178C) — High-Level Requirements | Cert evidence | Document set | Req. engineer | Cert authority | Baselined | [CONDITIONAL: DO-178C] | DO-178C §5.1, §11.9 |

---

## 3. Phase 3 — Architecture & Design

### 3.0 Phase Summary
- **Purpose [HIGH]:** Define how the system will satisfy requirements (12207:2017 §6.4.4 *Architecture Definition*; §6.4.5 *Design Definition*; SWEBOK v3 KA-Software Design).
- **Effort share [MODERATE]:** 10–20 % (BDUF); continuous in Agile.
- **Stakeholders:** Architects, designers, security architect, data architect, ops/SRE, QA.
- **Entry:** Baselined requirements.
- **Exit:** Architecture baselined; design adequate to begin construction; ADRs recorded; threat model produced.
- **Deliverables:** SAD, HLD, LLD, ADRs, Interface Control Documents, data models, threat models, NFR allocation.

### 3.1 Step — Architectural Analysis
- **Purpose:** Identify drivers, constraints, quality attributes.
- **Activities:** Quality attribute workshop (SEI QAW); stakeholder utility tree; constraint catalog.
- **Outputs:** Architectural Drivers list; QA Scenarios [MODERATE] (SEI/ATAM).
- **Exit:** Drivers reviewed.

### 3.2 Step — Architecture Definition
- **Purpose:** Establish system structure and views.
- **Activities:** Decompose into elements; define views per ISO/IEC/IEEE 42010:2011 (architecture description); document concerns/viewpoints.
- **Outputs:** **Software Architecture Document (SAD)** / **High-Level Design (HLD)** [HIGH] (IEEE 1016-2009 *Software Design Descriptions*; arc42 template; "4+1" Kruchten); architectural views (logical, process, development, physical, scenarios).
- **Owner:** Lead/principal architect.
- **Exit:** Architecture review (e.g., SEI ATAM) passed.

### 3.3 Step — Architecture Decisions
- **Purpose:** Capture significant decisions and rationale.
- **Activities:** Record options, decision, consequences (Nygard format).
- **Outputs:** **Architecture Decision Records (ADRs)** [MODERATE] (Nygard 2011; ThoughtWorks Tech Radar; explicit in arc42 §9).
- **Owner:** Architect.
- **Exit:** ADRs published in repo.

### 3.4 Step — Detailed (Low-Level) Design
- **Purpose:** Specify components, classes, modules sufficient for coding.
- **Activities:** Class/module design, sequence diagrams, state machines, algorithms.
- **Outputs:** **Low-Level Design (LLD) / Software Design Description (SDD)** [HIGH] (IEEE 1016-2009 §5: stakeholder concerns, design viewpoints, design views, design overlays); **Low-Level Requirements** in DO-178C terms [CONDITIONAL: DO-178C §5.2].
- **Owner:** Module lead / senior dev.
- **Exit:** Design review (peer); checklist (e.g., Fagan).

### 3.5 Step — Interface Design
- **Purpose:** Define interfaces between system elements and external systems.
- **Activities:** Identify interfaces; specify protocols, message formats, error handling, SLAs.
- **Outputs:** **Interface Control Document (ICD)** [HIGH, CONDITIONAL: regulated/aerospace/integration-heavy] (MIL-STD-498; NASA SE Handbook §6.3); API specs (OpenAPI/AsyncAPI/Protobuf) [HIGH].
- **Owner:** Integration architect.
- **Exit:** ICDs signed by both sides of interface.

### 3.6 Step — Data Design
- **Purpose:** Define logical and physical data models and lifecycle.
- **Activities:** Conceptual → logical → physical modeling (ER diagrams, schemas), retention/archival rules, classification.
- **Outputs:** **Data Model / Entity-Relationship Diagram (ERD)** [HIGH]; **Data Dictionary** [HIGH]; Data Classification Matrix [MODERATE]; Retention Schedule (cross-cutting).
- **Owner:** Data architect / DBA.
- **Exit:** Model reviewed.

### 3.7 Step — Security Architecture & Threat Modeling
- **Purpose:** Identify threats and design countermeasures (SSDF PW.1).
- **Activities:** STRIDE/LINDDUN/PASTA threat modeling; data flow diagrams; trust boundaries; control mapping; abuse cases.
- **Outputs:** **Threat Model** [HIGH] (NIST SP 800-218 PW.1.1 — "Use forms of risk modeling—such as threat modeling, attack modeling, or attack surface mapping—to help assess the security risk for the software"); **Security Architecture Document** [MODERATE] (OWASP SAMM Design > Threat Assessment, Security Architecture).
- **Owner:** Security architect.
- **Exit:** Threat model reviewed; mitigations traced to design and tests.

### 3.8 Step — Non-Functional Requirements (NFR) Allocation
- **Purpose:** Allocate quality attributes to elements.
- **Activities:** Allocate performance, availability, scalability budgets; design for testability.
- **Outputs:** **NFR Allocation Matrix** [MODERATE]; **Performance Budget Document** [MODERATE]; SLO targets (cross-cutting with §7).
- **Owner:** Architect / SRE.
- **Exit:** Budgets agreed; tests defined.

### 3.9 Step — Design Verification & Baseline
- **Purpose:** Confirm design satisfies requirements.
- **Activities:** Design reviews, design walkthroughs, structural traceability check.
- **Outputs:** Design Review Records; updated **RTM** (reqs → design); Design Baseline.
- **Exit:** Design baselined under CM.

### 3.Z Phase 3 Artifact Catalog

| Artifact | Purpose | Format | Author | Audience | Lifecycle | Confidence | Citation |
|---|---|---|---|---|---|---|---|
| Software Architecture Document / HLD | Whole-system structure | Document; views | Lead architect | Dev, ops, security, QA | Living; baselined per release | [HIGH] | IEEE 1016-2009; ISO 42010:2011; arc42 |
| Low-Level Design (LLD) / SDD | Module-level design | Document / wiki | Senior dev | Implementers, reviewers | Baselined per release | [HIGH] | IEEE 1016-2009 |
| Architecture Decision Record (ADR) | Decision + rationale | Markdown ≤1 pg | Architect | Future maintainers | Append-only; superseded not deleted | [MODERATE] | Nygard 2011; arc42 §9 |
| Interface Control Document (ICD) | Inter-system contract | Document | Integration architect | Both sides | Baselined; versioned | [HIGH, CONDITIONAL: integration / aerospace] | MIL-STD-498; NASA SE Handbook |
| API Specification | Service contract | OpenAPI / AsyncAPI / proto | Service owner | Consumers | Living | [HIGH] | OpenAPI 3.x; SSDF PW.4 |
| Data Model / ERD | Entity structure | Diagram + DDL | Data architect | DBA, dev, BI | Living; baselined | [HIGH] | SWEBOK v3 KA-Software Design |
| Data Dictionary | Field definitions | Table | Data steward | Dev, BI, compliance | Living | [HIGH] | SWEBOK; DAMA-DMBOK |
| Threat Model | Threat catalog + mitigations | Diagram + table | Security architect | Dev, security | Living; updated on change | [HIGH] | NIST SP 800-218 PW.1; OWASP SAMM Design |
| Security Architecture Document | Security control design | Document | Security architect | Auditor, dev | Baselined | [MODERATE] | OWASP SAMM; SSDF PW.1 |
| NFR Allocation Matrix | Quality attribute mapping | Table | Architect | All | Living | [MODERATE] | SWEBOK v3 |
| Software Architecture (DO-178C) | Cert artifact | Document | Architect | Cert authority | Baselined | [CONDITIONAL: DO-178C §5.2, §11.10] | DO-178C |

---

## 4. Phase 4 — Implementation / Construction

### 4.0 Phase Summary
- **Purpose [HIGH]:** Produce executable software conforming to design (12207:2017 §6.4.6 *Implementation Process*).
- **Effort share:** 30–50 % (Waterfall); continuous in Agile/DevOps.
- **Entry:** Approved/refined design or "Ready" backlog item.
- **Exit:** Code passes peer review, unit tests, and CI quality gates; produces a deployable artifact.

### 4.1 Step — Coding Standards Application
- **Outputs:** **Coding Standards Document** [HIGH, CONDITIONAL: regulated; e.g., DO-178C §11.8 mandates a Software Code Standards document; IEC 62304 §5.5.1].
- **Owner:** Engineering lead.

### 4.2 Step — Source Code Production
- **Activities:** Implement units; write inline tests.
- **Outputs:** **Source Code** [HIGH] (12207:2017 §6.4.6.3); **Unit Test Code** [HIGH].
- **Owner:** Developer.

### 4.3 Step — Code Review / Pull Request
- **Activities:** Peer review (Fagan, lightweight, or pair); static analysis review.
- **Outputs:** **Code Review Records** / Pull Request comments [HIGH] (SWEBOK v3 KA-SQ §2.3; DO-178C Table A-5 Obj. 1–7); merged commit history.
- **Owner:** Reviewer (independent for Class C / DAL A–B).

### 4.4 Step — Static Application Security Testing (SAST) & Composition Analysis
- **Activities:** SAST scan; SCA for OSS/dependency vulnerabilities; license scan.
- **Outputs:** SAST report; SCA report; **Software Bill of Materials (SBOM)** [HIGH] (CISA/NTIA *Minimum Elements for a Software Bill of Materials*, 2021; updated draft 2025; Executive Order 14028; SSDF PS.3 / PW.4).
- **Owner:** Developer / AppSec.

### 4.5 Step — Build & Continuous Integration
- **Activities:** Compile, link, package; produce reproducible build.
- **Outputs:** **Build Manifest** [HIGH] (SLSA provenance attestation v1.0; SSDF PS.2/PS.3); **Build Artifacts** (binary, container image); **Build Logs**; signed provenance.
- **Owner:** CI engineer / dev.

### 4.6 Step — Unit Test Execution
- **Outputs:** Unit test results [HIGH]; coverage report; for DO-178C: structural coverage evidence (Statement, Decision, MC/DC for DAL A) [CONDITIONAL: DO-178C §6.4.4.2, Table A-7].

### 4.7 Step — Configuration Management of Code
- **Outputs:** Tagged commits; branch policies; **Software Configuration Management Records** (cross-cutting; 12207:2017 §6.3.5).

### 4.8 Step — Secure Coding Verification (SSDF)
- **Activities:** Per SSDF PW.4–PW.7: secure coding practices, code review, source code testing.
- **Outputs:** Compliance attestation entries; secret-scanning reports.

### 4.Z Phase 4 Artifact Catalog

| Artifact | Purpose | Format | Author | Audience | Lifecycle | Confidence | Citation |
|---|---|---|---|---|---|---|---|
| Source Code | Executable spec | Repository | Developer | All | Living; tagged | [HIGH] | 12207:2017 §6.4.6 |
| Coding Standards | Uniform style/safety | Document | Eng lead | Devs | Standing | [HIGH; CONDITIONAL: regulated mandates it] | DO-178C §11.8; IEC 62304 §5.5.1; MISRA |
| Unit Test Code & Results | Code-level verification | Code + reports | Developer | QA, regulator | Living; archived | [HIGH] | 12207:2017 §6.4.9; IEEE 829-2008 |
| Code Review Record | Evidence of peer review | PR comments / form | Reviewer | Auditor, team | Retained | [HIGH] | SWEBOK v3; DO-178C Tbl A-5 |
| SAST Report | Static security findings | Tool output | AppSec | Dev, AppSec | Per build | [HIGH] | OWASP SAMM Verification; SSDF PW.7 |
| SCA / Dependency Scan | Third-party vulnerabilities | Tool output | AppSec | Dev, AppSec | Per build | [HIGH] | SSDF PW.4; OWASP Top 10 A06 |
| Software Bill of Materials (SBOM) | Component inventory | SPDX / CycloneDX | Build system | Customers, gov, SOC | Per build artifact | [HIGH] | CISA/NTIA Minimum Elements 2021; CISA 2025 draft; EO 14028 |
| Build Manifest / Provenance | Reproducible build record | SLSA attestation | CI system | Auditor, downstream | Per build | [HIGH] | SLSA v1.0; SSDF PS.2 |
| Build Artifact | Deployable output | Binary / image / package | CI | Deployment | Per build | [HIGH] | 12207:2017 §6.4.6 |
| Source Code Standards (DO-178C) | Cert evidence | Document | Lead dev | Cert authority | Baselined | [CONDITIONAL: DO-178C §11.8] | DO-178C |

---

## 5. Phase 5 — Verification & Validation

### 5.0 Phase Summary
- **Purpose [HIGH]:** Verify the product is built right and validate it is the right product (12207:2017 §6.4.9 *Verification* and §6.4.11 *Validation*; FDA GPSV §3.1.2 distinction).
- **Effort share:** 20–40 %.
- **Stakeholders:** QA lead, test engineers, users (UAT), security testers, performance engineers, regulators (where applicable).
- **Entry:** Build available; test environment ready; test artifacts approved.
- **Exit:** Test exit criteria met; defects triaged; release candidate approved.

### 5.1 Step — Test Strategy Definition
- **Outputs:** **Test Strategy** [HIGH] (ISTQB/IEEE 29119-1; corresponds to organizational test policy + strategy).
- **Owner:** Head of QA.

### 5.2 Step — Master Test Planning
- **Outputs:** **Master Test Plan** [HIGH] (IEEE Std 829-2008 *Standard for Software and System Test Documentation* — superseded by ISO/IEC/IEEE 29119-3:2013 which renames to *Project Test Plan* and *Test Sub-Plans*).
- **Owner:** Test manager.

### 5.3 Step — Level Test Plans
- **Activities:** Develop per-level plans.
- **Outputs:**
  - **Unit Test Plan** [HIGH] (IEEE 829 §6 / 29119-3)
  - **Integration Test Plan** [HIGH]
  - **System Test Plan** [HIGH]
  - **User Acceptance Test (UAT) Plan** [HIGH]
  - **Performance Test Plan** [MODERATE]
  - **Security Test Plan** [HIGH] (SSDF PW.8)
  - **Regression Test Plan** [HIGH]

### 5.4 Step — Test Case Design and Scripting
- **Outputs:** **Test Cases** and **Test Scripts/Procedures** [HIGH] (IEEE 829-2008 §8/§9; 29119-3 *Test Case Specification*, *Test Procedure Specification*); test data sets.
- **Owner:** Test engineer.

### 5.5 Step — Verification (Reviews, Analyses, Tests)
- **Activities:** Inspections, analyses, formal verification (where used), and testing at each V-Model level. DO-178C distinguishes Reviews, Analyses, and Tests as the verification methods (§6.3).
- **Outputs:** Verification records; **Test Logs/Records** [HIGH] (IEEE 829-2008 §15); **Anomaly/Defect Reports** [HIGH] (IEEE 1044-2009; IEC 62304 §6 *Problem Resolution*).

### 5.6 Step — Validation (UAT, Operational Validation)
- **Activities:** Stakeholders confirm fitness for intended use in target environment.
- **Outputs:** **UAT Sign-off** [HIGH] (FDA GPSV §3.1.2: "validation is confirmation by examination and provision of objective evidence that software specifications conform to user needs and intended uses").

### 5.7 Step — Performance, Security, and Other Specialty Testing
- **Outputs:** Performance test report; **DAST report** [HIGH]; **Penetration Test Report** [MODERATE]; chaos engineering reports [VARIES: SRE].

### 5.8 Step — Test Reporting and Closure
- **Outputs:** **Test Summary Report** / **Master Test Report** [HIGH] (IEEE 829-2008 §17; 29119-3 *Test Status Report*, *Test Completion Report*); updated RTM (req ↔ test ↔ result); **Test Coverage Report**.

### 5.9 Step — Independent V&V (where required)
- **Outputs:** IV&V reports [CONDITIONAL: IEEE 1012-2016 *Independent V&V*; DO-178C "verification with independence" per Annex A; IEC 62304 §5.6 for Class B/C].

### 5.Z Phase 5 Artifact Catalog

| Artifact | Purpose | Format | Author | Audience | Lifecycle | Confidence | Citation |
|---|---|---|---|---|---|---|---|
| Test Strategy | Org-wide test approach | Document | QA leadership | All | Standing | [HIGH] | ISTQB; ISO/IEC/IEEE 29119-1 |
| Master Test Plan | Project test plan | Document | Test manager | Project, regulator | Baselined | [HIGH] | IEEE 829-2008; 29119-3 |
| Unit/Integration/System/UAT/Perf/Sec/Regression Test Plans | Level-specific | Document | Test lead per level | Dev, QA, users | Baselined | [HIGH] | IEEE 829-2008; 29119-3 |
| Test Case Specification | Atomic test definition | Doc / tool | Test engineer | QA, regulator | Living | [HIGH] | IEEE 829 §8; 29119-3 |
| Test Procedure / Script | Step-by-step execution | Doc / automated | Test engineer | QA | Living | [HIGH] | IEEE 829 §9; 29119-3 |
| Test Log | Execution evidence | Tool output | Test runner | Auditor | Retained | [HIGH] | IEEE 829 §15 |
| Anomaly / Defect Report | Defect record | Tracker ticket | Tester | Dev, PM | Lifecycle: open→closed | [HIGH] | IEEE 1044-2009 |
| UAT Sign-off | User validation | Memo / form | User rep | Sponsor | Baselined per release | [HIGH] | FDA GPSV §3.1.2 |
| Test Summary Report | Outcome of test cycle | Document | Test manager | Sponsor, regulator | Per release | [HIGH] | IEEE 829 §17 |
| RTM (final) | Reqs→design→code→tests→results | Matrix | QA | Regulator, audit | Released | [HIGH] | 29148; DO-178C §6.5; IEC 62304 §5.1.1 |
| Software Verification Plan / Cases / Procedures / Results (DO-178C) | Cert evidence | Document set | V&V lead | Cert authority | Baselined | [CONDITIONAL: DO-178C §11.13–§11.14] | DO-178C Annex A Table A-3..A-7 |
| Software Verification Plan (IEC 62304) | Verification activities | Document | V&V lead | Notified body | Baselined | [CONDITIONAL: IEC 62304 §5.1.6, §5.5–§5.7] | IEC 62304 |
| IV&V Report | Independent V&V result | Document | IV&V org | Regulator | Per cycle | [CONDITIONAL: IEEE 1012-2016] | IEEE 1012-2016 |

---

## 6. Phase 6 — Release & Deployment

### 6.0 Phase Summary
- **Purpose [HIGH]:** Transition validated software into the operational environment (12207:2017 §6.4.10 *Transition*).
- **Effort share:** 5–10 % (traditional); collapsed into automated pipelines under CD.
- **Entry:** Release candidate approved; release readiness review passed.
- **Exit:** Software in production; users notified; ops accepts handover.

### 6.1 Step — Release Planning
- **Outputs:** **Release Plan** [HIGH] (12207:2017 §6.4.10).

### 6.2 Step — Release Readiness Review (Go/No-Go)
- **Outputs:** **Release Readiness Review Record** [HIGH]; sign-off matrix; for DO-178C the **Software Conformity Review** prior to **Software Accomplishment Summary (SAS)** (DO-178C §9.4, §11.20).

### 6.3 Step — Deployment Plan & Runbook
- **Outputs:** **Deployment Plan** [HIGH]; **Deployment Runbook** [HIGH]; **Rollback Plan** [HIGH]; environment configuration (IaC).

### 6.4 Step — Build Promotion / Pipeline Execution
- **Activities:** Promote artifact through environments; signed deploy.
- **Outputs:** Deployment record; signed provenance attestation; SBOM published with artifact.

### 6.5 Step — Release Notes and Documentation Publication
- **Outputs:** **Release Notes** [HIGH]; user/operator documentation update; **Known Issues List**.

### 6.6 Step — Operational Acceptance
- **Outputs:** Operational Acceptance Sign-off; handover package to ops/SRE.

### 6.7 Step — Regulated Release Activities [CONDITIONAL]
- **Outputs:**
  - DO-178C **Software Configuration Index (SCI)** and **Software Life Cycle Environment Configuration Index (SECI)** [CONDITIONAL: DO-178C §11.16–§11.17]
  - DO-178C **Software Accomplishment Summary (SAS)** [CONDITIONAL: §11.20]
  - IEC 62304 **Release Documentation** including residual anomalies disclosure [CONDITIONAL: IEC 62304 §5.8]
  - 21 CFR Part 11 e-record signature manifest [CONDITIONAL]

### 6.Z Phase 6 Artifact Catalog

| Artifact | Purpose | Format | Author | Audience | Lifecycle | Confidence | Citation |
|---|---|---|---|---|---|---|---|
| Release Plan | Schedule / scope of release | Document | Release manager | All | Per release | [HIGH] | 12207:2017 §6.4.10 |
| Release Readiness Review | Go/no-go evidence | Form / minutes | Release mgr | Sponsor | Per release | [HIGH] | ITIL 4; 12207 §6.4.10 |
| Deployment Plan | Steps and sequence | Document | Release / SRE | Ops | Per release | [HIGH] | 12207:2017 §6.4.10 |
| Deployment Runbook | Operational steps | Markdown / wiki | SRE / Ops | Ops on-call | Living | [HIGH] | Google SRE Book Ch. 8 |
| Rollback Plan | Reversion steps | Document | Release / SRE | Ops | Per release | [HIGH] | ITIL Change Mgmt |
| Release Notes | What's changed | Document / web page | Product / release mgr | Users | Per release | [HIGH] | Industry standard |
| Known Issues List | Outstanding defects | List | QA | Users | Per release | [MODERATE] | Industry practice |
| Software Configuration Index (SCI) | DO-178C cert | Document | CM | FAA/EASA | Baselined | [CONDITIONAL: DO-178C §11.16] | DO-178C |
| Software Life Cycle Environment Configuration Index (SECI) | Tools/env | Document | CM | Cert authority | Baselined | [CONDITIONAL: DO-178C §11.17] | DO-178C |
| Software Accomplishment Summary (SAS) | Final cert summary | Document | Cert lead | FAA/EASA | Final | [CONDITIONAL: DO-178C §11.20] | DO-178C §9.3 |
| Residual Anomaly List | Open issues at release | Table | QA | Notified body | Released | [CONDITIONAL: IEC 62304 §5.8.3] | IEC 62304 |

---

## 7. Phase 7 — Operations & Maintenance

### 7.0 Phase Summary
- **Purpose [HIGH]:** Operate the software, monitor service, manage incidents, and evolve the product (12207:2017 §6.4.13 *Operation*; §6.4.14 *Maintenance*; ISO/IEC 14764:2022 *Software Engineering — Software Life Cycle Processes — Maintenance*).
- **Maintenance categories per ISO/IEC 14764:** Corrective, Adaptive, Perfective, Preventive [HIGH].
- **Stakeholders:** Ops/SRE, support, security ops (SOC), product, dev.

### 7.1 Step — Service Operation and Monitoring
- **Outputs:** **Service Level Agreement (SLA)** [HIGH]; **Service Level Objectives (SLOs)** and **Service Level Indicators (SLIs)** [HIGH] (Google SRE Book Ch. 4); **Error Budget Policy** [MODERATE]; monitoring dashboards.

### 7.2 Step — Incident Management
- **Outputs:** **Incident Reports** [HIGH] (ITIL 4 *Incident Management*); paging records.

### 7.3 Step — Postmortems / Post-Incident Reviews
- **Outputs:** **Postmortem / Post-Incident Review Document** [HIGH] (Google SRE Book Ch. 15 — blameless postmortem); action item register.

### 7.4 Step — Change Management
- **Outputs:** **Request for Change (RFC) / Change Request** [HIGH] (ITIL 4 *Change Enablement*); CAB minutes; change record. Under DevOps, normal changes are pre-approved via pipeline policy.

### 7.5 Step — Maintenance Releases
- **Activities:** Bug fix, adaptive (env change), perfective (improvement), preventive (refactor).
- **Outputs:** Patch releases; updated SBOM; updated documentation.

### 7.6 Step — Vulnerability and Patch Management
- **Outputs:** Vulnerability advisories; **VEX (Vulnerability Exploitability eXchange) documents** [HIGH] (CISA VEX guidance 2023; SSDF RV.1–RV.3); patch records.

### 7.7 Step — Continuous Improvement & Metrics
- **Outputs:** **DORA metrics** [HIGH] (Deployment Frequency, Lead Time for Changes, Change Failure Rate, Failed Deployment Recovery Time / MTTR — DORA *State of DevOps* reports; Forsgren, Humble, Kim, *Accelerate* 2018); SLO compliance reports.

### 7.8 Step — Periodic Reviews / Audits [CONDITIONAL: regulated]
- **Outputs:** Internal audit records (ISO 13485 §8.2.4); Software Quality Assurance Records (DO-178C §11.19).

### 7.Z Phase 7 Artifact Catalog

| Artifact | Purpose | Format | Author | Audience | Lifecycle | Confidence | Citation |
|---|---|---|---|---|---|---|---|
| SLA | Customer-facing service contract | Document | Service owner / legal | Customer, ops | Living; renewed | [HIGH] | ITIL 4 SLM |
| SLO / SLI | Internal targets | Document / dashboard | SRE | Ops, product | Living | [HIGH] | Google SRE Book Ch. 4 |
| Error Budget Policy | Speed/stability rule | Document | SRE / leadership | Eng leadership | Standing | [MODERATE] | Google SRE Book Ch. 3 |
| Incident Report | Per-incident record | Ticket | On-call / IM | Ops, mgmt | Per incident | [HIGH] | ITIL 4 |
| Postmortem | Learning artifact | Document | IC / SRE | Org | Per major incident | [HIGH] | Google SRE Ch. 15 |
| RFC / Change Request | Proposal to change | Form / ticket | Requestor | CAB | Per change | [HIGH] | ITIL 4 Change Enablement |
| VEX Document | Vuln. exploitability statement | CSAF / OpenVEX | Producer | Customers, SOC | Per advisory | [HIGH] | CISA VEX guidance |
| DORA Metrics Report | Delivery performance | Dashboard | Eng leadership | Org | Living | [HIGH] | DORA *State of DevOps*; *Accelerate* |
| Operations Runbook | Operational procedures | Markdown / wiki | SRE | Ops | Living | [HIGH] | SRE practice |
| Capacity Plan | Forecast & scaling | Document | SRE | Ops, finance | Periodic | [MODERATE] | Google SRE Ch. 18 |
| Audit Records | Compliance evidence | Records | QMS | Regulator | Retained per QMS | [CONDITIONAL: ISO 13485] | ISO 13485:2016 §8.2.4 |

---

## 8. Phase 8 — Retirement / Decommissioning

### 8.0 Phase Summary
- **Purpose [HIGH]:** Withdraw the system from service in a controlled manner (12207:2017 §6.4.15 *Disposal*).
- **Stakeholders:** Product, ops, data steward, legal, security, customers.

### 8.1 Step — Decommissioning Decision
- **Outputs:** **Retirement / Decommissioning Decision Memo** [HIGH] (12207:2017 §6.4.15.1).

### 8.2 Step — Decommissioning Plan
- **Outputs:** **Decommissioning Plan** [HIGH] including timeline, dependencies, communications, data handling, contractual obligations, regulatory retention (12207:2017 §6.4.15.3).

### 8.3 Step — User Communication and Migration
- **Outputs:** End-of-life (EOL) / End-of-Service (EOS) notice; migration plan; data export tooling.

### 8.4 Step — Data Archival, Migration, and Destruction
- **Outputs:** **Data Archival Plan** [HIGH]; archival manifest; **Certificate of Data Destruction** [HIGH] for secure media sanitization (NIST SP 800-88 Rev. 1 *Guidelines for Media Sanitization*).

### 8.5 Step — Infrastructure Decommissioning
- **Outputs:** Environment teardown record; IAM revocation list; license return; final cost reconciliation.

### 8.6 Step — Knowledge Preservation & Lessons Learned
- **Outputs:** **Project Closeout Report** [HIGH] (PMBOK 7th Ed.); lessons-learned register; archival of artifacts to records management.

### 8.7 Step — Regulated Closure [CONDITIONAL]
- **Outputs:** Regulatory notification (e.g., FDA discontinuation); long-term retention of design history file and audit records (ISO 13485 §4.2.5; 21 CFR Part 11 e-record retention).

### 8.Z Phase 8 Artifact Catalog

| Artifact | Purpose | Format | Author | Audience | Lifecycle | Confidence | Citation |
|---|---|---|---|---|---|---|---|
| Retirement Decision Memo | Authorize decommissioning | Memo | Owner / sponsor | Stakeholders | Final | [HIGH] | 12207:2017 §6.4.15 |
| Decommissioning Plan | How withdrawal will occur | Document | PM / ops | All | Baselined | [HIGH] | 12207:2017 §6.4.15.3 |
| EOL / EOS Notice | Customer notice | Communication | Product mgmt | Customers | One-time | [HIGH] | Industry std. |
| Data Archival Plan | Data preservation strategy | Document | Data steward | Compliance, ops | Baselined | [HIGH] | NIST SP 800-88; ISO 15489 |
| Certificate of Data Destruction | Evidence of sanitization | Form | Custodian | Auditor, customer | Per asset | [HIGH] | NIST SP 800-88 Rev. 1 |
| Project Closeout Report | Lessons / final state | Document | PM | Org | Final | [HIGH] | PMBOK 7th Ed. |
| Records Retention Schedule | What to keep, how long | Document | RIM | Legal, audit | Standing | [HIGH; CONDITIONAL strengthens] | ISO 15489; 21 CFR Part 11 |

---

## 9. Cross-Cutting Artifact Index

| Artifact | Phases Active | Owner | Confidence | Source |
|---|---|---|---|---|
| Project Management Plan (subsidiary plans: scope, schedule, cost, comms, risk, resource) | 1–8 | PM | [HIGH] | PMBOK 7th Ed.; 12207:2017 §6.3.1 |
| Risk Register / Risk Management File | 1–8 | Risk lead / PM | [HIGH] | ISO 31000:2018; PMBOK; ISO 14971 (medical) |
| Configuration Management Plan & Records | 2–8 | CM lead | [HIGH] | ISO/IEC/IEEE 12207 §6.3.5; IEEE 828-2012; DO-178C §11.18 |
| Software Quality Assurance Plan & Records | 1–8 | QA lead | [HIGH] | IEEE 730-2014; DO-178C §11.19 |
| Documentation Plan / Information Management Plan | 1–8 | Tech writer / PM | [HIGH] | ISO/IEC/IEEE 26511; 12207 §6.3.6 |
| Communications Plan & Status Reports | 1–8 | PM | [HIGH] | PMBOK 7th Ed. |
| Stakeholder Register | 1–8 | PM | [HIGH] | PMBOK 7th Ed. |
| Security Plan / SSDF Compliance Record | 1–8 | CISO / AppSec | [HIGH] | NIST SP 800-218; SSDF PO–RV |
| Threat Model | 3–7 (created 3, updated 5–7) | Security architect | [HIGH] | SSDF PW.1; OWASP SAMM |
| Security Test Reports (SAST/DAST/SCA/Pen) | 4–7 | AppSec | [HIGH] | SSDF PW.7/PW.8; OWASP SAMM Verification |
| SBOM | 4–8 | Build system | [HIGH] | CISA/NTIA Min Elements; EO 14028; SSDF PS.3 |
| VEX | 6–8 | Producer | [HIGH] | CISA VEX guidance |
| Requirements Traceability Matrix | 2–8 | QA / RM | [HIGH] | 29148:2018 §5.2.8; DO-178C §6.5; IEC 62304 §5.1.1 |
| Audit Trail / Records | 1–8 | QMS | [HIGH; CONDITIONAL strengthens] | 21 CFR Part 11 §11.10(e); ISO 13485 §4.2.5 |
| Compliance Matrix | 2–8 | Compliance lead | [CONDITIONAL: regulated] | DO-178C §11.20; FDA QSR |
| Training Records | 1–8 | HR / training lead | [HIGH; CONDITIONAL strengthens] | ISO 13485 §6.2; SSDF PO.2 |
| Glossary / Terminology Document | 1–8 | Tech writer | [MODERATE] | 26511; arc42 §12 |
| Change Log / Change History | 4–8 | CM | [HIGH] | 12207 §6.3.5; IEEE 828-2012 |
| Software Development Plan (SDP) | 1–8 | PM / eng lead | [HIGH; CONDITIONAL: required] | DO-178C §11.2; IEC 62304 §5.1; FDA GPSV §5.2.1 |
| Software Verification Plan | 2–8 | V&V lead | [HIGH; CONDITIONAL] | DO-178C §11.3; IEC 62304 §5.1.6 |
| Software Configuration Management Plan | 1–8 | CM lead | [HIGH; CONDITIONAL] | DO-178C §11.4; IEC 62304 §8 |
| Software Quality Assurance Plan | 1–8 | QA lead | [HIGH; CONDITIONAL] | DO-178C §11.5; IEEE 730-2014 |
| Plan for Software Aspects of Certification (PSAC) | 1–8 | Cert lead | [CONDITIONAL: DO-178C] | DO-178C §11.1 |
| Software Risk Management File | 1–8 | Safety lead | [CONDITIONAL: medical] | ISO 14971:2019; IEC 62304 §7 |
| Problem Reports / Anomaly Reports | 4–8 | Anyone | [HIGH] | IEEE 1044-2009; IEC 62304 §6 |
| Periodic SQA Audit Records | 4–8 | QA | [HIGH; CONDITIONAL] | DO-178C Tbl A-9; IEEE 730-2014 |

---

## 10. Master Artifact Index (Alphabetical)

| Artifact | Phase(s) | Confidence |
|---|---|---|
| Acceptance Criteria | 2 | [HIGH for Agile] |
| Anomaly / Defect Report | 5–7 | [HIGH] |
| API Specification | 3–8 | [HIGH] |
| Architecture Decision Record (ADR) | 3 | [MODERATE] |
| Audit Trail | 1–8 | [HIGH] |
| Build Artifact | 4–6 | [HIGH] |
| Build Manifest / Provenance | 4–6 | [HIGH] |
| Business Case | 1 | [HIGH] |
| Business Requirements Specification (BRS/BRD) | 2 | [HIGH] |
| Capability (SAFe) | 2 | [VARIES: SAFe] |
| Capacity Plan | 7 | [MODERATE] |
| Certificate of Data Destruction | 8 | [HIGH] |
| Change Control Records | 2–8 | [HIGH] |
| Change Log | 4–8 | [HIGH] |
| Coding Standards | 4 | [HIGH] |
| Code Review Records | 4 | [HIGH] |
| Compliance Matrix | 2–8 | [CONDITIONAL] |
| Concept of Operations (ConOps/OpsCon) | 1–2 | [HIGH] |
| Configuration Management Plan | 2–8 | [HIGH] |
| Data Archival Plan | 8 | [HIGH] |
| Data Dictionary | 3 | [HIGH] |
| Data Model / ERD | 3 | [HIGH] |
| Decommissioning Plan | 8 | [HIGH] |
| Definition of Done | 2,4,5,6 | [HIGH for Scrum] |
| Definition of Ready | 2 | [MODERATE] |
| Deployment Plan | 6 | [HIGH] |
| Deployment Runbook | 6–7 | [HIGH] |
| DORA Metrics Report | 7 | [HIGH] |
| Enabler (SAFe) | 2 | [VARIES] |
| Epic | 2 | [VARIES: SAFe/Agile] |
| Error Budget Policy | 7 | [MODERATE] |
| Feature (SAFe) | 2 | [VARIES] |
| Functional Requirements Document (FRD) | 2 | [MODERATE] |
| High-Level Design (HLD) / SAD | 3 | [HIGH] |
| Incident Report | 7 | [HIGH] |
| Interface Control Document (ICD) | 3 | [HIGH; CONDITIONAL] |
| Known Issues List | 6 | [MODERATE] |
| Lean Business Case | 1 | [VARIES: SAFe] |
| Low-Level Design (LLD) / SDD | 3 | [HIGH] |
| Master Test Plan | 5 | [HIGH] |
| NFR Allocation Matrix | 3 | [MODERATE] |
| Operations Runbook | 7 | [HIGH] |
| Performance Test Plan | 5 | [MODERATE] |
| Plan for Software Aspects of Certification (PSAC) | 1 | [CONDITIONAL: DO-178C] |
| Postmortem | 7 | [HIGH] |
| Product Backlog | 2,4 | [HIGH for Scrum] |
| Product Goal | 1–8 | [VARIES: Scrum] |
| Project Charter | 1 | [HIGH] |
| Project Closeout Report | 8 | [HIGH] |
| Project Management Plan | 1–8 | [HIGH] |
| Regression Test Plan | 5 | [HIGH] |
| Release Notes | 6 | [HIGH] |
| Release Plan | 6 | [HIGH] |
| Release Readiness Review | 6 | [HIGH] |
| Request for Change (RFC) | 7 | [HIGH] |
| Requirements Baseline | 2 | [HIGH] |
| Requirements Traceability Matrix (RTM) | 2–8 | [HIGH] |
| Residual Anomaly List | 6 | [CONDITIONAL: IEC 62304] |
| Risk Register / Risk Management File | 1–8 | [HIGH] |
| Rollback Plan | 6 | [HIGH] |
| SAST Report | 4 | [HIGH] |
| SCA Report | 4 | [HIGH] |
| SBOM | 4–8 | [HIGH] |
| Security Architecture Document | 3 | [MODERATE] |
| Security Test Plan | 5 | [HIGH] |
| Sprint Backlog | 2,4 | [HIGH for Scrum] |
| Sprint Goal | 4 | [HIGH for Scrum] |
| Source Code | 4 | [HIGH] |
| Stakeholder Register | 1–8 | [HIGH] |
| Stakeholder Requirements Specification (StRS) | 2 | [HIGH] |
| Statement of Work (SOW) | 1 | [HIGH; CONDITIONAL: procurement] |
| Software Accomplishment Summary (SAS) | 6 | [CONDITIONAL: DO-178C] |
| Software Architecture Document (SAD) | 3 | [HIGH] |
| Software Configuration Index (SCI) | 6 | [CONDITIONAL: DO-178C] |
| Software Development Plan (SDP) | 1–8 | [CONDITIONAL: regulated] |
| Software Life Cycle Environment Configuration Index (SECI) | 6 | [CONDITIONAL: DO-178C] |
| Software Quality Assurance Plan (SQAP) | 1–8 | [HIGH; CONDITIONAL strengthens] |
| Software Requirements Specification (SRS) | 2 | [HIGH] |
| Software Verification Plan (SVP) | 2–8 | [HIGH; CONDITIONAL] |
| SLA / SLO / SLI | 7 | [HIGH] |
| System Test Plan | 5 | [HIGH] |
| System Requirements Specification (SyRS) | 2 | [HIGH] |
| Test Case Specification | 5 | [HIGH] |
| Test Log | 5 | [HIGH] |
| Test Procedure / Script | 5 | [HIGH] |
| Test Strategy | 5 | [HIGH] |
| Test Summary Report | 5 | [HIGH] |
| Threat Model | 3–7 | [HIGH] |
| UAT Plan | 5 | [HIGH] |
| UAT Sign-off | 5 | [HIGH] |
| Unit Test Plan / Code / Results | 4–5 | [HIGH] |
| Use Case | 2 | [HIGH] |
| User Requirements Specification (URS) | 2 | [HIGH; CONDITIONAL strengthens] |
| User Story | 2 | [VARIES: Agile/SAFe] |
| VEX Document | 6–8 | [HIGH] |
| Vision / Scope Document | 1 | [MODERATE] |

---

## 11. Model-Specific Variations

### 11.1 Agile / Scrum
- **Renamed:** SRS → **Product Backlog** + **User Stories** + **Acceptance Criteria** (Scrum Guide 2020). The Scrum Guide does not define an SRS; the Product Backlog with the Product Goal commitment is the single source of work.
- **Replaced:** Big-bang HLD/LLD → **emergent design** + **ADRs** [MODERATE]. Test plans → **Definition of Done** + automated test code. Project Charter → **Product Goal**.
- **Compressed:** Phases 4, 5, 6 collapse into the Sprint, ending with a potentially releasable **Increment** that meets the **Definition of Done** (Scrum Guide 2020 — Increment is one of three artifacts; DoD is its commitment).
- **Conditional/missing:** Scrum Guide does not address operations, retirement, or formal procurement.

### 11.2 SAFe 6.0
- **Renamed:** Backlog hierarchy is explicit: **Portfolio Epic → Capability → Feature → Story** (SAFe 6.0). Project Charter → **Lean Business Case** (Epic). Vision → **Portfolio Vision / Solution Vision**.
- **Added:** **PI Objectives**, **Program Board / ART Planning Board**, **System Demo / Solution Demo**, **Inspect & Adapt** record, **Architectural Runway**, **Enabler stories/features/epics** (SAFe 6.0).
- **Compressed:** Release decoupled from cadence (**Release on Demand**); deployment automated.
- **Cross-train coordination:** Pre-PI Planning, Post-PI Planning at Solution Train (SAFe Large Solution).

### 11.3 DevOps / CI/CD
- **Renamed:** Deployment Plan → **deployment pipeline-as-code** (Humble & Farley, *Continuous Delivery* 2010); Runbooks → executable runbooks/automation; Build Manifest → **SLSA provenance**.
- **Automated:** Build, test, security scan (SAST/SCA/DAST), SBOM generation, deployment, rollback. Compliance evidence is generated by the pipeline (audit-as-code).
- **Added:** **DORA metrics** (Deployment Frequency, Lead Time for Changes, Change Failure Rate, Failed Deployment Recovery Time — DORA *State of DevOps* 2024); **Error Budget Policy**; **VEX** for vulnerability disclosure.
- **Compressed:** Phases 4–6 are continuous; phase 7 monitoring data feeds back into phase 2 backlog.
- **SSDF mapping (NIST SP 800-218 v1.1):** PO (Prepare the Organization) → cross-cutting governance; PS (Protect the Software) → CM, signing; PW (Produce Well-Secured Software) → phases 2–5; RV (Respond to Vulnerabilities) → phase 7.

### 11.4 Regulated SDLCs

#### 11.4.1 FDA — General Principles of Software Validation (GPSV v2.0, 2002) and 21 CFR Part 11
- **Mandatory artifacts:** Software validation plan; requirements (URS); design specifications; verification protocols and reports; validation reports; traceability; problem reports; configuration management; change control (FDA GPSV §5).
- **21 CFR Part 11** mandates electronic record audit trails (§11.10(e)), system validation (§11.10(a)), copies of records (§11.10(b)), record protection (§11.10(c)), authority checks (§11.10(g)), and electronic signature manifestation (§11.50, §11.70).

#### 11.4.2 IEC 62304:2006/A1:2015 — Medical Device Software Lifecycle
- **Class A/B/C** drives required artifacts (IEC 62304 §4.3).
- **Mandatory artifacts (all classes):** Software Development Plan (§5.1); Software Requirements (§5.2); Software Risk Management File integrated with ISO 14971 (§7); Software Configuration Management (§8); Software Problem Resolution (§9); Software Release documentation including residual anomaly list (§5.8).
- **Class B/C add:** Software Architecture (§5.3); Software Integration and Integration Testing (§5.6); System Testing (§5.7).
- **Class C adds:** Detailed Design (§5.4); Unit verification (§5.5); enhanced segregation analysis.
- **SOUP (Software of Unknown Provenance)** must be identified, with functional/performance requirements, hardware/software requirements, and a list of known anomalies (§5.3.3, §7.1.3).

#### 11.4.3 RTCA DO-178C / EUROCAE ED-12C — Airborne Software
- **22 life cycle data items (§11):** PSAC; Software Development Plan; Software Verification Plan; Software Configuration Management Plan; Software Quality Assurance Plan; Software Requirements Standards; Software Design Standards; Software Code Standards; Software Requirements Data (HLR); Design Description (LLR + architecture); Source Code; Executable Object Code; Software Verification Cases and Procedures; Software Verification Results; Software Life Cycle Environment Configuration Index (SECI); Software Configuration Index (SCI); Problem Reports; Software Configuration Management Records; Software Quality Assurance Records; Software Accomplishment Summary; Trace Data; Parameter Data Item Files (DO-178C §11.1–§11.22).
- **DAL A:** 71 objectives; DAL B: 69; DAL C: 62; DAL D: 26; DAL E: 0 (DO-178C Annex A).
- **Verification with independence** required for higher DALs (DO-178C Annex A tables).
- **Structural coverage:** Statement (DAL C); Decision (DAL B); Modified Condition/Decision Coverage — MC/DC (DAL A) (DO-178C §6.4.4.2).

#### 11.4.4 ISO 26262 — Road Vehicle Functional Safety
- **ASIL A–D** classification drives rigor.
- Part 6 (*Product development at the software level*) defines required work products: software safety requirements, software architectural design, software unit design and implementation, software unit verification, software integration verification, verification of software safety requirements (ISO 26262-6:2018).

### 11.5 Conflict Disclosure
- **Test documentation standard:** IEEE 829-2008 was the long-standing reference for test plans, cases, procedures, logs, summary reports. It has been **superseded by ISO/IEC/IEEE 29119** (Parts 1–5; Part 3 covers test documentation). Some industries (especially regulated ones) still cite IEEE 829 by name; modern audits accept 29119-3. Both are presented above.
- **NIST SP 800-64 Rev. 2** was withdrawn in May 2019; readers are directed to **NIST SP 800-160 Vol. 1**. Where SDLC-phase guidance is needed, the prior five-phase NIST taxonomy is widely cited but is no longer normative.
- **IEEE 1074** (developing software life cycle processes, last issued 2006) was withdrawn in 2017; ISO/IEC/IEEE 12207:2017 is the current life-cycle standard.
- **IEEE 830** for SRS was superseded by ISO/IEC/IEEE 29148:2011 and revised in 2018.
- **NIST SP 800-218 Rev. 1** is currently in initial public draft (Dec 2025); v1.1 (Feb 2022) remains the final version cited above.

---

## 12. Sources Consulted

- **ISO/IEC/IEEE 12207:2017**, *Systems and software engineering — Software life cycle processes*, ISO/IEC/IEEE, 2017.
- **ISO/IEC/IEEE 15288:2015**, *Systems and software engineering — System life cycle processes*, ISO/IEC/IEEE, 2015.
- **ISO/IEC/IEEE 29148:2018**, *Systems and software engineering — Life cycle processes — Requirements engineering* (supersedes IEEE 830-1998, IEEE 1233-1998, IEEE 1362-1998).
- **IEEE Std 1016-2009**, *IEEE Standard for Information Technology — Systems Design — Software Design Descriptions*.
- **IEEE Std 829-2008**, *IEEE Standard for Software and System Test Documentation* (superseded by ISO/IEC/IEEE 29119-3:2013).
- **ISO/IEC/IEEE 29119-1:2022 / 29119-2:2021 / 29119-3:2021**, *Software and systems engineering — Software testing*.
- **IEEE Std 1012-2016**, *IEEE Standard for System, Software, and Hardware Verification and Validation*.
- **IEEE Std 730-2014**, *IEEE Standard for Software Quality Assurance Processes*.
- **IEEE Std 828-2012**, *IEEE Standard for Configuration Management in Systems and Software Engineering*.
- **IEEE Std 1044-2009**, *IEEE Standard Classification for Software Anomalies*.
- **IEEE Std 1074** (withdrawn 2017), *IEEE Standard for Developing a Software Project Life Cycle Process*.
- **ISO/IEC 14764:2022**, *Software engineering — Software life cycle processes — Maintenance*.
- **ISO/IEC/IEEE 26511 / 26512 / 26515**, *Systems and software engineering — Documentation*.
- **ISO/IEC/IEEE 42010:2011**, *Systems and software engineering — Architecture description*.
- **SWEBOK Guide v3** (2014) and **v4** (2024), IEEE Computer Society.
- **PMBOK Guide, 7th Edition**, Project Management Institute, 2021 (governance artifacts only: Charter, Business Case, Stakeholder Register, Risk Register, Closeout).
- **NIST SP 800-218 v1.1**, *Secure Software Development Framework (SSDF) v1.1: Recommendations for Mitigating the Risk of Software Vulnerabilities*, Feb. 2022 (Rev. 1 currently IPD, Dec. 2025).
- **NIST SP 800-160 Vol. 1 Rev. 1**, *Engineering Trustworthy Secure Systems* (current reference for SDLC security; supersedes the withdrawn SP 800-64 Rev. 2 of Oct. 2008).
- **NIST SP 800-88 Rev. 1**, *Guidelines for Media Sanitization*.
- **The Scrum Guide**, Schwaber & Sutherland, Nov. 2020. https://scrumguides.org
- **SAFe 6.0** framework documentation, Scaled Agile, Inc. https://scaledagileframework.com (sections cited: Epic, Capability, Feature, Story, Enabler, PI Planning, ART, Lean Business Case, Architectural Runway).
- **DORA / *State of DevOps* Reports** (2018–2024); Forsgren, Humble & Kim, *Accelerate*, IT Revolution Press, 2018.
- **Humble & Farley**, *Continuous Delivery*, Addison-Wesley, 2010.
- **Google SRE Book** (Beyer, Jones, Petoff, Murphy eds.), O'Reilly, 2016 (Chapters 3, 4, 8, 15, 18 cited).
- **ITIL 4** Foundation, Axelos, 2019 (Incident, Change Enablement, Service Level Management practices).
- **FDA**, *General Principles of Software Validation; Final Guidance for Industry and FDA Staff*, v2.0, 11 Jan. 2002.
- **FDA**, *Computer Software Assurance for Production and Quality System Software* (final guidance, supersedes GPSV §6).
- **21 CFR Part 11**, *Electronic Records; Electronic Signatures*, U.S. Code of Federal Regulations.
- **IEC 62304:2006 / Amendment 1:2015**, *Medical device software — Software life cycle processes*.
- **ISO 14971:2019**, *Medical devices — Application of risk management to medical devices*.
- **ISO 13485:2016**, *Medical devices — Quality management systems*.
- **RTCA DO-178C / EUROCAE ED-12C**, *Software Considerations in Airborne Systems and Equipment Certification*, RTCA, Dec. 2011 (with supplements DO-330, DO-331, DO-332, DO-333).
- **FAA AC 20-115D**, *Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178*, 21 Jul. 2017.
- **ISO 26262:2018**, *Road vehicles — Functional safety* (Part 6 cited for software).
- **OWASP SAMM v2** (Software Assurance Maturity Model), OWASP Foundation. https://owaspsamm.org (Five Business Functions: Governance, Design, Implementation, Verification, Operations).
- **BSIMM** (Building Security In Maturity Model), Synopsys/Black Duck (most recent published edition).
- **CISA / NTIA**, *The Minimum Elements for a Software Bill of Materials (SBOM)*, NTIA, 12 Jul. 2021; **CISA**, *2025 Minimum Elements for a Software Bill of Materials* (draft, public comment closed 3 Oct. 2025).
- **Executive Order 14028**, *Improving the Nation's Cybersecurity*, 12 May 2021.
- **CISA VEX** documentation (Vulnerability Exploitability eXchange), 2023.
- **SLSA v1.0** (Supply-chain Levels for Software Artifacts), Open Source Security Foundation.
- **NASA Systems Engineering Handbook** (NASA SP-2016-6105 Rev. 2) — referenced for ICD content.
- **Boehm, B.**, "A Spiral Model of Software Development and Enhancement," *IEEE Computer* 21(5), 1988.
- **Royce, W.**, "Managing the Development of Large Software Systems," *Proc. IEEE WESCON*, 1970.
- **Kruchten, P.**, "The 4+1 View Model of Architecture," *IEEE Software*, 1995.
- **Nygard, M.**, "Documenting Architecture Decisions," 2011.
- **arc42** architecture documentation template, https://arc42.org.
- **Wiegers, K. & Beatty, J.**, *Software Requirements*, 3rd Ed., Microsoft Press, 2013.
- **Cockburn, A.**, *Writing Effective Use Cases*, Addison-Wesley, 2001.
- **GAMP 5 Second Edition**, ISPE, 2022.

Access date for online sources: 1 May 2026.