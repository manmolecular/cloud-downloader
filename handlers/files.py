#!/usr/bin/env python3

from pathlib import Path


class FilesHandler:
    def __init__(self):
        pass

    def get_files_by_uuid(self, uuid: str, data_path: str or Path = "data"):
        try:
            return [str(path.name) for path in Path(f"{data_path}/{uuid}").glob("*.*")]
        except:
            pass
