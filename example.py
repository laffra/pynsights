#
# Pynsights should be the first import in your main module.
#
import pynsights

#
# Pynsights uses sys.settrace, which traces all Python calls.
# Note that builtin functions (implemented in C) are not traced.
# Therefore, the calls to time, os, and sys below are not traced.
# All the calls to the helloworld module are actually traced.
#
# Pynsights ignores calls inside modules. It focuses on calls
# between modules, to emphasize the architectural structure of
# the application being explored.
#
# Pynsights will slow down execution and increase CPU a bit.
# This is to be expected, considering the amount of work it does.
#
# See README.md for more information.
#

from hello.helloworld import helloworld
import time

def run():
    for n in range(1, 101):
        time.sleep(0.01)
        helloworld()  



if __name__ == "__main__":
    run()

