from typing import Dict, List
from pathlib import PurePath
import datetime
from exif import Image
from gpxpy.gpx import GPXXMLSyntaxException


class RemoteFile:
    def __init__(
        self,
        remote_path: PurePath,
        file_handler: "FileHandlerInterface",
        content: bytes = None,
    ):
        self.remote_path = remote_path
        self.file_handler = file_handler
        self._content: bytes = content
        self._exif_image: Image = None

    def push(self):
        """Write local state of file back via file_handler backend"""
        # if _exif_image was called, we assume that we want to write back self._exif_image data. else we just write back byte content in self._content
        self.file_handler.write_file(
            path=self.remote_path,
            content=self._exif_image.get_file() if self._exif_image else self.content,
        )

    @property
    def content(self) -> bytes:
        if self._content is None:
            self._content = self.file_handler.read_file(self.remote_path)
        return self._content

    @content.setter
    def content(self, value: bytes):
        self._content = value

    @property
    def exif_image(self) -> Image:
        if self._exif_image is None:
            try:
                self._exif_image = Image(self.content)
            except GPXXMLSyntaxException:
                raise ValueError(
                    f"Not a valid image file format or invalid exif data for file ' {self.remote_path}'"
                )
        return self._exif_image


class FileHandlerInterface:
    def __init__(self, params: Dict = None):
        raise NotImplementedError

    def list_dirs(self, directory: PurePath) -> List[PurePath]:
        raise NotImplementedError

    def list_files(self, directory: PurePath) -> List[RemoteFile]:
        raise NotImplementedError

    def read_file(self, path: PurePath) -> bytes:
        raise NotImplementedError

    def write_file(self, path: PurePath, content: bytes):
        raise NotImplementedError

    def get_alternative_photo_creation_date_utc(
        self, path: PurePath
    ) -> datetime.datetime:
        """Optional fallback method to get a photos creation date. Will be used if there is no datetime in the exif data
            If your file handler backend wont provide any informations just always return None
        Args:
            path (PurePath): Path to the photo we want to the creation date of

        Returns:
            datetime.datetime: Return a datetime.datetime date. !UTC timezone only!
        """
        return None
