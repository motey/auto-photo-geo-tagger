from typing import List, Dict, Iterator, Type
import datetime
from exif import Image
import gpxpy
from gpxpy.gpx import GPXTrackPoint
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
    convert_datetime_to_site_specific_time,
    photo_has_exif_gps_data,
    probe_timezones_in_track_section,
    get_photo_date,
)


file_handler_name_matching: Dict = {
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

    def __init__(self):
        self.gpx_file_sources: List[FileSource] = []
        self.photo_file_sources: List[FileSource] = []
        self.points: List[GPXTrackPointComparable] = []

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
                file_handler_class=file_handler_name_matching[file_source_type],
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
                file_handler_class=file_handler_name_matching[file_source_type],
                file_handler_params=file_source_params,
                allowed_extensions=allowed_extensions,
            )
        )

    def run(self):
        self._load_gpx_track_points()
        self._match_images_to_gpx_track_points()

    def _load_gpx_track_points(self):
        """Load all GPX tracks from all provided GPX files and aggreate them to one long track"""
        for gpx_file_source in self.gpx_file_sources:
            for gpx_file in gpx_file_source.iter_files():
                gpx = gpxpy.parse(gpx_file.content)
                for track in gpx.tracks:
                    for segment in track.segments:
                        self.points.extend(
                            [
                                GPXTrackPointComparable.from_GPXTrackPoint(p)
                                for p in segment.points
                            ]
                        )
        # Make trackpoints unique and sort by time
        self.points = sorted(set(self.points), key=lambda x: x.time, reverse=True)
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
                photo_date = get_photo_date(file)
                if photo_date:
                    point: GPXTrackPointComparable = (
                        self._get_nearest_track_point_in_time(photo_date)
                    )
                    # if we found a trackpoint with a timestamp that closely matches the timestamp of the photo and we did not cross any timezones during the day the photo was taken, we can assert the photo was shoot at `point`
                    if point and len(
                        probe_timezones_in_track_section(
                            initial_track_point=point,
                            track_points=self.points,
                            range_to_probe_in_hours=12,
                            probe_accuracy=0.1,
                        )
                        == 1
                    ):
                        self._write_gpxpoint_to_exif_gps_data(point, file)

    def _write_gpxpoint_to_exif_gps_data(
        self, point: GPXTrackPointComparable, file: RemoteFile
    ):
        file.exif_image.gps_latitude = point.latitude
        file.exif_image.gps_longitude = point.longitude
        for tag, val in self.ADDITIONAL_EXIF_TAGS_IF_MODIFIED:
            setattr(file.exif_image, tag, val)
        file.push()

    def _get_nearest_track_point_in_time(
        self, target_time: datetime.datetime
    ) -> GPXTrackPointComparable:
        # https://stackoverflow.com/questions/32237862/find-the-closest-date-to-a-given-date
        nearest_point: GPXTrackPointComparable = min(
            self.points,
            key=lambda x: abs(
                convert_datetime_to_site_specific_time(x.time, x.latitude, x.longitude)
                - target_time
            ),
        )

        # we do not want return the nearest point if it is too far away in time (defined by self.NEAREST_TIME_TOLERANCE_SECS).
        # ..but some tracker do not create trackpoints when there is no movement.
        # therefore we need to test if there was no movement. then we can ignore self.NEAREST_TIME_TOLERANCE_SECS
        if (
            abs((nearest_point.time - target_time).total_seconds())
            >= self.NEAREST_TIME_TOLERANCE_SECS
        ):
            nearest_point_time_localized = convert_datetime_to_site_specific_time(
                nearest_point.time, nearest_point.latitude, nearest_point.longitude
            )
            index_of_nearest_point = self.points.index(nearest_point)
            index_next_point = None
            # get next trackpoint that, together with nearest_point, encloses `target_time`
            if (
                nearest_point_time_localized > target_time
                and index_of_nearest_point < len(self.points) - 1
            ):
                index_next_point = index_of_nearest_point + 1
            elif (
                nearest_point_time_localized < target_time
                and index_of_nearest_point > 0
            ):
                index_next_point = index_of_nearest_point + 1
            if not index_next_point:
                # if we were at the end or start of our track, we cant not determine any distance.
                return None
            next_point = self.points[index_next_point]

            distance_between_points: int = int(
                distance.Distance(
                    (nearest_point.latitude, nearest_point.longitude),
                    (next_point.latitude, next_point.longitude),
                ).meters
            )

            if (
                distance_between_points
                < self.IGNORE_NEAREST_TIME_TOLERANCE_SECS_IF_DISTANCE_SMALLER_THEN_N_METERS
            ):
                # we had no movement therefore the `nearest_point`, although far away in time, is valid
                return nearest_point
            else:
                return None
