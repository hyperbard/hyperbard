import os

import pytest

from hyperbard.statics import DATA_PATH, GRAPHICS_PATH, META_PATH, RAWDATA_PATH


@pytest.mark.skipif(
    "config.getoption('--remote')",
    reason="Only run locally",
)
def test_paths():
    assert os.path.exists(DATA_PATH)
    assert os.path.exists(GRAPHICS_PATH)
    assert os.path.exists(META_PATH)
    assert os.path.exists(RAWDATA_PATH)
