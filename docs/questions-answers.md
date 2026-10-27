# Questions and answers

Notes for explaining this case study in an interview.

**Is this a real project?**
No. It's a case study I designed on top of my e-commerce analytics project. The retailer, stakeholders and
meetings are hypothetical; every number comes from my analysis of the public Online Retail II data.

**What is RFM, and how is "At-Risk" defined?**
Recency (days since the last order), Frequency (number of orders) and Monetary (total spend). Each customer gets a
1 to 4 score for each, by quartile, where 4 is best. At-Risk means R is 1-2 (they ordered longest ago) and F is 3-4
(they ordered most often): people who used to buy a lot and have stopped.

**Why At-Risk customers and not Lost ones?**
At-Risk customers ordered 6.5 times on average and spent about £2,470 each before going quiet. Lost customers
ordered about 1.5 times, spent about £550, and have been gone for about 410 days. At-Risk is the group most likely
to come back and most valuable when they do. Lost customers could get a cheaper, no-discount test later.

**Why a control group? Isn't it a waste not to email 10% of them?**
Without it I can't separate the campaign's effect from customers who would have come back anyway, or from
seasonality (November sales are almost 3x February's). Holding back 89 customers is a small price for a result the
sponsor can trust.

**Is a control group of 89 big enough?**
Only for a clear effect. If 5% of the control group comes back and 10% of the treatment group does, the
difference is about two standard errors, which is just at the usual confidence bar. That's why the target is +5
points, and why running the campaign monthly, so the control groups add up, gives a firmer answer over time.

**How did you size the opportunity?**
The segment's average order is about £378 (£2.19M across 888 customers × 6.53 orders). With 799 customers emailed,
each extra 5 points of reactivation is about 40 customers. If each places one order in 90 days, that's about £15k
per 5 points. The discount costs 10% of each redeemed first order. I showed low, base and high scenarios rather
than a single number.

**Why 90 days?**
At-Risk customers placed about 6.5 orders over two years, roughly one every three to four months, so 90 days is
about one normal buying cycle: long enough for a returning customer to order, short enough to decide quickly.

**What did you find about the segments not matching?**
The analysis's per-customer export lists 895 At-Risk customers and its summary lists 888. NTILE splits customers
with the same value arbitrarily, and the two queries split them differently. That's a trust problem: a customer
could be emailed one week and not the next on the same data. FR-02 requires a tie-break on customer ID. Another
fix would be fixed thresholds (for example, "no order in 90+ days"), so tied customers always get the same score;
I kept the quartiles to stay consistent with the analysis.

**Why make email required at guest checkout? Won't that lose sales?**
Most shops already ask for an email to send the order confirmation, so it's usually a small change, but it's still
a risk. NFR-05 compares checkout completion daily for 4 weeks after release and puts the field back to optional if
completion drops by more than 1 point.

**What's the difference between the BRD and the user stories?**
The BRD says what the business needs and why, with the rules and constraints, and it's what gets signed off. User
stories slice it into small pieces a team can build and test, each with acceptance criteria. Every story traces
back to a requirement in the traceability matrix in the UAT plan.

**Why are most stories "Must"?**
I cut the scope to the minimum needed for a test that is valid (control group, consistent segments) and legal
(consent). Everything else went to Won't for this phase, rather than sitting in the backlog as a false "Should".

**What is soft opt-in?**
A UK PECR rule that lets a business email its existing customers about similar products, as long as they were given
a simple way to opt out when their details were collected and in every message since. The DPO confirms which
customers qualify; I wouldn't decide that myself.

**What if the control group comes back as much as the treatment group?**
Then the emails didn't change behaviour, and the discount was wasted on people who would have returned anyway.
I'd stop the discount and test a different message, timing or audience before spending more. Finding that out
cheaply is the whole point of the test.

**What would you do first in a real project?**
Answer open question Q1: what the 235k rows without a customer ID really are. If they're phone or wholesale orders
rather than web guest orders, the checkout change won't close the gap, and the plan for BR-03 changes.
