#
# Pynsights should be the first import in your main module.
#
import pynsights

#
# Pynsights uses sys.setprofile, which traces all Python calls.
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

import pynsights
from hello.helloworld import helloworld
import gc
import time

COUNT = 10
ENABLE_REMOTE_CONTROL = False


@pynsights.trace
def say_hello(n):
    pynsights.annotate("helloworld - %d" % n)
    helloworld()  
    print(f"\rExample: Run Hello World - {10 - n}", end="")


def run():
    print("-" * 50)
    print("Example: Run Hello World", COUNT, "times.")
    for n in range(1, COUNT + 1):
        say_hello(n)
        time.sleep(0.1)
        gc.collect()
    print("\nExample: Done.")
    print("-" * 50)
    run_forever()


def run_forever():
    if ENABLE_REMOTE_CONTROL:
        print("\nNow running forever until remote stops us.")
        while True:
            time.sleep(10)


def setup_remote_control():
    if ENABLE_REMOTE_CONTROL:
        pynsights.listen(6673)
        import webbrowser
        webbrowser.open("http://localhost:6673/trace")


if __name__ == "__main__":
    setup_remote_control()
    run()
