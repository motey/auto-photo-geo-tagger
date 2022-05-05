from typing import List, Dict, Iterator, Type
from pathlib import PurePath
from exif import Image
import gpxpy
from gpxpy.geo import Location
from apgt.file_handlers import FileHandlerInterface, LocalFileHandler, WebDav3Handler
from apgt.file_source import FileSource
import datetime

file_handler_name_matching: Dict = {
    "local": LocalFileHandler,
    "WebDav3": WebDav3Handler,
}


class APGT:
    points: List[Location] = None

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
                gpx = gpxpy.parse(gpx_file)
                for track in gpx.tracks:
                    for segment in track.segments:
                        self.points.extend(segment.points)

    def _match_images_to_gpx_track_points(self):
        pass

    def _get_nearest_point_in_time(self, target_time: datetime.datetime) -> Location:
        # https://stackoverflow.com/questions/32237862/find-the-closest-date-to-a-given-date
        pass
