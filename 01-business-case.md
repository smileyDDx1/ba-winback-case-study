# 1. Business case: customer win-back and data capture

| | |
|---|---|
| **Author** | Debangshu Das |
| **Version** | 1.0, 27 Oct 2026 |
| **Status** | Draft for review. Portfolio case study: the retailer and stakeholders are hypothetical |
| **Data** | Online Retail II (UCI #502), 1 Dec 2009 to 9 Dec 2011, analysed in [ecommerce-analytics](https://github.com/smileyDDx1/ecommerce-analytics) |

## 1.1 Background

The retailer is a UK online shop selling giftware to consumers and small businesses. Over two years it took
**£20.48M** in sales from **5,878** identified customers. Repeat buying is healthy overall: 72% of customers ordered
more than once. The analysis still points to two problems that cost money today.

## 1.2 Problem statements

**P1. Valuable customers are lapsing, and nothing reacts.**
888 customers sit in the At-Risk segment. They ordered often (6.5 orders each on average) and brought in
**£2.19M, 10.7% of all sales**, but their last order was **about 275 days ago** on average, and at least three
months ago for each of them. Nothing in the current process notices when a good customer goes quiet.
*(Assumed as-is: one newsletter goes to every subscriber. To confirm with the CRM manager.)*

**P2. One pound in seven can't be tied to a customer.**
235,151 line items (about 23% of rows) have no customer ID. They are worth **£2.94M, about 14% of sales**, or
roughly £1.45M a year. Those orders are invisible to segmentation, retention reporting and campaign targeting.

**Context, not in scope:** average month-1 retention is **21.2%**. In a typical monthly cohort, only about one
new customer in five orders again the next calendar month. That is an onboarding problem for phase 2
([future plans](docs/future-plans.md)).

## 1.3 Objectives

| ID | Objective | Measure | Target |
|---|---|---|---|
| O1 | Win back lapsed, previously frequent customers | Reactivation rate, treatment minus control, 90 days (KPI-2) | +5 percentage points or more |
| O2 | Show the campaign pays for itself | Incremental revenue in 90 days vs discount cost (KPI-3) | At least 3x the discount cost |
| O3 | Tie new sales to customers | Share of monthly sales with no customer ID (KPI-4) | Under 5% within 6 months of the checkout release (baseline ~14%) |
| O4 | Make segments trustworthy | Two runs on the same data give every customer the same segment (FR-02) | 100% match |

## 1.4 Scope

**In scope**
- A weekly RFM segment refresh that breaks ties the same way every run, and an At-Risk audience list.
- A three-email win-back sequence for At-Risk customers who may be emailed, with a 10% random control group and
  a single-use 10% discount in the second email.
- Guest checkout that asks for an email and links the order to a customer record.
- A results dashboard covering the campaign and the data-capture fix.

**Out of scope for this phase**
- New-customer onboarding and month-1 retention (phase 2).
- Loyalty or VIP programmes for Champions.
- Back-filling customer IDs on past orders: the data has no reliable key to match them.
- Channels other than email, and price or range changes.

## 1.5 Options considered

| Option | For | Against | Decision |
|---|---|---|---|
| A. Do nothing | No cost | At-Risk customers keep drifting away; ~£1.45M a year of sales stays untargetable | Rejected |
| B. Discount email to every lapsed customer (At-Risk and Lost, 2,940 people), no control group | Widest reach | Discounts go to people who would have come back anyway; no way to prove the effect; Lost customers bought only ~1.5 times each | Rejected |
| C. Targeted At-Risk win-back with a control group, plus email capture at guest checkout | Measurable, cheap to run, fixes the data gap for future orders | Smaller reach; needs a checkout change | **Recommended** |

## 1.6 Sizing the win-back

**Inputs from the analysis:** 888 At-Risk customers; average order value for the segment about **£378**
(£2.19M ÷ (888 × 6.53 orders)); historic pace about **3 orders a year** (6.5 orders over two years).

**Assumptions** (each one is either measured by the control group or listed as a risk):
- All 888 can be emailed. Consent is not checked yet (risk R1).
- With a 10% control group, **799** customers are emailed and **89** are held back.
- A reactivated customer places one order in the 90-day window, at the segment average.
- Customers who would come back anyway (the baseline) are unknown; the control group measures them. For the
  discount cost I assume 5%.

| Scenario | Uplift vs control | Extra customers (of 799) | Extra revenue in 90 days | Discount cost | Yearly value if they return to ~3 orders a year |
|---|---|---|---|---|---|
| Low | +5 pts | 40 | £15k | £3.0k | £45k |
| **Base** | **+10 pts** | **80** | **£30k** | **£4.5k** | **£91k** |
| High | +15 pts | 120 | £45k | £6.0k | £136k |

*Discount cost = 10% of a first order (£37.80) for every customer who redeems, that is (5% baseline + uplift) ×
799. Emails go out on the existing platform, so sending cost is left out.*

Even the low scenario covers the discount cost five times, so the test itself is low-risk. The bigger prize is the
yearly value if win-backs stick, which is why the results are reviewed at day 90 before anything is scaled.

**The data-capture fix** does not create revenue by itself. It turns about £1.45M a year of anonymous sales into
sales that can be analysed and targeted, and stops the gap growing.

## 1.7 Key risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | Some At-Risk customers have no marketing consent | Smaller audience; legal exposure | Consent check in the audience rules (FR-04); DPO sign-off before the first send |
| R2 | Discounts teach customers to wait for offers | Lower margin | Offer only in email 2, single use, 30 days; effect measured against control |
| R3 | Seasonality hides the effect (Nov 2011 sales were ~3x Feb 2011) | Wrong conclusion | Treatment and control are measured over the same weeks |
| R4 | A required email field at guest checkout loses sales | Lower conversion | Checkout completion watched daily; roll back if it drops more than 1 point (NFR-05) |
| R5 | The 235k rows without an ID are not web guest orders (e.g. phone or wholesale orders, adjustments) | The checkout fix doesn't move KPI-4 | Profile those rows by channel before build (open question Q1 in the [BRD](04-brd.md)) |

## 1.8 Recommendation

Approve **option C** as a single 90-day test. At day 90 the sponsor decides: make it a monthly programme if the
uplift is at least +5 points and incremental revenue is at least 3x the discount cost; otherwise stop and review
the offer and the audience.

**Next steps:** confirm consent data with the DPO → profile the rows without a customer ID (Q1) → build the
segment refresh and the checkout change → UAT ([plan](07-uat-plan.md)) → launch.
