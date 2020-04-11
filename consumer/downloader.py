#!/usr/bin/env python3

from multiprocessing import Pool
from os import path
from pathlib import Path
from urllib.parse import urlparse

from requests import get


class Downloader:
    def __init__(self, base_path: str or Path):
        self.base_path = base_path

    @staticmethod
    def _extract_filename(url: str) -> str:
        """
        Extract filename from URL
        :param url:
        :return:
        """
        parse_url = urlparse(url)
        return path.basename(parse_url.path)

    def url_response(self, task: dict) -> str:
        """
        Save file by URL chunk by chunk
        :param task: uuid + url
        :return: status string
        """
        uuid = task.get("uuid")
        url = task.get("url")
        full_path = Path(f"{self.base_path}/{uuid}/{self._extract_filename(url)}")
        full_path.parent.mkdir(parents=True, exist_ok=True)
        response = get(url, stream=True)
        with open(file=full_path, mode="wb") as file_to_write:
            for chunk in response:
                file_to_write.write(chunk)
        return f"Save {full_path}"

    def start_download(self, url_list: list, uuid: str, processes: int = 10) -> None:
        """
        Start downloading files provided in list
        :param url_list: list of URLs to download
        :param uuid: UUID
        :param processes: quantity of processes
        :return: None
        """
        task = [{"url": url, "uuid": uuid} for url in url_list]
        with Pool(processes=processes) as pool:
            for status in pool.imap_unordered(self.url_response, task):
                print(status)
