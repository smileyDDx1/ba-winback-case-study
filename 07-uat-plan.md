# 7. UAT plan

User acceptance testing checks that the build does what the business asked for, in the business's own words. The
BA coordinates it, business users run the cases, and the sponsor signs off.

## 7.1 Approach

- **Where:** staging environment, with test inboxes and a time-shifted test mode for the email sequence.
- **When:** one week, after system testing has passed. A 15-minute defect triage each day.
- **Test data:**
  - **Set A:** the 8 customers from the [KPI SQL check](06-kpis.md#68-how-the-sql-was-checked), with known
    recency and frequency (At-Risk = customers 5 and 8).
  - **Set B:** 1,000 synthetic At-Risk customers, five of them flagged for each exclusion rule.
  - Three internal test inboxes.
- **Not covered by UAT:** NFR-01 (performance) is covered by system testing. NFR-05 (checkout guardrail) is
  monitored for 4 weeks after go-live.

## 7.2 Roles

| Who | Runs |
|---|---|
| BI Analyst | UAT-01, 02, 03, 12, 13, 15 |
| CRM & Email Marketing Manager | UAT-04 to 08, 14 |
| Web Product Owner | UAT-09 to 11 |
| BA (me) | Writes the cases, coordinates, tracks defects, collects sign-off |
| Head of E-commerce | Final sign-off |

## 7.3 Entry and exit criteria

**Entry:** build complete and system-tested; data sets A and B loaded; DPO has approved the consent rules (D-01);
testers have access to staging, the test inboxes and the dashboard.

**Exit:** every Must case passed; no open Critical or High defects; Medium defects have an agreed fix date;
sponsor sign-off recorded.

## 7.4 Test cases

| ID | Scenario | Steps | Expected result | Traces to |
|---|---|---|---|---|
| UAT-01 | At-Risk list follows the rules | Load set A; run the refresh | List holds customers 5 and 8 only; customer 3's cancelled invoice doesn't change its recency | FR-01, FR-04, US-01 |
| UAT-02 | Same data, same segments | Load set A twice, in different row orders; run the refresh on each | Every customer gets the same segment in both runs, including customer 8, who ties with customers 4 and 6 on order count | FR-02, US-02 |
| UAT-03 | Segment history is kept | Run the refresh for two weeks, with an order from customer 5 in between | History shows customer 5 At-Risk in week 1 and another segment in week 2; dashboard counts 1 movement | FR-03, US-10 |
| UAT-04 | Exclusions work and are logged | Build the audience from set B | The flagged customers (no consent, unsubscribed, hard bounce, open complaint, in a win-back in the last 90 days) are excluded, each with the right reason | FR-04, NFR-02, US-03 |
| UAT-05 | Control group | Split the set B audience; start the test campaign | 9% to 11% in control; assignments saved with campaign ID, start date and rules version before the send; zero emails to control | FR-05, DR-03, NFR-04, US-04 |
| UAT-06 | Email timing and code rules | Start the sequence for the test inboxes | Emails on day 0, 7 and 14; the code takes 10% off once; a second use and a use on day 31 are rejected with a message | FR-06, FR-09, US-05 |
| UAT-07 | Emails stop after an order | Test inbox orders on day 3 | No day 7 or day 14 email | FR-07, US-06 |
| UAT-08 | Product picks in email 1 | Test customer bought A ×5, B ×3, C ×2, D ×1; B is no longer on sale | Email 1 shows A, C and D | FR-08, US-12 |
| UAT-09 | Guest checkout needs a valid email | Guest checkout with a blank email, then `ana@`, then a valid email | Blank and invalid are blocked with a message; valid continues; order saved with a customer ID | FR-10, US-07 |
| UAT-10 | Returning guest is recognised | Customer `ana@example.com` exists; guest checks out with `" Ana@Example.com "` | Order has the existing customer ID; no duplicate customer | FR-11, DR-04, US-08 |
| UAT-11 | New guest gets a record | Guest checks out twice with `new@example.com` | One new customer flagged as guest; both orders share its ID | FR-12, US-09 |
| UAT-12 | Dashboard matches the SQL | Open the dashboard for the test campaign; BI analyst runs KPI-2 and KPI-3 on the same data | Identical numbers; no customer-level personal data on the dashboard | FR-13, NFR-06, US-10 |
| UAT-13 | Data-capture chart | Load a month with known guest and customer sales | The chart's share equals the KPI-4 result; the release date is marked | FR-14, US-11 |
| UAT-14 | Unsubscribe is honoured | Test inbox unsubscribes after email 1 | No further emails; suppression applied within 48 hours | NFR-02, US-03 |
| UAT-15 | Failed refresh is handled | Make the database unavailable during the Monday refresh | No audience created that week; BI analyst alerted by 07:00 | NFR-03 |

## 7.5 Defect severity

| Severity | Meaning | Example |
|---|---|---|
| Critical | Wrong people contacted, or orders lost. Stops UAT. | A control or no-consent customer receives an email |
| High | Wrong numbers or broken rules, no workaround | Sequence doesn't stop after an order; dashboard differs from the SQL |
| Medium | Wrong but with a workaround | Product picks missing from email 1 |
| Low | Cosmetic | Typo in an email |

## 7.6 Requirements traceability matrix

| Business requirement | Requirements | User stories | UAT cases | KPIs |
|---|---|---|---|---|
| BR-01 Spot lapsing frequent customers every week | FR-01, FR-02, FR-03, NFR-01, NFR-03 | US-01, US-02 | UAT-01, UAT-02, UAT-03, UAT-15 | KPI-1 |
| BR-02 Win them back with a measurable effect | FR-04 to FR-09, DR-02, DR-03, NFR-02, NFR-04 | US-03 to US-06, US-12 | UAT-04 to UAT-08, UAT-14 | KPI-2, KPI-3 |
| BR-03 Tie every new online order to a customer | FR-10 to FR-12, DR-04, NFR-05 | US-07 to US-09 | UAT-09 to UAT-11 | KPI-4 |
| BR-04 Show the results to decision-makers | FR-13, FR-14, DR-01, DR-05, NFR-06 | US-10, US-11 | UAT-12, UAT-13 | KPI-1 to KPI-5 |

Every functional and non-functional requirement has at least one UAT case, except NFR-01 and NFR-05 (covered as
noted in 7.1). DR-05 (how long data is kept) is checked in the DPO's retention review, not in UAT.
