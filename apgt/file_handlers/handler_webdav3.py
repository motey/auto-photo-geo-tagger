from typing import Dict, List
from pathlib import PurePath
from apgt.file_handlers._handler_interface import FileHandlerInterface


class WebDav3Handler(FileHandlerInterface):
    def __init__(self, params: Dict):
        raise NotImplementedError

    def list_dirs(self, directory: PurePath) -> List[PurePath]:
        raise NotImplementedError

    def list_files(self, directory: PurePath) -> List[PurePath]:
        raise NotImplementedError

    def read_file(self, path: PurePath) -> bytes:
        raise NotImplementedError

    def write_file(self, path: PurePath, content: bytes):
        raise NotImplementedError
