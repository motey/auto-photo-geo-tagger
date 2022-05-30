from exif import Image
from libxmp.utils import file_to_dict
from libxmp import consts


def get_all_metadata():
    file = "tests/test_data/images_no_gps/02_tz_aware/8_2020.01.01_00.00_tz2_tp01.jpg"
    file = "older_phone_2011.12.24_18:10.JPG"
    file = "tests/test_data/modern_phone_tz_aware_2020.08.14_14.33.jpg"
    file = "tests/test_data/older_phone_2011.01.06_12.32.jpg"
    print("##EXIF")
    i = Image(file)
    for exif_attr in i.list_all():
        try:
            print(exif_attr, getattr(i, exif_attr))
        except:
            print(exif_attr, "ERROR")
    print("##XMP")
    xmp = file_to_dict(file)
    for scheme, vals in xmp.items():
        print("##SCHEME", scheme)
        for val in vals:
            print(val)


# get_all_metadata()


def test_gps_timestammpd():
    from exif import Image
    import datetime
    from pathlib import Path

    f = Path(
        "tests/test_data/images_to_gps_tag/01_tz_unaware/1_2020.01.01_02.02_tp01.jpg"
    )
    with open(
        f,
        "rb+",
    ) as image_file:
        my_image = Image(image_file)
        my_image.has_exif  # is true
        my_image.gps_timestamp = (11, 11, 11)


test_gps_timestammpd()
