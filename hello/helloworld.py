from .hello import hello
from .world import world

import time

def helloworld():
    time.sleep(0.15)
    return hello() + world()