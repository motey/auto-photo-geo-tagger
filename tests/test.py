from asyncio import subprocess
import os
import sys
from multiprocessing import Process
import subprocess
from pathlib import PurePath, Path
from distutils.dir_util import copy_tree
from shutil import rmtree

SCRIPT_DIR = None
if __name__ == "__main__":
    # some boilerplate code to load this local module instead of installed one for developement
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    SCRIPT_DIR = os.path.join(SCRIPT_DIR, "..")
    print(os.path.normpath(SCRIPT_DIR))
    sys.path.insert(0, os.path.normpath(SCRIPT_DIR))

# reset image dir
test_tmp_path = PurePath(SCRIPT_DIR, "tests/test_data/images_to_gps_tag")
if Path(test_tmp_path).is_dir():
    rmtree(PurePath(SCRIPT_DIR, "tests/test_data/images_to_gps_tag"))
copy_tree(
    src=str(PurePath(SCRIPT_DIR, "tests/test_data/images_no_gps")),
    dst=str(PurePath(SCRIPT_DIR, "tests/test_data/images_to_gps_tag")),
)
my_env = os.environ.copy()
my_env["ENV"] = "TEST"

working_dir = PurePath(SCRIPT_DIR, "apgt")
main = PurePath(SCRIPT_DIR, "apgt", "main.py")
subprocess.run(main, env=my_env, cwd=working_dir)
