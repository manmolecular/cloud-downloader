#!/usr/bin/env python3

from publisher.publisher import Publisher


if __name__ == "__main__":
    url_list = [
        "http://www.tsu.ru/upload/medialibrary/22d/pobeda75.jpg",
        "http://www.tsu.ru/upload/resize_cache/iblock/4e7/320_213_2/0m8a8521_drugtsu_cam520.jpg",
    ]
    publisher = Publisher()
    for _ in range(10):
        print(publisher.publish_task(url_list))
