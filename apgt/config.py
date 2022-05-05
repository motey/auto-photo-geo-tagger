from typing import List, Dict, Union
from Configs import ConfigBase


class DEFAULT(ConfigBase):

    # FILES_REMOTE_ACCESS; If you use any remote locations for you files you can define the access parameters here
    # At the moment supported "type"s are :
    # * "webdav3" based on https://pypi.org/project/webdavclient3/
    # examples:
    # {"nextcloud01": {"type":"webdav3", params: {"webdav_hostname": "https://mynexctloud.org","webdav_login": "my-username", "webdav_password":"s3cret"}}
    FILES_REMOTE_ACCESS: Dict[str, Dict[str, str]] = {}

    # FILES_GPX_TRACK_LOCATIONS; The locations where apgt can find your GPX Track for geotagging your photos
    # If you want to specify any remote locations you need to provide the "type" parameter with a defintion from the FILES_REMOTE_ACCESS parameter
    # examples:
    # {"my-local-gpx01":{"pathes":["/data/gpx"]}, "my-remote-gpx02":{"pathes":["Documents/gpx","Archive/gpx"],"type":"nextcloud01"}}
    FILES_GPX_TRACK_LOCATIONS: Dict[str, Dict[str, str]] = {}

    # FILES_PHOTO_EXTENSIONS; Only tag images with following extenions. Hints: include dot: e.g. ".jpeg" | case insensitive: .jpeg=.JPEG
    FILES_PHOTO_EXTENSIONS: List[str] = [".jpeg", ".jpg", ".tiff", ".tif"]

    # FILES_GPX_EXTENSIONS; Only parse track file with following extenions. Hints: include dot: e.g. ".jpeg" | case insensitive: .jpeg=.JPEG
    FILES_GPX_EXTENSIONS: List[str] = [".gpx"]

    # FILES_PHOTOS_LOCATIONS; The locations where apgt can find your Photos
    # If you want to specify any remote locations you need to provide the "type" parameter with a defintion from the FILES_REMOTE_ACCESS parameter
    # Examples:
    # {"my-local-pics01":{"pathes":["/data/pics"]}, "my-remote-pics02":{"pathes":["Documents/Pictures","Archive/Pictures"],"type":"nextcloud01"}}
    FILES_PHOTOS_LOCATIONS: Dict = {}

    # TAGGING_TIME_TOLERANCE; Which difference in seconds of GPX Track point time and photo taken time do we tolerate to assume, that a photo was shot at this track point
    # 0 to disable and always just take the nearest point. No mater how far away its from the photo shot time
    # defaults to 300
    TAGGING_TIME_TOLERANCE_SECS: int = 300

    # TAGGING_ACCURACY_TOLERANCE_METER; if a gpx trackpoint does have a `extension/accuracy` data, we can define a max value of accuracy we tolerate to use the value for tagging
    # 0 for disable
    # defaults to 0
    TAGGING_ACCURACY_TOLERANCE_METER: int = 0

    # TAGGING_CRON_INTERVAL; How often should apgt rerun and check for new files to geotag? provide a cron string. https://crontab.guru/
    # Set to None/"null" to run only once an exit
    # defaults to
    # examples:
    # "0 0 * * SAT" -> once a week every saturday at 0:00
    # "0 * * * *" -> at every full hour
    # "0 */6 * * *" -> every six hours
    # "0 23 * * *" -> every night at 23:00
    TAGGING_CRON_INTERVAL: str = "0 23 * * *"

    # TAGGING_CRON_INTERVAL; Run once immediately when started, irrespective of TAGGING_CRON_INTERVAL
    TAGGING_CRON_RUN_AT_START: bool = True
