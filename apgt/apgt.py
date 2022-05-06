from typing import List, Dict, Iterator, Type
import datetime
from exif import Image
import gpxpy
from gpxpy.gpx import GPXTrackPoint
from apgt.file_handlers import (
    FileHandlerInterface,
    LocalFileHandler,
    WebDav3Handler,
    RemoteFile,
)
from apgt.file_source import FileSource
from apgt.tools import convert_datetime_to_site_specific_time

file_handler_name_matching: Dict = {
    "local": LocalFileHandler,
    "WebDav3": WebDav3Handler,
}


class APGT:
    points: List[GPXTrackPoint] = None

    def __init__(self):
        self.gpx_file_sources: List[FileSource] = []
        self.photo_file_sources: List[FileSource] = []

    def add_gpx_file_source(
        self,
        name: str,
        pathes: List[str],
        file_source_type: str = "local",
        file_source_params: Dict = None,
        allowed_extensions: List[str] = [".gpx"],
    ):
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
        for gpx_file_source in self.gpx_file_sources:
            for gpx_file in gpx_file_source.iter_files():
                gpx = gpxpy.parse(gpx_file.content)
                for track in gpx.tracks:
                    for segment in track.segments:
                        self.points.extend(segment.points)

    def _match_images_to_gpx_track_points(self):
        for photo_source in self.photo_file_sources:
            for file in photo_source.iter_files():
                photo = Image(file.content)
                photo_date = self.guess_date(file, photo)
                if photo_date:
                    point: GPXTrackPoint = self._get_nearest_point_in_time(photo_date)
                    if point:
                        self._write_gpxpoint_to_exif_gps_data(point, photo)

    def _write_gpxpoint_to_exif_gps_data(self, point: GPXTrackPoint, photo: Image):
        pass

    def _get_nearest_point_in_time(
        self, target_time: datetime.datetime
    ) -> GPXTrackPoint:
        # https://stackoverflow.com/questions/32237862/find-the-closest-date-to-a-given-date
        return min(
            self.points,
            key=lambda x: abs(
                convert_datetime_to_site_specific_time(x.time, x.latitude, x.longitude)
                - target_time
            ),
        )

    def guess_date(
        self, photo_file: RemoteFile, photo_image: Image
    ) -> datetime.datetime:
        if photo_image.has_exif and (
            photo_image.datetime_original or photo_image.datetime
        ):
            return (
                photo_image.datetime
                if photo_image.datetime
                else photo_image.datetime_original
            )
        else:
            return photo_file.file_handler.get_alternative_file_creation_date_utc(
                photo_file.remote_path
            )
