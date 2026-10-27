# 5. User stories

Each story has acceptance criteria in Given / When / Then form and traces to the [BRD](04-brd.md) and the
[UAT plan](07-uat-plan.md).

| Priority | Stories |
|---|---|
| Must | US-01 to US-09 |
| Should | US-10, US-11 |
| Could | US-12 |
| Won't (this phase) | Onboarding emails for new customers, SMS, reminders for Lost customers |

Most stories are Must because the scope was cut to the minimum needed for a test that is valid (control group,
consistent segments) and legal (consent). Everything else moved to Won't.

---

### US-01 Weekly At-Risk list · Must
**As a** CRM manager **I want** a fresh list of At-Risk customers every Monday **so that** I can start win-back
emails without asking the BI team each time.

- **Given** sales data up to the snapshot date, **when** the Monday 06:00 refresh runs, **then** the list contains
  every customer with an R score of 1-2 and an F score of 3-4.
- **Given** the list, **when** I open it, **then** each row shows customer ID, last order date, number of orders
  and lifetime revenue.
- **Given** a customer whose latest invoice is cancelled, **when** the refresh runs, **then** the cancellation does
  not change their recency or their order count.

*Traces to:* FR-01, FR-04 · UAT-01

### US-02 Same data, same segments · Must
**As a** BI analyst **I want** ties in the scoring broken the same way every time **so that** a customer's segment
never changes between two runs on the same data.

- **Given** customers with the same number of orders on a quartile boundary, **when** the refresh runs twice,
  **then** each of them gets the same segment both times.
- **Given** the same snapshot loaded in a different row order, **when** the refresh runs, **then** 100% of
  customers get the same segment.

*Why:* in the analysis, the per-customer export lists 895 At-Risk customers but the summary lists 888, because
the quartile function split tied customers differently in the two queries.
*Traces to:* FR-02 · UAT-02

### US-03 Only email people we may email · Must
**As the** Data Protection Officer **I want** customers without consent, unsubscribed or with bounced emails left
out automatically **so that** the campaign stays within UK GDPR and PECR.

- **Given** an At-Risk customer with no marketing consent and no soft opt-in, **when** the audience is built,
  **then** they are excluded with the reason "no consent".
- **Given** a customer who has unsubscribed, **when** the audience is built, **then** they are excluded with the
  reason "unsubscribed".
- **Given** a customer clicks unsubscribe in any win-back email, **when** 48 hours have passed, **then** they get
  no further emails.

*Traces to:* FR-04, NFR-02 · UAT-04, UAT-14

### US-04 Control group · Must
**As a** CRM manager **I want** a random 10% of the audience held back **so that** I can measure what the emails
really changed.

- **Given** an audience of 1,000 customers, **when** the split runs, **then** between 9% and 11% are in control
  and the rest in treatment.
- **Given** the split, **when** the emails are sent, **then** no control customer receives a win-back email.
- **Given** the split, **then** every assignment is saved with the campaign ID, start date and rules version before
  the first email goes out.

*Traces to:* FR-05, DR-03, NFR-04 · UAT-05

### US-05 Three emails with an offer · Must
**As a** customer who hasn't ordered in a while **I want** a friendly reminder and a reason to come back **so
that** returning feels worth it.

- **Given** I am in the treatment group, **when** the campaign starts, **then** I get email 1 on day 0, email 2
  with my discount code on day 7, and email 3 on day 14.
- **Given** my code, **when** I use it once, **then** 10% comes off my order.
- **Given** I have used my code, or 30 days have passed, **when** I try it again, **then** it is rejected with a
  clear message.

*Traces to:* FR-06, FR-09 · UAT-06

### US-06 Stop emails after an order · Must
**As a** customer **I want** the reminders to stop once I've ordered **so that** I don't get offers for something
I've already done.

- **Given** I am in the treatment group, **when** I place an order on day 3, **then** I don't receive the day 7 or
  day 14 emails.

*Traces to:* FR-07 · UAT-07

### US-07 Guest checkout asks for an email · Must
**As a** guest shopper **I want** to check out with just my email **so that** I don't have to create an account.

- **Given** I check out as a guest, **when** I leave the email blank or type an invalid one, **then** I can't
  continue and I see what to fix.
- **Given** I enter a valid email, **when** I pay, **then** my order is saved with a customer ID.

*Traces to:* FR-10 · UAT-09

### US-08 Recognise returning guests · Must
**As a** CRM manager **I want** guest orders linked to the existing customer with the same email **so that**
returning guests count in their own history.

- **Given** a customer exists with `ana@example.com`, **when** a guest checks out with `" Ana@Example.com "`,
  **then** the order is saved with that customer's ID and no new customer is created.

*Traces to:* FR-11, DR-04 · UAT-10

### US-09 New guests become customers · Must
**As a** BI analyst **I want** a customer record created for a new guest email **so that** their next order joins
the same history.

- **Given** no customer has `new@example.com`, **when** a guest checks out with it, **then** a customer record
  flagged as guest is created and the order uses its ID.
- **Given** that record exists, **when** the same email checks out again, **then** the second order gets the same
  ID.

*Traces to:* FR-12 · UAT-11

### US-10 Campaign results dashboard · Should
**As the** Head of E-commerce **I want** treatment and control results side by side **so that** I can decide at
day 90 whether to keep the programme.

- **Given** the campaign has run for some weeks, **when** I open the dashboard, **then** I see audience size,
  reactivation rate and revenue per customer for each group, and the uplift.
- **Given** the weekly snapshots, **when** I open the dashboard, **then** I can see how many At-Risk customers moved
  to another segment.
- **Given** any figure on the dashboard, **when** the BI analyst runs the KPI SQL on the same data, **then** the
  numbers match exactly.

*Traces to:* FR-13, FR-03 · UAT-12, UAT-03

### US-11 Data-capture trend · Should
**As the** Web Product Owner **I want** a monthly chart of sales without a customer ID **so that** I can see
whether the checkout change worked.

- **Given** the checkout release date, **when** I open the chart, **then** each month shows the share of sales with
  no customer ID, and the release date is marked.

*Traces to:* FR-14 · UAT-13

### US-12 Personal product picks · Could
**As a** lapsed customer **I want** the first email to show products I used to buy **so that** it feels relevant
rather than generic.

- **Given** my order history, **when** email 1 is built, **then** it shows my three most-bought products by
  quantity, skipping any no longer on sale.

*Traces to:* FR-08 · UAT-08
