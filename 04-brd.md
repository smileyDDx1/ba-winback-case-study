# 4. Business requirements document (BRD)

| | |
|---|---|
| **Initiative** | Customer win-back and data capture |
| **Author** | Debangshu Das |
| **Version** | 1.0, 27 Oct 2026 (draft for review) |
| **Related** | [Business case](01-business-case.md) · [User stories](05-user-stories.md) · [KPIs](06-kpis.md) · [UAT plan](07-uat-plan.md) |

## 4.1 Purpose

This document lists what the business needs from the win-back campaign and the guest-checkout change, so the
CRM, web and BI teams can build it and the sponsor can sign it off. The reasons and the sizing are in the
[business case](01-business-case.md).

## 4.2 Glossary

| Term | Meaning |
|---|---|
| RFM | Recency (days since the last order), Frequency (number of orders), Monetary (total spend). Each is scored 1 to 4 by quartile; 4 is best. |
| At-Risk | Customers with an R score of 1-2 (ordered longest ago) and an F score of 3-4 (ordered most often). |
| Snapshot date | The latest sale date in the data when the segments are calculated. |
| Treatment / control | Customers who get the emails / a random 10% who don't, so the two can be compared. |
| Reactivated | See DR-02. |
| Uplift | Treatment reactivation rate minus control reactivation rate, in percentage points. |
| Unattributed sales | Sales on invoices with no customer ID. |
| Soft opt-in | UK rule (PECR) that lets a business email existing customers about similar products, if they were offered a way to opt out when their details were collected and in every message since. |

## 4.3 Business requirements

| ID | The business needs to... |
|---|---|
| BR-01 | Spot lapsing, previously frequent customers every week. |
| BR-02 | Win them back with a campaign whose effect can be measured. |
| BR-03 | Tie every new online order to a customer. |
| BR-04 | Show the results to the people who decide whether to continue. |

## 4.4 Functional requirements

Priority uses MoSCoW: **M**ust, **S**hould, **C**ould, **W**on't (this phase).

| ID | Requirement | Priority | Source | Stories |
|---|---|---|---|---|
| FR-01 | Every Monday at 06:00, recalculate R, F and M scores for all identified customers from sales up to the snapshot date, using the quartile rules from the analysis (`rfm.sql`). | M | BR-01 | US-01 |
| FR-02 | Break ties in the R and F scoring by customer ID, so two runs on the same data put every customer in the same segment. | M | BR-01 | US-02 |
| FR-03 | Keep every customer's segment for each weekly snapshot, so movements such as At-Risk to Loyal can be counted. | S | BR-01, BR-04 | US-10 |
| FR-04 | Build the win-back audience from At-Risk customers, excluding anyone who has no marketing consent or soft opt-in, has unsubscribed, has a hard-bounced email, has an open complaint, or was in a win-back audience in the last 90 days. Log the reason for every exclusion. | M | BR-02 | US-01, US-03 |
| FR-05 | Randomly put 10% of the audience in a control group that gets no win-back email, and save the assignment (DR-03) before the first email is sent. | M | BR-02 | US-04 |
| FR-06 | Send the treatment group three emails: day 0 (we miss you), day 7 (discount code) and day 14 (last reminder). | M | BR-02 | US-05 |
| FR-07 | Stop a customer's remaining emails as soon as they place an order. | M | BR-02 | US-06 |
| FR-08 | Show the customer's three most-bought products (by quantity) in email 1, skipping any no longer on sale. | C | BR-02 | US-12 |
| FR-09 | The discount code is unique to the customer, single use, 10% off, valid for 30 days, and can't be combined with other offers. | M | BR-02 | US-05 |
| FR-10 | Guest checkout requires a valid email address before payment. | M | BR-03 | US-07 |
| FR-11 | If the guest email matches an existing customer (ignoring case and spaces at either end), save the order with that customer ID. | M | BR-03 | US-08 |
| FR-12 | If it matches no customer, create a customer record flagged as guest and save the order with the new ID. | M | BR-03 | US-09 |
| FR-13 | A dashboard shows KPI-1 to KPI-3 for treatment and control side by side, updated weekly, plus segment movements (FR-03). | S | BR-04 | US-10 |
| FR-14 | A monthly chart shows the share of sales with no customer ID (KPI-4), with the checkout release date marked. | S | BR-04 | US-11 |

## 4.5 Data requirements

| ID | Requirement |
|---|---|
| DR-01 | A **sale** is a line on a non-cancelled invoice with revenue above zero (the same rule as the analysis). |
| DR-02 | A customer is **reactivated** if they have at least one sale from the campaign start date up to, but not including, day 90. |
| DR-03 | New table `winback_audience` (campaign_id, customer_id, group_name, start_date, rules_version), written once per batch before any email is sent and never updated. DDL in [KPIs](06-kpis.md). |
| DR-04 | The customer email is the matching key at checkout. It is stored trimmed and in lower case, with one customer per email. |
| DR-05 | Weekly segment snapshots and audience tables are kept for 24 months, then deleted (to confirm with the DPO). |

## 4.6 Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Performance | The weekly refresh finishes within 30 minutes for up to 50,000 customers. |
| NFR-02 | Compliance | Only customers with valid marketing consent or soft opt-in are emailed. Every email has a one-click unsubscribe, applied within 48 hours. The DPO signs off the rules. |
| NFR-03 | Reliability | If the refresh fails or runs late, no audience is created that week and the BI analyst gets an alert by 07:00. |
| NFR-04 | Auditability | Every audience row stores the campaign ID, start date and rules version (DR-03), and is never changed after the send. |
| NFR-05 | Checkout guardrail | For 4 weeks after release, checkout completion is compared daily with the 4 weeks before. If it drops by more than 1 percentage point, the email field goes back to optional while the cause is reviewed. |
| NFR-06 | Privacy | Dashboards show totals only. Customer-level lists are open to the CRM and BI roles only. |

## 4.7 Assumptions, constraints and dependencies

**Assumptions**
- A-01: The email platform can import a list, run a timed sequence and stop it on a purchase event.
- A-02: Consent and unsubscribe flags exist for each customer and can be joined on customer ID.
- A-03: The web platform allows changes to the guest-checkout fields.
- A-04: Online orders and the analytics database use the same customer IDs.

**Constraints**
- C-01: One 90-day test before any decision to scale.
- C-02: Discount budget of about £4.5k (base case), signed off by Finance.
- C-03: Past orders are not back-filled with customer IDs.

**Dependencies**
- D-01: DPO sign-off on the consent rules before the first send.
- D-02: The checkout change can ship separately from the campaign; neither blocks the other.

## 4.8 Open questions

| ID | Question | Why it matters | Owner |
|---|---|---|---|
| Q1 | What are the 235k rows without a customer ID: web guest orders, phone orders, wholesale invoices or adjustments? | Decides whether FR-10 to FR-12 actually close the gap | BI Analyst |
| Q2 | Do we hold valid consent for business customers, many of whom are small shops? | Sets the real audience size | DPO |
| Q3 | Is 10% the right offer, or should a later test compare no discount with 10%? | Margin vs response | CRM Manager |
| Q4 | Who owns the dashboard after the test? | Keeps the KPIs alive | Head of E-commerce |

## 4.9 Out of scope (Won't, this phase)

Onboarding emails for new customers, SMS and paid-social channels, reminders for Lost customers, loyalty or VIP
programmes, and back-filling customer IDs on past orders. See [future plans](docs/future-plans.md).
