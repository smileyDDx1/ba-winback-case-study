# Customer win-back and data-capture initiative: a BA case study

A business analysis case study built on my [e-commerce analytics project](https://github.com/smileyDDx1/ecommerce-analytics)
([live dashboard](https://smileyddx1.github.io/ecommerce-analytics/dashboard/index.html)). The analysis showed
*what* is going wrong: good customers lapse, and a big slice of sales can't be tied to any customer. This case study
works out *what the business should do about it*, written up the way a BA hands work to a delivery team: business
case, stakeholders, process maps, BRD, user stories, KPIs with SQL, and a UAT plan.

> **Note:** the retailer, stakeholders and meetings are hypothetical. Every number comes from my analysis of the
> public [Online Retail II dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii) (UCI #502): one UK
> online retailer, Dec 2009 to Dec 2011, about 1.07M line items.

## The problem in two numbers

- **888 At-Risk customers** used to order often (6.5 orders each on average) and brought in **£2.19M, 10.7% of
  sales**, but haven't ordered for **about 275 days** on average.
- **£2.94M of sales, about 14%**, has no customer ID, so it can't be used for segmentation, retention analysis or
  targeting.

## What's in here

| # | Document | What it answers |
|---|---|---|
| 1 | [Business case](01-business-case.md) | Why act; objectives, scope, options, sizing, risks |
| 2 | [Stakeholders](02-stakeholders.md) | Who is involved, who decides (RACI), how they're kept informed |
| 3 | [Process maps](03-process-maps.md) | As-is vs to-be flows, as Mermaid diagrams |
| 4 | [BRD](04-brd.md) | Numbered business, functional, data and non-functional requirements |
| 5 | [User stories](05-user-stories.md) | 12 stories with Given / When / Then acceptance criteria and MoSCoW priority |
| 6 | [KPIs](06-kpis.md) | Metric definitions, baselines and targets, with SQL against the analytics schema |
| 7 | [UAT plan](07-uat-plan.md) | 15 test cases and a traceability matrix back to the requirements |

Also: [`checks/check_kpi_sql.py`](checks/check_kpi_sql.py) tests every KPI query on a small hand-made data set;
[interview Q&A](docs/questions-answers.md); [future plans](docs/future-plans.md).

## How I approached it

1. Started from the analysis results (RFM segments, cohort retention, data-quality counts), not from opinions.
2. Picked two problems that are measurable and fixable in one phase: win back At-Risk customers, and stop losing
   the customer ID on new orders. Onboarding for new customers went to phase 2.
3. Sized the win-back with low, base and high scenarios and wrote every assumption down.
4. Broke the scope into requirements, then user stories, then UAT cases, with IDs so every test traces back to a
   requirement.
5. Wrote the KPI SQL on the same schema as the analysis, and checked it on test data where I knew the answers.

## Key decisions

- **A 10% control group**, so the campaign's effect is measured, not assumed. Without it, seasonality would swamp
  the result: November 2011 sales were almost 3x February's.
- **Segments must be reproducible.** The analysis's per-customer export lists 895 At-Risk customers but its summary
  lists 888: the quartile function splits tied customers arbitrarily, so customers on a boundary can change segment
  between two runs. FR-02 fixes this by breaking ties on customer ID, and the SQL check proves it with three
  customers tied across a quartile boundary.
- **Measure unattributed sales by value, not by row count**, because the business cares about the money it can't
  target. (By rows the gap is about 23%; by value about 14%.)
- **Per-customer averages for uplift**, so the 90% / 10% group sizes don't distort the comparison.

## What I learned

- Writing acceptance criteria forces exact definitions. "Reactivated" became "at least one sale from the start
  date up to, but not including, day 90, with cancelled orders and returns not counted", and each part of that
  definition has its own test.
- Ranges with stated assumptions are easier to defend than one big number, and they show which assumption matters
  most: here, the uplift.
- A test is only useful if it can fail. My first version of the SQL check passed even with the cancellation filter
  removed, because my test cancellation only had a negative line. Breaking the SQL on purpose showed the gap, and I
  fixed the test data.

## Limitations

- Stakeholders, consent status and costs are assumptions; a real project would confirm them in interviews first.
- The data ends in December 2011, so the campaign can't actually run. The KPI SQL is tested on synthetic data,
  not on campaign results.
- The as-is process is partly assumed (marked in the documents) and would be checked with the teams involved.
