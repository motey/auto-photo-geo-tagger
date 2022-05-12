from typing import List, Dict, Iterator, Type
import logging
import datetime
from exif import Image
import gpxpy
import pytz
from geopy import distance
import itertools
from apgt.track_point_comparable import GPXTrackPointComparable
from apgt.file_handlers import (
    LocalFileHandler,
    WebDav3Handler,
    RemoteFile,
)
from apgt.file_source import FileSource
from apgt.tools import (
    convert_datetime_tz_to_site_specific_tz,
    photo_has_exif_gps_data,
    probe_timezones_in_track_section,
    get_photo_date,
    set_naive_datetime_to_site_specific_tz,
    get_next_item_in_list,
)

log = logging.getLogger(__name__)

file_handler_type_name_matching: Dict = {
    "local": LocalFileHandler,
    "WebDav3": WebDav3Handler,
}


class ErrorNoGPXTracksFound(Exception):
    pass


class APGT:

    # used in_get_nearest_track_point_in_time() if a point is too far away in time we wont consider it as "nearest"
    NEAREST_TIME_TOLERANCE_SECS: int = 300
    # if movement distance to neighbor points is less than this value, we can ignore NEAREST_TIME_TOLERANCE_SECS
    IGNORE_NEAREST_TIME_TOLERANCE_SECS_IF_DISTANCE_SMALLER_THEN_N_METERS: int = 100
    ADDITIONAL_EXIF_TAGS_IF_MODIFIED: Dict = None
    OPTIMISTIC_DATEMATCHING: bool = False

    def __init__(self):
        self.gpx_file_sources: List[FileSource] = []
        self.photo_file_sources: List[FileSource] = []
        # Trackpoints seperated by day
        self.points: Dict[datetime.datetime, List[GPXTrackPointComparable]] = {}

    def add_gpx_file_source(
        self,
        name: str,
        pathes: List[str],
        file_source_type: str = "local",
        file_source_params: Dict = None,
        allowed_extensions: List[str] = [".gpx"],
    ):
        """Add a GPX file source

        Args:
            name (str): Identifier
            pathes (List[str]): _description_
            file_source_type (str, optional): _description_. Defaults to "local".
            file_source_params (Dict, optional): _description_. Defaults to None.
            allowed_extensions (List[str], optional): _description_. Defaults to [".gpx"].
        """
        self.gpx_file_sources.append(
            FileSource(
                name=name,
                base_pathes=pathes,
                file_handler_class=file_handler_type_name_matching[file_source_type],
                file_handler_params=file_source_params,
                allowed_extensions=allowed_extensions,
            )
        )

    def add_photo_file_source(
        self,
        name: str,
        pathes: List[str],
        file_source_type: str = "local",
        file_source_params: Dict = None,
        allowed_extensions: List[str] = [".jpg", ".jpeg", ".tiff", ".tif"],
    ):
        self.photo_file_sources.append(
            FileSource(
                name=name,
                base_pathes=pathes,
                file_handler_class=file_handler_type_name_matching[file_source_type],
                file_handler_params=file_source_params,
                allowed_extensions=allowed_extensions,
            )
        )

    def run(self):
        self._load_gpx_track_points()
        self._match_images_to_gpx_track_points()

    def _load_gpx_track_points(self):
        """Load all GPX tracks from all provided GPX files and aggreate them to tracks seperated by day"""
        for gpx_file_source in self.gpx_file_sources:
            for gpx_file in gpx_file_source.iter_files():
                gpx = gpxpy.parse(gpx_file.content)
                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            day = point.time.date()
                            if not day in self.points:
                                self.points[day] = []
                            self.points[day].append(
                                GPXTrackPointComparable.from_GPXTrackPoint(point)
                            )

        # Make trackpoints unique and sort by time

        self.points = dict(sorted(self.points.items()))
        for day, points in self.points.items():
            self.points[day] = sorted(set(points), key=lambda x: x.time)
        if len(self.points) == 0:
            raise ErrorNoGPXTracksFound(
                f"No tracks with trackpoints found in pathes {list(itertools.chain(*[fs.base_pathes for fs in self.gpx_file_sources]))}"
            )

    def _match_images_to_gpx_track_points(self):
        for photo_source in self.photo_file_sources:
            for file in photo_source.iter_files():
                if photo_has_exif_gps_data(file.exif_image):
                    # image allready has gps data. go to next mage
                    continue
                point = self._find_matching_trackpoint_for_photo(file)
                if point:
                    self._write_gpxpoint_to_exif_gps_data(point, file)

    def _find_matching_trackpoint_for_photo(
        self, file: RemoteFile
    ) -> GPXTrackPointComparable:
        photo_date = get_photo_date(file, self.OPTIMISTIC_DATEMATCHING)
        if photo_date:
            point: GPXTrackPointComparable = self._get_nearest_track_point_in_time(
                photo_date
            )
            # print(file.remote_path, photo_date, point)
            # if we found a trackpoint with a timestamp that closely matches the timestamp of the photo and we did not cross any timezones during the day the photo was taken, we can assert the photo was shoot at `point`
            if point:
                crossed_timezones_during_potential_photo_creation_time = probe_timezones_in_track_section(
                    initial_track_point=point,
                    track_points=self._get_relevant_points_to_find_specific_datetime(
                        photo_date
                    ),
                    range_to_probe_in_hours=12,
                    probe_accuracy=0.1,
                )
                if (
                    photo_date.tzinfo is not None
                    or len(crossed_timezones_during_potential_photo_creation_time) <= 1
                ):
                    return point
                else:
                    log.debug(
                        f"No trackpoint for image '{file.remote_path}' because timezones were crossed in potencial trackpoints. ({crossed_timezones_during_potential_photo_creation_time} ) We can not assure which date is a match. You have to tag this image manually."
                    )
            else:
                log.debug(
                    f"No trackpoint found for image '{file.remote_path}'. Image date: {photo_date}"
                )

    def _write_gpxpoint_to_exif_gps_data(
        self, point: GPXTrackPointComparable, file: RemoteFile
    ):
        log.debug(
            f"Tag photo '{file.remote_path}' created on {get_photo_date(file,self.OPTIMISTIC_DATEMATCHING)} with point {point} ({point.name if hasattr(point,'name') else ''} point local time:{convert_datetime_tz_to_site_specific_tz(point.time,point.latitude,point.longitude)} )"
        )
        file.exif_image.gps_latitude = point.latitude
        file.exif_image.gps_longitude = point.longitude
        log.debug(
            "No exif GPS timestamp written because https://gitlab.com/TNThieding/exif/-/issues/65"
        )
        # file.exif_image.gps_timestamp = point.time.strftime("%H:%M:%S")
        file.exif_image.gps_datestamp = point.time.strftime("%Y:%m:%d")
        for tag, val in self.ADDITIONAL_EXIF_TAGS_IF_MODIFIED.items():
            setattr(file.exif_image, tag, val)
        file.push()

    def _get_relevant_points_to_find_specific_datetime(
        self, target_datetime: datetime.datetime
    ) -> List[GPXTrackPointComparable]:
        if target_datetime.tzinfo:
            # When we have a timezone info we can narrow down the relevant points to a specific day
            day = target_datetime.astimezone(pytz.utc).date()
            if day in self.points:
                return self.points[day]
        # when we dont have a timezone we need to return the points of a day+-1 (3days).
        # That includes all potencial points that could match because of timezone shifting

        day = target_datetime.date()
        relevant_days = []
        # day before
        relevant_days.append(day - datetime.timedelta(days=1))
        relevant_days.append(day)
        # day after
        relevant_days.append(day + datetime.timedelta(days=1))

        points: List[GPXTrackPointComparable] = []
        for d in relevant_days:
            if d in self.points:
                points.extend(self.points[d])
        return points

    def _get_nearest_track_point_in_time(
        self, target_time: datetime.datetime
    ) -> GPXTrackPointComparable:
        # https://stackoverflow.com/questions/32237862/find-the-closest-date-to-a-given-date
        relevant_points = self._get_relevant_points_to_find_specific_datetime(
            target_time
        )
        """
        print(
            "relevant_points",
            "\n".join(
                [
                    f"{p.name}-{convert_datetime_tz_to_site_specific_tz(p.time, p.latitude, p.longitude)}-{p}"
                    for p in relevant_points
                ]
            ),
        )
        """
        if not relevant_points:
            return
        nearest_point: GPXTrackPointComparable = min(
            relevant_points,
            key=lambda x: abs(
                convert_datetime_tz_to_site_specific_tz(x.time, x.latitude, x.longitude)
                - set_naive_datetime_to_site_specific_tz(
                    target_time, x.latitude, x.longitude
                )
            ),
        )

        if not nearest_point:
            # No trackpoints for the day of photo creation
            return None
        # print(
        #    f"NP {nearest_point.name}-{convert_datetime_tz_to_site_specific_tz(nearest_point.time, nearest_point.latitude, nearest_point.longitude)}-{nearest_point}"
        # )
        nearest_point_time_localized = convert_datetime_tz_to_site_specific_tz(
            nearest_point.time, nearest_point.latitude, nearest_point.longitude
        )
        target_time_localized = set_naive_datetime_to_site_specific_tz(
            target_time, nearest_point.latitude, nearest_point.longitude
        )

        # print("nearest_point", nearest_point)
        # print("nearest_point.time", nearest_point.time)
        # print("target_time", target_time)
        # print("target_time_localized", target_time_localized)
        # print(
        #    f"TIMDISTANCE to large {self.NEAREST_TIME_TOLERANCE_SECS}",
        #    abs((nearest_point_time_localized - target_time_localized).total_seconds())
        #    >= self.NEAREST_TIME_TOLERANCE_SECS,
        # )
        # print(
        #    "TIMDISTANCE",
        #    abs((nearest_point_time_localized - target_time_localized).total_seconds()),
        # )

        # we do not want return the nearest point if it is too far away in time (defined by self.NEAREST_TIME_TOLERANCE_SECS).
        # ..but some tracker do not create trackpoints when there is no movement.
        # therefore we need to test if there was no movement. then we can ignore self.NEAREST_TIME_TOLERANCE_SECS
        if (
            abs((nearest_point_time_localized - target_time_localized).total_seconds())
            >= self.NEAREST_TIME_TOLERANCE_SECS
        ):
            neighbor_trackpoint = self._get_neighbor_trackpoint(
                nearest_point, target_time_localized
            )
            if neighbor_trackpoint is None:
                # if we were at the end or start of our track, we cant not determine any distance.
                return None
            distance_to_neighbor_point_meter: int = int(
                distance.distance(
                    (nearest_point.latitude, nearest_point.longitude),
                    (neighbor_trackpoint.latitude, neighbor_trackpoint.longitude),
                ).meters
            )
            if (
                distance_to_neighbor_point_meter
                < self.IGNORE_NEAREST_TIME_TOLERANCE_SECS_IF_DISTANCE_SMALLER_THEN_N_METERS
            ):
                # we had no movement therefore the `nearest_point`, although far away in time, is valid
                return nearest_point
            else:
                return None
        else:
            return nearest_point

    def _get_neighbor_trackpoint(
        self,
        starting_point: GPXTrackPointComparable,
        direction_date_localized: datetime.datetime,
    ):
        starting_day = starting_point.time.date()
        if starting_point.time > direction_date_localized:
            # the neighbor points lies before starting_point

            direction = -1
        else:
            # the neighbor points lies after starting_point
            direction = 1
        index_of_starting_point = self.points[starting_day].index(starting_point)
        if (index_of_starting_point > 0 and direction == -1) or (
            index_of_starting_point < len(self.points[starting_day]) - 1
            and direction == 1
        ):
            # neighbor track point is in the same day. easy case...
            return self.points[starting_day][index_of_starting_point + direction]
        else:
            # neighbor point does exist in one of the neigbor day...
            neighbor_day = get_next_item_in_list(
                list(self.points.keys()),
                starting_day,
                reverse=starting_point.time > direction_date_localized,
            )
            if neighbor_day is None:
                # there is no neighbor day and therefore no neighbor point:(
                return None
            return (
                self.points[starting_day][-1]
                if direction == -1
                else self.points[starting_day][0]
            )
