# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib", "pandas"]
# ///

"""Plot NOAA Storm Events by month, event type, and state."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# ---------------------------------------------------------------------------
# The knobs.
# ---------------------------------------------------------------------------

PAPER = "#faf8f4"
INK = "#1d1d1b"
LINE_FIGSIZE = (16, 8)
RECORD_FIGSIZE = (18, 18)
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

HERE = Path(__file__).parent
DATA = HERE / "data"
OUT = HERE / "out"

# ---------------------------------------------------------------------------
# The drawing.
# ---------------------------------------------------------------------------


def main():
    files = sorted(DATA.glob("StormEvents_details*.csv"))
    if not files:
        raise SystemExit("no StormEvents details CSV found in data/")

    source = files[-1]
    events = pd.read_csv(source, low_memory=False)
    events["MONTH"] = pd.to_numeric(events["BEGIN_YEARMONTH"].astype(str).str[-2:])
    timestamp_format = "%d-%b-%y %H:%M:%S"
    events["BEGIN"] = pd.to_datetime(
        events["BEGIN_DATE_TIME"], format=timestamp_format, errors="coerce"
    )
    events["END"] = pd.to_datetime(
        events["END_DATE_TIME"], format=timestamp_format, errors="coerce"
    )
    events["DURATION_HOURS"] = (events["END"] - events["BEGIN"]).dt.total_seconds() / 3600
    events = events.dropna(subset=["MONTH", "DURATION_HOURS", "EVENT_TYPE", "STATE"])
    first_month = int(events["MONTH"].min())
    last_month = int(events["MONTH"].max())
    active_months = list(range(first_month, last_month + 1))
    active_month_labels = [MONTH_LABELS[month - 1] for month in active_months]

    duration = events.pivot_table(
        index="MONTH", columns="EVENT_TYPE", values="DURATION_HOURS", aggfunc="mean"
    ).reindex(active_months)
    counts = pd.crosstab(events["EVENT_TYPE"], events["STATE"])
    state_month_counts = (
        events.groupby(["MONTH", "STATE"])
        .size()
        .reset_index(name="ENTRIES")
    )
    states = sorted(state_month_counts["STATE"].unique())
    colour_map = plt.get_cmap("turbo", len(states))
    state_colours = {state: colour_map(number) for number, state in enumerate(states)}

    line_figure, line_axis = plt.subplots(figsize=LINE_FIGSIZE, facecolor=PAPER)
    for axis in (line_axis,):
        axis.set_facecolor(PAPER)
        axis.tick_params(colors=INK)
        axis.grid(color=INK, alpha=0.1)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    duration.plot(ax=line_axis, marker="o", linewidth=1.5, colormap="tab20")
    line_axis.set_title("Average event duration by month and event type", color=INK)
    line_axis.set_xlabel("month", color=INK)
    line_axis.set_ylabel("average duration (hours)", color=INK)
    line_axis.set_xlim(first_month - 0.25, last_month + 0.25)
    line_axis.set_xticks(active_months)
    line_axis.set_xticklabels(active_month_labels)
    line_axis.legend(title="EVENT_TYPE", bbox_to_anchor=(1.01, 1), loc="upper left",
                     frameon=False, ncol=2, fontsize=8)

    record_figure, (bar_axis, scatter_axis) = plt.subplots(
        2, 1, figsize=RECORD_FIGSIZE, facecolor=PAPER,
        gridspec_kw={"height_ratios": [1.15, 1.6]},
    )
    for axis in (bar_axis, scatter_axis):
        axis.set_facecolor(PAPER)
        axis.tick_params(colors=INK)
        axis.grid(color=INK, alpha=0.1)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    counts.plot(
        kind="barh", stacked=True, ax=bar_axis,
        color=[state_colours[state] for state in counts.columns],
        legend=False,
    )
    bar_axis.set_title("Storm Event records by event type and state", color=INK)
    bar_axis.set_xlabel("record entries", color=INK)
    bar_axis.set_ylabel("event type", color=INK)
    bar_axis.tick_params(axis="y", labelsize=9)

    for state_number, state in enumerate(states):
        state_rows = state_month_counts[state_month_counts["STATE"] == state]
        scatter_axis.scatter(
            state_rows["ENTRIES"], state_rows["MONTH"],
            s=48, color=state_colours[state], alpha=0.78,
            edgecolors=PAPER, linewidths=0.5, label=state,
        )
    scatter_axis.set_title("Monthly record entries by state", color=INK)
    scatter_axis.set_xlabel("record entries in that state and month", color=INK)
    scatter_axis.set_ylabel("month from BEGIN_YEARMONTH", color=INK)
    scatter_axis.set_yticks(active_months)
    scatter_axis.set_yticklabels(active_month_labels)
    scatter_axis.set_ylim(last_month + 0.5, first_month - 0.5)
    scatter_axis.legend(
        title="STATE", bbox_to_anchor=(1.01, 1), loc="upper left",
        frameon=False, ncol=2, fontsize=8,
    )

    OUT.mkdir(exist_ok=True)
    line_target = OUT / "storm-event-duration-by-month.png"
    record_target = OUT / "storm-event-records-by-state.png"
    line_figure.subplots_adjust(left=0.08, right=0.73, top=0.93, bottom=0.12)
    record_figure.subplots_adjust(left=0.18, right=0.75, top=0.95, bottom=0.07, hspace=0.42)
    line_figure.savefig(line_target, dpi=150, facecolor=PAPER)
    record_figure.savefig(record_target, dpi=150, facecolor=PAPER)
    print(f"wrote {line_target.relative_to(HERE)}")
    print(f"wrote {record_target.relative_to(HERE)} from {source.name} — {len(events)} records")


if __name__ == "__main__":
    main()
