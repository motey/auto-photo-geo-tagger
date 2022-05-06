from typing import Dict, List
from pathlib import PurePath
import datetime


class RemoteFile:
    def __init__(
        self,
        remote_path: PurePath,
        file_handler: "FileHandlerInterface",
        content: bytes = None,
    ):
        self.remote_path = remote_path
        self.file_handler = file_handler
        self._content = content

    def push(self):
        self.file_handler.write_file(path=self.remote_path, content=self.content)

    @property
    def content(self):
        if self._content is None:
            self._content = self.file_handler.read_file(self.remote_path)
        return self._content

    @content.setter
    def content(self, value: bytes):
        self._content = value


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

    def get_alternative_file_creation_date_utc(
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
