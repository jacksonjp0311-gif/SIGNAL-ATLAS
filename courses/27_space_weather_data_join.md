# Lesson 27: Make a useful dataset from two public feeds

## Goal

Trace a pair of NOAA observations from their original files to a date-matched table, chart, and reusable research packet.

## Start here

1. Open the [Data Explorer](../site/datasets.html).
2. Read the original F10.7 JSON and geomagnetic text files linked below the chart.
3. Compare a few rows in the joined CSV with the normalized geomagnetic JSON.
4. Open the [AI packet](../data/packets/examples/space-weather-noaa-2026-11-03.v0.7.packet.json) and identify its dataset IDs, source IDs, date window, and limitations.

## Work the data

The Atlas joins by the supplied date labels. It keeps eight estimated planetary Kp values per complete day, then computes a daily maximum and arithmetic mean. It excludes a day if the source has missing Kp intervals or if the matching F10.7 value is unavailable.

The 2026-11-03 geomagnetic row is incomplete. Find it in the normalized JSON, note the null values, and verify that it is absent from the complete comparison table. The missing values are not zeros.

## Questions

- How do the two panels differ in units and meaning?
- Which dates have a daily estimated Kp maximum of at least 5?
- What information is lost when eight three-hour values are summarized as one maximum?
- Why is matching the date label not the same as matching simultaneous measurements?
- What additional data would be needed before studying a longer-term relationship?

## Reproduce

Run the offline builder from the repository root:

    python tools/build_space_weather_v07.py

Then run the focused tests:

    python -m unittest discover -s tests -p "test_v07_space_weather.py"

This exercise demonstrates reproducible data handling, not a validated forecast or causal model.
