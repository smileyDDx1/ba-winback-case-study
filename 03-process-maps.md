# 3. Process maps

The as-is flow is partly assumed (marked below) and would be confirmed with the CRM manager and the web team.
The diagrams are Mermaid and render on GitHub.

## 3.1 As-is: order capture and marketing

```mermaid
flowchart TD
    A(["Customer checks out"]) --> B{"Signed in?"}
    B -- Yes --> C["Order saved with customer ID"]
    B -- No --> D["Guest checkout: order saved<br/>with no customer ID"]
    C --> E["Monthly newsletter,<br/>same email for every subscriber"]
    D --> F["Order invisible to segments,<br/>retention and campaigns"]
    E --> G["Nobody checks who has<br/>stopped buying"]
```

**Pain points**

| # | Pain point | Evidence | Fixed by |
|---|---|---|---|
| 1 | Orders without a customer ID can't be analysed or targeted | 235,151 rows, £2.94M (~14% of sales) | FR-10 to FR-12 |
| 2 | Lapsing customers are not noticed | 888 At-Risk customers, £2.19M, ~275 days since last order | FR-01, FR-04 |
| 3 | Marketing results can't be proven | No control group today *(assumed)* | FR-05, KPI-2, KPI-3 |
| 4 | Segments can change between two runs on the same data | Per-customer export: 895 At-Risk; summary: 888 | FR-02 |

## 3.2 To-be: weekly win-back

```mermaid
flowchart TD
    subgraph BI["Data / BI team - every Monday 06:00"]
        S1["Refresh RFM scores,<br/>ties broken by customer ID"] --> S2["At-Risk list:<br/>R score 1-2, F score 3-4"]
    end
    subgraph CRM["CRM manager and email platform"]
        C1{"Consent or soft opt-in,<br/>not unsubscribed or bounced?"}
        C1 -- No --> X1["Exclude and log the reason"]
        C1 -- Yes --> C2{"In a win-back in<br/>the last 90 days?"}
        C2 -- Yes --> X2["Skip this week"]
        C2 -- No --> C3["Random split:<br/>90% treatment, 10% control"]
        C3 -- Control --> K1["No emails, orders still tracked"]
        C3 -- Treatment --> E1["Day 0: we miss you"]
        E1 --> E2["Day 7: single-use 10% code"]
        E2 --> E3["Day 14: last reminder"]
    end
    subgraph CUST["Customer"]
        O1(["Places an order"])
    end
    S2 --> C1
    E1 -. order .-> O1
    E2 -. order .-> O1
    E3 -. order .-> O1
    O1 --> STP["Remaining emails stop"]
    E3 --> M["Day 90: compare reactivation,<br/>treatment vs control"]
    K1 --> M
```

## 3.3 To-be: guest checkout links the order to a customer

```mermaid
flowchart TD
    A(["Customer checks out"]) --> B{"Signed in?"}
    B -- Yes --> C["Order saved with customer ID"]
    B -- No --> D["Guest checkout asks for email<br/>(required, format checked)"]
    D --> E{"Email matches a customer?<br/>(trimmed, case-insensitive)"}
    E -- Yes --> F["Order linked to that customer ID"]
    E -- No --> G["New customer record,<br/>flagged as guest"]
    G --> H["Order linked to the new ID"]
    C --> I["Order counts in segments,<br/>retention and campaigns"]
    F --> I
    H --> I
```

## 3.4 What changes

| Step | As-is | To-be | Requirements |
|---|---|---|---|
| Spot lapsing customers | Not done | Weekly RFM refresh and At-Risk list | FR-01 to FR-03 |
| Choose who to email | Every subscriber gets the newsletter | At-Risk only, after consent and suppression checks | FR-04 |
| Measure the effect | Not possible | 10% random control group | FR-05, KPI-2, KPI-3 |
| Win-back contact | None | 3 emails over 14 days, stop on order | FR-06 to FR-09 |
| Guest checkout | Order saved with no customer | Email required and matched to a customer | FR-10 to FR-12 |
| Reporting | Monthly revenue only *(assumed)* | Weekly campaign dashboard, monthly data-capture trend | FR-13, FR-14 |
