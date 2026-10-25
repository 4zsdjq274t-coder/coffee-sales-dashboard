# Coffee Sales Dashboard — team15

**Deployed** on Streamlit Community Cloud.

**Live app:** https://<your-app-id>.streamlit.app/

**Team:** Chen, Junxian; Yu, Boyan; Bai, Yuning; Qian, Hongyi.

Every member publishes their own repository, README, and app. This README is my own write-up of
the design decisions behind the app; the dashboard itself is the one our team built together.

---

## 1. The data and the person it is for

The data is `index_1.csv` from [Coffee Sales by ihelon on Kaggle](https://www.kaggle.com/datasets/ihelon/coffee-sales),
a transaction log from a real coffee vending machine. **One row is one recorded sale.**

I work with `index_1.csv` alone. It carries a full year of transactions, which is enough to see
how demand moves and how the drink mix shifts, and keeping to one file keeps every number on the
page traceable to a single source. `index_2.csv` from the same dataset is not used and enters no
calculation.

| Property | Value |
|---|---|
| Period covered | 1 March 2024 – 23 March 2025 |
| Size | 3,636 rows, 6 columns, 279,369 bytes (~0.28 MB) |
| Fields | `date`, `datetime`, `cash_type`, `card`, `money`, `coffee_name` |
| Currency | `money` is in Ukrainian hryvnia (UAH) |
| `card` | anonymous card identifier |
| Preparation | used as published; no sampling, filtering, or aggregation |
| License | CC0 Public Domain on Kaggle. The MIT license on my code does not override this |

The dashboard is built for **one person: the operations manager responsible for this vending
machine**. The scenario below is the use case our team chose for the machine's operator. It is a
proposed reading of the data, not something the dataset's author told us.

## 2. Why this deserves a dashboard

**Who looks at it, and how often.** The manager opens it each morning for a quick read on the
previous day, and sits down with it once a week before deciding what to send out for the next
replenishment cycle.

**The decision it supports.** *If the operations manager sees that a drink's share of
transactions has risen and kept rising over several weeks, they will revise that drink's
ingredient allocation for the next replenishment cycle — subject to what the recipes and current
stock actually allow.* And: *if they see total transactions drop sharply against the previous
week, they will contact the site to find out why.*

Both halves matter. If I could not finish the sentence with a concrete action, this would not be
a dashboard yet.

**What happens today without it.** In the scenario we imagined, the manager exports sales
periodically and rebuilds a summary by hand. That costs preparation time every week, invites
inconsistent date ranges between one summary and the next, and — most importantly — means a
change in demand is spotted when someone has time to look, not when it happens. I am not
claiming a measured saving in hours or money; we did not interview the operator and the data
carries no record of how they work now.

**Why a dashboard rather than something simpler.** These are recurring questions asked by the
same person, and the answer changes every week — which rules out a one-off report. A scheduled
weekly email would fix the date range and the comparison in advance, so the manager could not
drill into an unusual week or shift the window when a public holiday distorts it. An alert would
say "something dropped" without showing which drinks moved, so it would trigger an investigation
without arming the person for it. Filtering dates and comparing drinks side by side is exactly
what an interactive page adds.

## 3. What is on the page, and what I left off

The exploratory work is in [`coffee-sales-eda.ipynb`](coffee-sales-eda.ipynb) (Pandas and
Matplotlib): shape and types, missing values, duplicates, date coverage, the distribution of
amounts, demand by drink, and how demand moves over time.

**Four findings drove the design:**

- Nothing is missing from `date`, `money`, or `coffee_name`, and no row is a full duplicate. Only
  `card` has gaps — 89 of them, every one on a cash payment. Those sales stay in the totals: an
  absent card number does not make the sale any less real.
- There are eight drinks, and **Americano with Milk and Latte together make up 44.2% of
  transactions**. Half of all demand sits in two recipes, so counting transactions by drink and
  showing each drink's share is directly useful to a replenishment decision.
- **Seven dates have no rows at all**, and the file stops on 23 March 2025, so its last month is
  partial. Any period-over-period comparison needs the boundaries stated on the page.
- Amounts run from **18.12 to 40.00 UAH** and vary *within* a drink type, so revenue moves with
  price and mix as well as with volume. That is why transaction count leads and revenue follows.

### The three headline numbers

| Metric | How it is calculated | Why the manager cares |
|---|---|---|
| **Transactions** | count of rows in the selected period | the cleanest read on how much people are buying; not distorted by price |
| Revenue (UAH) | sum of `money` | the financial size of that activity |
| Avg. transaction (UAH) | revenue ÷ transactions | separates "fewer sales" from "smaller sales" |

Transactions come first. Revenue is the number a finance report would lead with, but it mixes
volume with price and drink mix, so it cannot answer "are people buying less?" on its own.

### The order of the page

1. **Top — context.** Team title, who the page is for and what decision it serves, the snapshot
   period, and the intended refresh. The sidebar holds one date-range filter, preset to the full
   snapshot. There is no store selector, because there is one machine.
2. **Next — the three headline numbers**, side by side in `st.columns` with `st.metric`,
   transactions first. Comparison only makes sense between periods with comparable coverage, so
   the page says so.
3. **Middle — two charts.** A daily transaction trend answers "when did demand change?"; a
   horizontal bar chart of transactions by drink, labelled with each drink's share, answers
   "which drinks are driving it?" Together they explain the headline numbers rather than
   restating them.
4. **Bottom — the limits**, stated in a caption: what the data cannot tell you. There is no raw
   transaction table, because the decisions above run on aggregate demand and no one has asked
   to read individual rows.

Reading top to bottom, the page goes from "is anything wrong?" to "why?" to "what should I not
conclude?" — and the manager gets the answer before they have to scroll. Our team sketched this
order on paper before writing any code, as the exercise asks.

**Two things I deliberately cut.** Payment-method breakdowns: how a customer paid does not change
what goes into the machine, however interesting the cash/card split looks in the EDA. And
anything at customer level: `card` is anonymised, it is absent for every cash sale, so it cannot
yield a customer count — and even if it could, "who bought" does not change a replenishment
order.

**What could mislead a reader, and how the page handles it.**

- *Missing dates are not zero-sales days.* A gap means no record, which could be a closed
  machine, a failed export, or genuinely no custom. The trend chart leaves gaps as gaps instead
  of filling them with zero, and the caption counts how many dates in the selected range have no
  records.
- *The data has no business fields.* No quantity, no inventory, no recipe, no cost. So the page
  says *transactions*, never *cups*; it never shows profit, never declares a stockout, and never
  prescribes an order quantity. A fall in sales prompts a phone call to the site — it does not
  prove the machine is broken.
- *It is a snapshot, not a feed.* The actual period is printed on the page next to the words
  **Kaggle snapshot**. A live-looking dashboard built on a year-old CSV is the main way this
  page could mislead someone, so the boundary is stated rather than implied.

## 4. How fresh the numbers need to be

**Refresh nightly; the manager reviews the next morning; replenishment is adjusted weekly.**

Nightly is the right cadence because the decision it feeds is made weekly, and the underlying
data changes daily. Refreshing more often would add integration and monitoring cost for no
change in any decision — no one reorders ingredients at 3pm because of a 2pm sale. True
real-time concerns, like the machine going offline, belong in a separate device alert, not on
this page.

The one metric I would track is **weekly transaction count**. As a starting rule: *a fall of more
than 20% against the previous complete Monday–Sunday week triggers a call to the site.* Before
acting, check that reporting is complete and look for holidays or a changed opening schedule; if
the drop survives that, inspect machine availability and physical stock. I want to be clear that
20% is a proposed threshold, not a validated one — calibrating it properly needs operating
history we do not have, and the right number may turn out to be 10% or 30%.

**What stale data costs.** A day late, and an investigation starts a day later — usually
harmless. A week late is a different problem: replenishment gets planned on demand that has
already moved, which shows up as shortages on drinks that are suddenly popular and unnecessary
stock on drinks that have gone quiet. Since ingredients have a shelf life, that is money
written off, not just an inconvenient week.

The app prints the real data period, the word **Kaggle snapshot**, and
**Intended production refresh: nightly**. This project reads a static CSV; the refresh line
describes the process I would put around it in production, not something the deployed app does.

## 5. Files and deployment

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard entrypoint |
| `index_1.csv` | the Kaggle data, sitting beside the app |
| `requirements.txt` | Streamlit, Pandas, Matplotlib |
| `coffee-sales-eda.ipynb` | exploratory analysis and the evidence behind the design |
| `README.md` | this write-up |

**To deploy your own copy:** fork or copy these files into the root of a public repository under
your own GitHub account. In Streamlit Community Cloud, choose that repository, branch `main`,
entrypoint `app.py`, and set **Python 3.14** under **Advanced settings** — the exercise requires
it. Then deploy.

Once it is live, paste the app URL at the top of this file and open it in a private window to
confirm someone else can reach it. Submit the live app URL and your own repository URL on Canvas.
