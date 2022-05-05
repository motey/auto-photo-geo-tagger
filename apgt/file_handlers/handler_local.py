from importlib.resources import path
from typing import Dict, List
from pathlib import PurePath, Path
from apgt.file_handlers._handler_interface import FileHandlerInterface


class LocalFileHandler(FileHandlerInterface):
    def __init__(self, params: Dict = None):
        pass

    def list_dirs(self, directory: PurePath) -> List[PurePath]:
        p = Path(directory)
        pathes = []
        for obj in p.iterdir():
            if obj.is_dir():
                pathes.append(obj)
        return pathes

    def list_files(self, directory: PurePath) -> List[PurePath]:
        p = Path(directory)
        pathes = []
        for obj in p.iterdir():
            if obj.is_file():
                pathes.append(obj)
        return pathes

    def read_file(self, path: PurePath) -> bytes:
        return open(path, "rb")

    def write_file(self, path: PurePath, content: bytes):
        with open("path", "wb") as new_image_file:
            new_image_file.write(content)
