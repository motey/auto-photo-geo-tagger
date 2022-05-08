import os
import sys
import logging
from Configs import getConfig
from croniter import croniter
import datetime
import time
from multiprocessing import Process
from typing import Callable, List, Dict
from subprocess import SubprocessError

if __name__ == "__main__":
    # some boilerplate code to load this local module instead of installed one for developement
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    SCRIPT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(SCRIPT_DIR))
from apgt import APGT
from apgt.apgt import ErrorNoGPXTracksFound
from apgt.config import DEFAULT

config: DEFAULT = getConfig()

logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)-15s %(processName)-8s %(module)-8s %(levelname)-8s:  %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger(__name__)


def run_in_subprocess(func: Callable):
    proc = Process(target=func)
    proc.start()
    proc.join()
    if proc.exitcode != 0:
        raise SubprocessError()


def run_apgt():
    auto_tagger = APGT()
    auto_tagger.ADDITIONAL_EXIF_TAGS_IF_MODIFIED = (
        config.TAGGING_ADDITIONAL_EXIF_TAGS_IF_MODIFIED
    )
    auto_tagger.NEAREST_TIME_TOLERANCE_SECS = config.TAGGING_TIME_TOLERANCE_SECS
    auto_tagger.IGNORE_NEAREST_TIME_TOLERANCE_SECS_IF_DISTANCE_SMALLER_THEN_N_METERS = (
        config.TAGGING_IGNORE_TIME_TOLERANCE_IF_DISTANCE_SMALLER_THEN_N_METERS
    )
    for file_source_name, file_source_def in config.FILES_GPX_TRACK_LOCATIONS.items():
        pathes: List[str] = file_source_def["pathes"]
        access_config = None
        if "remote_access_config_name" in file_source_def:
            access_config: Dict[str, str] = config.FILES_REMOTE_ACCESS[
                file_source_def["remote_access_config_name"]
            ]
        auto_tagger.add_gpx_file_source(
            name=file_source_name,
            pathes=pathes,
            file_source_type=access_config["type"] if access_config else "local",
            file_source_params=access_config["params"] if access_config else None,
            allowed_extensions=config.FILES_GPX_EXTENSIONS,
        )
    for file_source_name, file_source_def in config.FILES_PHOTOS_LOCATIONS.items():
        pathes: List[str] = file_source_def["pathes"]
        access_config = None
        if "remote_access_config_name" in file_source_def:
            access_config: Dict[str, str] = config.FILES_REMOTE_ACCESS[
                file_source_def["remote_access_config_name"]
            ]
        auto_tagger.add_photo_file_source(
            name=file_source_name,
            pathes=pathes,
            file_source_type=access_config["type"] if access_config else "local",
            file_source_params=access_config["params"] if access_config else None,
            allowed_extensions=config.FILES_GPX_EXTENSIONS,
        )
    try:
        auto_tagger.run()
    except ErrorNoGPXTracksFound:
        if not config.FILES_SURVIVE_NO_GPX_TRACKS_FOUND:
            raise


def main():
    # Load the library local for development and not the system installed one

    log.info(
        f"Current timezone: {(datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo)}"
    )

    def wait_until(end_datetime: datetime.datetime):
        while True:
            diff = (end_datetime - datetime.datetime.now()).total_seconds()
            if diff < 0:
                return  # In case end_datetime was in past to begin with
            time.sleep(diff / 2)
            if diff <= 0.1:
                return

    if config.TAGGING_CRON_INTERVAL:
        if config.TAGGING_CRON_RUN_AT_START:
            log.info(
                f"Run once at start now! Then go over to service mode with intervalled runs..."
            )
            run_in_subprocess(run_apgt)

        base_time = datetime.datetime.now()
        cron_job = croniter(config.SERVICE_CRON_INTERVAL, base_time)
        log.info(f"Begin service mode...")
        while True:
            next_time = cron_job.get_next(datetime.datetime)
            log.info(f"Wait until {next_time} for next import")
            wait_until(next_time)
            # run in a seperated process to prevent any possible memory leackage over time
            run_in_subprocess(run_apgt)
            log.info(f"------")
    else:
        log.info(f"Run once! (Not in service mode)")
        run_apgt()


if __name__ == "__main__":
    main()
