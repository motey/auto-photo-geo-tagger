from typing import Dict, List
from pathlib import PurePath


class FileHandlerInterface:
    def __init__(self, params: Dict = None):
        raise NotImplementedError

    def list_dirs(self, directory: PurePath) -> List[PurePath]:
        raise NotImplementedError

    def list_files(self, directory: PurePath) -> List[PurePath]:
        raise NotImplementedError

    def read_file(self, path: PurePath) -> bytes:
        raise NotImplementedError

    def write_file(self, path: PurePath, content: bytes):
        raise NotImplementedError
