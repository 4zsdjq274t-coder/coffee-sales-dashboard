from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Coffee Sales — team15", page_icon="☕", layout="wide")
st.title("Coffee Sales Dashboard — team15")
st.caption(
    "For the coffee vending-machine operations manager: review ingredient mix "
    "for replenishment and investigate sales anomalies."
)

# Keep the CSV beside this script, both locally and in the GitHub repository.
try:
    df = pd.read_csv(Path(__file__).with_name("index_1.csv"))
except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError):
    st.error("Cannot read index_1.csv. Place the original CSV beside app.py.")
    st.stop()

required = {"date", "money", "coffee_name"}
if not required.issubset(df.columns):
    missing = ", ".join(sorted(required - set(df.columns)))
    st.error(f"The CSV is missing required columns: {missing}.")
    st.stop()
if df.empty:
    st.error("The CSV contains no transaction records.")
    st.stop()

df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
df["money"] = pd.to_numeric(df["money"], errors="coerce")
df["coffee_name"] = df["coffee_name"].astype("string").str.strip()
invalid = (
    df["date"].isna()
    | df["money"].isna()
    | df["money"].isin([float("inf"), float("-inf")])
    | (df["money"] <= 0)
    | df["coffee_name"].isna()
    | df["coffee_name"].eq("")
)
if invalid.any():
    st.error(
        f"Found {int(invalid.sum())} rows with invalid dates, amounts, or drink names. "
        "Check the CSV before using these totals; no rows have been discarded."
    )
    st.stop()

first_date = df["date"].min().date()
last_date = df["date"].max().date()
st.caption(
    f"Data: {first_date:%d %b %Y} – {last_date:%d %b %Y} · Kaggle historical snapshot · "
    "Intended production refresh: nightly. Review the next morning; adjust replenishment weekly."
)

with st.sidebar:
    st.header("Date range")
    selected_dates = st.date_input(
        "Recorded transaction dates",
        value=(first_date, last_date),
        min_value=first_date,
        max_value=last_date,
        format="YYYY-MM-DD",
        key="date_range",
    )
    st.caption("The same date range applies to all three metrics and both charts.")

if len(selected_dates) != 2:
    st.info("Select both a start date and an end date to view the dashboard.")
    st.stop()

start_date, end_date = selected_dates
if start_date > end_date:
    st.info("Choose an end date on or after the start date.")
    st.stop()

selected = df.loc[
    df["date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
].copy()
st.caption(f"Selected period: {start_date:%d %b %Y} – {end_date:%d %b %Y}")

metric_columns = st.columns(3)
has_records = not selected.empty
metric_columns[0].metric("Transactions", f"{len(selected):,}" if has_records else "—")
metric_columns[1].metric(
    "Revenue (UAH)", f"{selected['money'].sum():,.2f}" if has_records else "—"
)
metric_columns[2].metric(
    "Avg. transaction (UAH)", f"{selected['money'].mean():,.2f}" if has_records else "—"
)

if not has_records:
    st.info("No recorded transactions in this date range. This does not confirm zero sales.")
else:
    calendar = pd.date_range(start_date, end_date, freq="D")
    daily = selected.groupby("date").size().reindex(calendar)
    drinks = selected.groupby("coffee_name").size().sort_values()
    chart_columns = st.columns(2)

    with chart_columns[0]:
        st.subheader("When did demand change?")
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.plot(daily.index, daily.values, color="#8B5E3C", marker=".", markersize=4)
        ax.set(xlabel="Date", ylabel="Recorded transactions", ylim=(0, None))
        ax.grid(axis="y", alpha=0.2)
        fig.autofmt_xdate()
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        missing_days = int(daily.isna().sum())
        st.caption(
            f"Daily transactions · {missing_days} dates without records in this range. "
            "Missing dates stay as gaps; they are not filled with zero."
        )

    with chart_columns[1]:
        st.subheader("Which drinks drive demand?")
        fig, ax = plt.subplots(figsize=(7, 4.5))
        bars = ax.barh(drinks.index, drinks.values, color="#8B5E3C")
        labels = [f"{count:,} ({count / len(selected):.1%})" for count in drinks]
        ax.bar_label(bars, labels=labels, padding=4)
        ax.set(xlabel="Recorded transactions", xlim=(0, drinks.max() * 1.45))
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption("Transaction counts and shares inform ingredient mix; check recipes and stock before ordering.")

st.caption(
    "Limits: rows are transactions, not verified cups or unique customers. "
    "No inventory, quantity, recipe, or cost data are available; profit and stockouts cannot be determined. "
    "Compare periods with similar reporting coverage; the snapshot ends on "
    f"{last_date:%d %b %Y}, so its final month may be incomplete."
)
with st.expander("Proposed action rule and data notes"):
    st.write(
        "Production proposal: investigate a fall of more than 20% in transactions between "
        "two consecutive complete Monday–Sunday weeks. First check feed completeness, "
        "holidays, and operating schedules; if unexplained, contact the site to inspect "
        "machine availability and stock. The threshold is provisional and needs validation. "
        "This historical dashboard does not run live alerts."
    )
    st.markdown("Source: [Kaggle Coffee Sales — ihelon](https://www.kaggle.com/datasets/ihelon/coffee-sales), index_1.csv (CC0).")
