import os
import sys
from typing import List
import gpxpy
from gpxpy.gpx import GPXTrackPoint
import datetime

if __name__ == "__main__":
    # some boilerplate code to load this local module instead of installed one for developement
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    SCRIPT_DIR = os.path.join(SCRIPT_DIR, "..")
    print(os.path.normpath(SCRIPT_DIR))
    sys.path.insert(0, os.path.normpath(SCRIPT_DIR))
from apgt.tools import (
    convert_datetime_to_site_specific_time,
    probe_timezones_in_track_section,
)

track_file_with_two_tz = open("tests/test_data/track_with_two_tz.gpx", "r")
track_with_two_tz = gpxpy.parse(track_file_with_two_tz)
points: List[GPXTrackPoint] = []
for track in track_with_two_tz.tracks:
    for segment in track.segments:
        for point in segment.points:
            points.append(point)

assert (
    len(
        probe_timezones_in_track_section(
            initial_track_point=points[5], track_points=points, probe_accuracy=1
        )
    )
    == 2
)

# test utc to local time conversion
assert "2022-05-06 14:00:00+02:00" == str(
    convert_datetime_to_site_specific_time(
        source_datetime=datetime.datetime(
            2022, 5, 6, 12, 00, tzinfo=datetime.timezone.utc
        ),
        latitude=47.88,
        longitude=12.8,
    )
)

# test unaware datetime (assume utc) to local time conversion
assert "2022-05-06 14:00:00+02:00" == str(
    convert_datetime_to_site_specific_time(
        source_datetime=datetime.datetime(2022, 5, 6, 12, 00),
        latitude=47.88,
        longitude=12.8,
    )
)
