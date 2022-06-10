import os
import time

from hyperbard.statics import RESOURCE_USAGE_PATH


def timeit(method):
    def timed(*args, **kw):
        start = time.time()
        result = method(*args, **kw)
        finish = time.time()
        timefile = f"{RESOURCE_USAGE_PATH}/{method.__name__}.txt"
        with open(timefile, "w") as f:
            f.write(f"{os.path.basename(__file__)}, {finish - start}")
        return result

    return timed
