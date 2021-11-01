# Pynsights

Understand Python code by visualizing how modules interact

# Installation

Clone the repo and setup the environment:

```
python3 -m pip install virtualenv\npython3 -m venv env_pynsights
source env_pynsights/bin/activate
python3 setup.py install
```

Publication to pypy will come soon.

# Example

For an example how Pynsights works, run the following:

```
python3 example.py 
```

# Usage

To enable Pynsights, add the following to the very top of your main module:

```
import pynsights
```

Pynsights will open a new browser window and render a graph.

<img src="https://github.com/laffra/pynsights/blob/main/images/Ikke.gif">

# Zooming out

When you click on "Toplevel", all sub-modules are collapsed into their
parent module. This reduces the complexity of the graph quite a bit.

![Tracing toplevel modules using Pynsights](images/ikke-toplevel.gif)

# Trace Calls

Click on a graph node to print calls made to that module. 
Click in the background to disabling tracing again. 
Click in the background again to clear the current log.
