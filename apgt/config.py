from typing import List, Dict, Union
from Configs import ConfigBase

# Default Environment
class DEFAULT(ConfigBase):
    LOG_LEVEL = "INFO"
    # FILES_REMOTE_ACCESS; If you use any remote locations for your files you can define the access parameters here
    # At the moment supported "type"s are :
    # * "webdav3" based on https://pypi.org/project/webdavclient3/
    # examples:
    # {"nextcloud01": {"type":"webdav3", params: {"webdav_hostname": "https://mynexctloud.org","webdav_login": "my-username", "webdav_password":"s3cret"}}
    FILES_REMOTE_ACCESS: Dict[str, Dict[str, str]] = {}

    # FILES_GPX_TRACK_LOCATIONS; The locations where apgt can find your GPX Track for geotagging your photos
    # If you want to specify any remote locations you need to provide the "remote_access_config_name" parameter with a defintion from the FILES_REMOTE_ACCESS parameter
    # examples:
    # {"my-local-gpx01":{"pathes":["/data/gpx"]}, "my-remote-gpx02":{"pathes":["Documents/gpx","Archive/gpx"],"remote_access_config_name":"nextcloud01"}}
    FILES_GPX_TRACK_LOCATIONS: Dict[str, Dict[str, str]] = {}

    # FILES_PHOTOS_LOCATIONS; The locations where apgt can find your Photos
    # If you want to specify any remote locations you need to provide the "type" parameter with a defintion from the FILES_REMOTE_ACCESS parameter
    # Examples:
    # {"my-local-pics01":{"pathes":["/data/pics"]}, "my-remote-pics02":{"pathes":["Documents/Pictures","Archive/Pictures"],"type":"nextcloud01"}}
    FILES_PHOTOS_LOCATIONS: Dict = {}

    # FILES_PHOTO_EXTENSIONS; Only tag images with following extenions. Hints: include dot: e.g. ".jpeg" | case insensitive: .jpeg=.JPEG
    FILES_PHOTO_EXTENSIONS: List[str] = [".jpeg", ".jpg", ".tiff", ".tif"]

    # FILES_GPX_EXTENSIONS; Only parse track file with following extenions. Hints: include dot: e.g. ".jpeg" | case insensitive: .jpeg=.JPEG
    FILES_GPX_EXTENSIONS: List[str] = [".gpx"]

    # FILES_SURVIVE_NO_GPX_TRACKS_FOUND; When there are no gpx tracks found in any source pathes, apgt will raise an exception and exit.
    # Set FILES_SURVIVE_NO_GPX_TRACKS_FOUND to True if you start apgt before you add any GPX tracks to your file system and want to supress this specific exception
    FILES_SURVIVE_NO_GPX_TRACKS_FOUND: bool = False

    # FILES_EXIF_OPTIMISTIC_DATE_PARSER; if you have photos with non default exif date format (YYYY:HH:MM hh:mm:ss) that will fail you can enable FILES_EXIF_OPTIMISTIC_DATE_PARSER.
    # If set to true we will use  https://dateparser.readthedocs.io/en/latest/ to parse dates
    # This should work with any format, that is not too crazy, but creates a slight risk of wrong date parsing and costs more compared to just read the default format
    FILES_EXIF_OPTIMISTIC_DATE_PARSER: bool = False

    # TAGGING_TIME_TOLERANCE_SECS; Which difference in seconds of GPX Track point time and photo taken time do we tolerate to assume, that a photo was shot at this track point
    # 0 to disable and always just take the nearest point. No mater how far away its from the photo shot time
    # defaults to 300
    TAGGING_TIME_TOLERANCE_SECS: int = 300

    # TAGGING_IGNORE_TIME_TOLERANCE_IF_DISTANCE_SMALLER_THEN_N_METERS; Some Tracker will not produce new tracking points if there was no movement. This would collide with the TAGGING_TIME_TOLERANCE_SECS parameter.
    # With this setting we can force to use tracking points further away in time as TAGGING_TIME_TOLERANCE_SECS to to geotag photos. even if the photos were taken hours after the tracking point event.
    TAGGING_IGNORE_TIME_TOLERANCE_IF_DISTANCE_SMALLER_THEN_N_METERS: int = 60

    #! Not implemented yet, no effect
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
    TAGGING_CRON_INTERVAL: str = None

    # TAGGING_CRON_INTERVAL; Run once immediately when started, irrespective of TAGGING_CRON_INTERVAL
    TAGGING_CRON_RUN_AT_START: bool = True

    TAGGING_ADDITIONAL_EXIF_TAGS_IF_MODIFIED: Dict = {
        "UserComment": "GPS location added with auto-photo-geo-tagger"
    }


# Overwrite default environment for testing
class TEST(DEFAULT):
    LOG_LEVEL = "DEBUG"
    FILES_GPX_TRACK_LOCATIONS = {
        "my-local-gpx01": {"pathes": ["../tests/test_data/tracks"]}
    }
    FILES_PHOTOS_LOCATIONS = {
        "my-local-gpx01": {"pathes": ["../tests/test_data/images_to_gps_tag"]}
    }
    TAGGING_TIME_TOLERANCE_SECS: int = 500
