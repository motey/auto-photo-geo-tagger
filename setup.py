from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="Auto-photo-geo-tracker",
    description="Automaticly geotag your photos (local or in the cloud) by supplying gpx track file(s)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/motey/auto-photo-geo-tagger",
    author="Motey",
    author_email="motey@gmx.de",
    license="MIT",
    packages=["apgt"],
    install_requires=["DZDConfigs", "exif", "gpxpy"],
    python_requires=">=3.9",
    zip_safe=False,
    include_package_data=True,
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        # "local_scheme": "node-and-timestamp"
        "local_scheme": "no-local-version",
        "write_to": "version.py",
    },
    setup_requires=["setuptools_scm"],
)
