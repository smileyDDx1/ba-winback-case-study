# 2. Stakeholders

These are hypothetical roles for a mid-sized online retailer. The interests below are my assumptions; in a real
project I would confirm them in short interviews before writing the requirements.

## 2.1 Stakeholder register

| Stakeholder | Role in this initiative | Interest | Influence | What they need from the BA |
|---|---|---|---|---|
| Head of E-commerce | Sponsor; approves the budget and the day-90 decision | High | High | Business case, day-90 results |
| CRM & Email Marketing Manager | Owns the campaign and the audience rules | High | High | Audience list, rules, content brief, results |
| Web Product Owner | Owns the checkout change | Medium | High | Guest-checkout requirements, UAT cases |
| Data Protection Officer (DPO) | Signs off consent and data use; can block the send | Medium | High | Audience rules, data kept, retention period |
| Finance Manager | Approves the discount budget; reports revenue | Low | High | Cost estimate, incremental-revenue method |
| Data / BI Analyst | Builds the segment refresh, KPI queries and dashboard | High | Low | Exact definitions, SQL, acceptance criteria |
| Customer Service Lead | Handles replies, complaints and unsubscribe requests | Medium | Low | Offer terms, FAQ, escalation path |
| Web Developer | Builds the checkout change | Low | Low | Clear stories and edge cases |

## 2.2 Power / interest grid

| | Lower interest | Higher interest |
|---|---|---|
| **Higher influence** | **Keep satisfied:** DPO, Finance Manager, Web Product Owner | **Manage closely:** Head of E-commerce, CRM & Email Marketing Manager |
| **Lower influence** | **Monitor:** Web Developer | **Keep informed:** Data / BI Analyst, Customer Service Lead |

## 2.3 RACI

R = Responsible (does the work), A = Accountable (one owner who signs off), C = Consulted, I = Informed.

| Activity | Head of E-com | CRM Mgr | Web PO | DPO | Finance | BI Analyst | CS Lead | Web Dev | BA |
|---|---|---|---|---|---|---|---|---|---|
| Approve the business case | A | C | C | C | C | I | I | – | R |
| Define segment and audience rules | I | A | – | C | – | C | – | – | R |
| Approve consent rules | I | C | – | A, R | – | – | – | – | C |
| Build the weekly segment refresh | I | A | – | – | – | R | – | – | C |
| Write email content and offer terms | I | A, R | – | C | C | – | C | – | C |
| Run the campaign and the control group | I | A, R | – | – | – | C | I | – | C |
| Guest-checkout email capture | I | C | A | C | – | – | I | R | C |
| UAT | A | R | R | – | – | R | – | C | R |
| Day-90 results and go / no-go | A | R | I | – | C | R | I | – | R |

## 2.4 Communication plan

| What | Who | When |
|---|---|---|
| 15-minute stand-up during build and UAT | CRM Mgr, Web PO, BI Analyst, Web Dev, BA | Daily |
| Status note: progress, risks, decisions needed | Head of E-commerce, Finance, DPO | Every two weeks |
| Campaign dashboard | Head of E-commerce, CRM Mgr | Weekly, from launch |
| Day-90 readout and go / no-go | All stakeholders | Day 90 |
