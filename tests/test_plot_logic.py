import pandas as pd

from plot import build_type_colours, cumulative_event_totals


def test_build_type_colours_stable_and_sorted():
    colours = build_type_colours(["Tornado", "Flood", "Hail"])
    assert list(colours) == ["Tornado", "Flood", "Hail"]
    assert colours["Flood"] == build_type_colours(["Tornado", "Flood", "Hail"])["Flood"]


def test_cumulative_event_totals_accumulates_by_month():
    events = pd.DataFrame(
        {
            "BEGIN_MONTH_INDEX": [1, 1, 2, 2],
            "END_MONTH_INDEX": [1, 2, 2, 3],
            "EVENT_TYPE": ["Tornado", "Flood", "Tornado", "Flood"],
        }
    )

    totals = cumulative_event_totals(events, [1, 2, 3])

    assert totals[1]["Tornado"] == 1
    assert totals[1]["Flood"] == 1
    assert totals[2]["Tornado"] == 2
    assert totals[2]["Flood"] == 2
    assert totals[3]["Tornado"] == 2
    assert totals[3]["Flood"] == 2
