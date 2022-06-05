import os

from hyperbard.statics import DATA_PATH, GRAPHICS_PATH, META_PATH, RAWDATA_PATH


def test_paths():
    assert os.path.exists(DATA_PATH)
    assert os.path.exists(GRAPHICS_PATH)
    assert os.path.exists(META_PATH)
    assert os.path.exists(RAWDATA_PATH)
