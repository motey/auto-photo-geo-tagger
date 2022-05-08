from typing import List, Dict, Iterator, Type
from apgt.file_handlers import FileHandlerInterface, RemoteFile
from pathlib import PurePath


class FileSource:
    def __init__(
        self,
        name: str,
        base_pathes: List[PurePath],
        file_handler_class: Type[FileHandlerInterface],
        file_handler_params: Dict = None,
        allowed_extensions: List[str] = [],
    ):
        self.name = name
        self.base_pathes = base_pathes
        self.file_handler_class: Type[FileHandlerInterface] = file_handler_class
        self.file_handler_params: Dict = file_handler_params
        self.current_file: RemoteFile = None
        self.allowed_extensions: List[str] = [ext.lower() for ext in allowed_extensions]

        self._current_file_handler: FileHandlerInterface = None

    def iter_files(self) -> Iterator[RemoteFile]:
        self._initate_file_handler()
        for base_path in self.base_pathes:
            for dir_path in self._walk_dirs(
                file_handler=self._current_file_handler, base_path=base_path
            ):
                for remote_file in self._current_file_handler.list_files(dir_path):
                    if (
                        remote_file.remote_path.suffix.lower()
                        in self.allowed_extensions
                    ):
                        self.current_file = remote_file
                        yield remote_file

    def update_current_file(self, content: bytes):
        if self.current_file is None:
            raise IndexError(
                f"Photo iteration for handler '{self.file_handler_class.__name__}' not yet started. Use {self.iter_files} first."
            )
        self._current_file_handler.write_file(
            path=self.current_file.remote_path, content=content
        )

    def _initate_file_handler(self):
        self._current_file_handler: FileHandlerInterface = self.file_handler_class(
            params=self.file_handler_params
        )

    def _walk_dirs(
        self, file_handler: FileHandlerInterface, base_path: PurePath
    ) -> Iterator[PurePath]:
        yield base_path
        for dir_path in file_handler.list_dirs(base_path):
            yield dir_path
            self._walk_dirs(file_handler, dir_path)
