# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib", "pandas", "Pillow"]
# ///

"""Create a month-by-month GIF of NOAA Storm Event locations."""

from pathlib import Path
import json

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import pandas as pd

# ---------------------------------------------------------------------------
# The knobs.
# ---------------------------------------------------------------------------

PAPER = "#faf8f4"
INK = "#1d1d1b"
MAP_EDGE = "#b8b2a7"
MAP_FILL = "#e8e3d8"
MAP_BOUNDS = (-125, -66, 24, 50)  # contiguous United States
HERE = Path(__file__).parent
DATA = HERE / "data"
OUT = HERE / "out"
BOUNDARY_FILE = DATA / "us-states.json"
GIF_TARGET = OUT / "us-extreme-weather-by-month.gif"


def find_boundary_file():
    """Return the state GeoJSON downloaded by fetch.py."""
    if not BOUNDARY_FILE.exists():
        raise SystemExit(
            "data/us-states.json is missing; run fetch.py before plot.py"
        )
    return BOUNDARY_FILE


def load_events(source):
    """Read records with usable beginning coordinates and month values."""
    events = pd.read_csv(source, low_memory=False)
    events["BEGIN_YEARMONTH"] = pd.to_numeric(
        events["BEGIN_YEARMONTH"], errors="coerce"
    )
    events["END_YEARMONTH"] = pd.to_numeric(
        events["END_YEARMONTH"], errors="coerce"
    )
    events["LAT"] = pd.to_numeric(events["BEGIN_LAT"], errors="coerce")
    events["LON"] = pd.to_numeric(events["BEGIN_LON"], errors="coerce")
    events = events.dropna(
        subset=["BEGIN_YEARMONTH", "LAT", "LON", "EVENT_TYPE"]
    ).copy()
    events["END_YEARMONTH"] = events["END_YEARMONTH"].fillna(
        events["BEGIN_YEARMONTH"]
    )
    events["BEGIN_MONTH"] = (
        events["BEGIN_YEARMONTH"] // 100 * 12
        + events["BEGIN_YEARMONTH"] % 100
    )
    events["END_MONTH"] = (
        events["END_YEARMONTH"] // 100 * 12
        + events["END_YEARMONTH"] % 100
    )
    return events


def draw_states(axis, boundary_file):
    """Draw only state polygons that fall inside the contiguous-U.S. view."""
    with boundary_file.open(encoding="utf-8") as handle:
        states = json.load(handle)["features"]
    west, east, south, north = MAP_BOUNDS
    for state in states:
        geometry = state["geometry"]
        polygons = geometry["coordinates"]
        if geometry["type"] == "Polygon":
            polygons = [polygons]
        for polygon in polygons:
            points = polygon[0]
            if not any(west <= lon <= east and south <= lat <= north for lon, lat in points):
                continue
            axis.add_patch(
                Polygon(
                    points, closed=True, facecolor=MAP_FILL,
                    edgecolor=MAP_EDGE, linewidth=0.55, zorder=1,
                )
            )


def main():
    files = sorted(DATA.glob("StormEvents_details*.csv"))
    if not files:
        raise SystemExit("no StormEvents details CSV found in data/")

    source = files[-1]
    events = load_events(source)
    if events.empty:
        raise SystemExit("no records with usable coordinates found")

    shape_file = find_boundary_file()
    months = range(
        int(events["BEGIN_MONTH"].min()), int(events["END_MONTH"].max()) + 1
    )
    event_types = sorted(events["EVENT_TYPE"].unique())
    colours = plt.get_cmap("tab20", len(event_types))
    type_colours = {
        event_type: colours(number) for number, event_type in enumerate(event_types)
    }
    figure, axis = plt.subplots(figsize=(15, 8.5), facecolor=PAPER)
    axis.set_facecolor(PAPER)
    axis.set_xlim(MAP_BOUNDS[0], MAP_BOUNDS[1])
    axis.set_ylim(MAP_BOUNDS[2], MAP_BOUNDS[3])
    axis.set_aspect("equal", adjustable="box")
    axis.set_xlabel("longitude", color=INK)
    axis.set_ylabel("latitude", color=INK)
    axis.tick_params(colors=INK)
    axis.spines[:].set_visible(False)
    draw_states(axis, shape_file)

    legend_handles = [
        Line2D(
            [0], [0], marker="o", linestyle="", markersize=7,
            markerfacecolor=type_colours[event_type], markeredgecolor=PAPER,
            label=event_type,
        )
        for event_type in event_types
    ]
    legend = axis.legend(
        handles=legend_handles,
        title="EVENT_TYPE (monthly records)",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=False,
        fontsize=8.5,
        title_fontsize=9,
    )

    def draw_frame(month):
        points = events[
            (events["BEGIN_MONTH"] <= month) & (events["END_MONTH"] >= month)
        ]
        month_counts = points["EVENT_TYPE"].value_counts()
        for text, event_type in zip(legend.get_texts(), event_types):
            text.set_text(f"{event_type} ({month_counts.get(event_type, 0):,})")
        for collection in list(axis.collections):
            collection.remove()
        for event_type, group in points.groupby("EVENT_TYPE"):
            linger_months = month - group["BEGIN_MONTH"]
            axis.scatter(
                group["LON"], group["LAT"],
                s=14 * (2 ** linger_months), alpha=0.72,
                color=type_colours[event_type],
                edgecolors=PAPER, linewidths=0.25, zorder=3,
            )
        year, month_number = divmod(month, 12)
        axis.set_title(
            f"U.S. extreme weather locations | {year} / {month_number:02d}"
            f" | {len(points):,} mapped records",
            loc="left", color=INK, fontsize=15, pad=12,
        )
        return axis.collections

    animation = FuncAnimation(
        figure, draw_frame, frames=months, interval=1000, blit=False, repeat=True
    )
    OUT.mkdir(exist_ok=True)
    figure.subplots_adjust(left=0.06, right=0.76, top=0.91, bottom=0.09)
    animation.save(GIF_TARGET, writer=PillowWriter(fps=1), dpi=130)
    plt.close(figure)
    print(f"wrote {GIF_TARGET.relative_to(HERE)}")
    print(f"used {len(events):,} mapped records across {len(months)} monthly frames")


if __name__ == "__main__":
    main()