from typing import List, Set
import datetime
import random
import pytz
from timezonefinder import TimezoneFinder
from exif import Image
from apgt.file_source import RemoteFile


def convert_datetime_to_site_specific_time(
    source_datetime: datetime.datetime,
    latitude: float,
    longitude: float,
    source_timezone: datetime.tzinfo = None,
):

    if source_datetime.tzinfo is None:
        if source_timezone is None:
            source_timezone = pytz.timezone("UTC")
        source_datetime = source_timezone.localize(source_datetime)
    # find the timezone of the coordinates
    tf = TimezoneFinder()
    target_tz_name = tf.timezone_at(lng=longitude, lat=latitude)
    target_tz = pytz.timezone(target_tz_name)
    # localize the utc time to the specific local time and return
    return source_datetime.astimezone(target_tz)


from gpxpy.gpx import GPXTrackPoint


def probe_timezones_in_track_section(
    initial_track_point: GPXTrackPoint,
    track_points: List[GPXTrackPoint],
    range_to_probe_in_hours: int = 12,
    probe_accuracy: int = 0.1,
) -> Set[datetime.tzinfo]:
    """Function to check if a track crossed timezones at a certain section.
    Define a specific track point and probe the neigbeir points left and right according to range_to_probe_in_hourse

    !Todo: This whole func needs a refactor. very ugly :)

    Args:
        initial_track_point (GPXTrackPoint): _description_
        track_points (List[GPXTrackPoint]): _description_
        range_to_probe_in_hours (int, optional): _description_. Defaults to 12.
        probe_accuracy (int, optional): 0-1
    """
    timezones: List[datetime.tzinfo] = []
    index_of_init_point = track_points.index(initial_track_point)
    tf = TimezoneFinder()

    for track_point_index in range(index_of_init_point, len(track_points) - 1):
        # oldschool looping without list slicing because we potentialy handle very large lists here
        # slicing will do create a new list and therefore is inneffiecient compared to oldschool looping
        # please correct me if i am wrong :)
        current_trackpoint = track_points[track_point_index]
        if current_trackpoint.time - initial_track_point.time > datetime.timedelta(
            hours=range_to_probe_in_hours
        ):
            # we are done probing because we reached the defined range limit `range_to_probe_in_hours`
            # but lets take the last timezone point into account
            last_trackpoint = track_points[track_point_index - 1]
            timezones.append(
                tf.timezone_at(
                    lng=last_trackpoint.longitude, lat=last_trackpoint.latitude
                )
            )
            break
        if random.random() < probe_accuracy:
            timezones.append(
                tf.timezone_at(
                    lng=current_trackpoint.longitude, lat=current_trackpoint.latitude
                )
            )
    for track_point_index in range(len(track_points) - 1, index_of_init_point, -1):
        current_trackpoint = track_points[track_point_index]
        if current_trackpoint.time - initial_track_point.time > datetime.timedelta(
            hours=range_to_probe_in_hours
        ):
            # we are done probing because we reached the defined range limit `range_to_probe_in_hours`
            # but lets take the last timezone point into account
            print(
                current_trackpoint.time,
                initial_track_point.time,
                current_trackpoint.time - initial_track_point.time,
            )
            last_trackpoint = track_points[track_point_index + 1]
            timezones.append(
                target_tz_name=tf.timezone_at(
                    lng=last_trackpoint.longitude, lat=last_trackpoint.latitude
                )
            )
            break
        if random.random() < probe_accuracy:
            timezones.append(
                tf.timezone_at(
                    lng=current_trackpoint.longitude, lat=current_trackpoint.latitude
                )
            )
        return set(timezones)


def photo_has_exif_gps_data(photo: Image) -> bool:
    if (
        photo.has_exif
        and hasattr(photo, "gps_longitude")
        and photo.gps_longitude
        and hasattr(photo, "gps_latitude")
        and photo.gps_latitude
    ):
        return True
    return False


def get_photo_date(photo_file: RemoteFile) -> datetime.datetime:
    if photo_file.exif_image.has_exif and (
        (
            hasattr(photo_file.exif_image, "datetime_original")
            and photo_file.exif_image.datetime_original
        )
        or (
            hasattr(photo_file.exif_image, "datetime")
            and photo_file.exif_image.datetime
        )
    ):
        return (
            photo_file.exif_image.datetime
            if photo_file.exif_image.datetime
            else photo_file.exif_image.datetime_original
        )
    else:
        return photo_file.file_handler.get_alternative_file_creation_date_utc(
            photo_file.remote_path
        )
