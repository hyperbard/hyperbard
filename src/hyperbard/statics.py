import os

this_dir = os.path.dirname(__file__)

RAWDATA_PATH = os.path.realpath(os.path.join(this_dir, "..", "..", "rawdata"))
DATA_PATH = os.path.realpath(os.path.join(this_dir, "..", "..", "data"))
META_PATH = os.path.realpath(os.path.join(this_dir, "..", "..", "metadata"))
GRAPHICS_PATH = os.path.realpath(os.path.join(this_dir, "..", "..", "graphics"))
GRAPHDATA_PATH = os.path.realpath(os.path.join(this_dir, "..", "..", "graphdata"))
