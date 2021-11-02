# Pynsights

Understand Python code by visualizing how modules interact

# Installation using Pip

Run the following:

```
pip install git+https://github.com/laffra/pynsights
```

# Manual Installation Into Local Repo

Clone the repo first:

```
git clone https://github.com/laffra/pynsights
```

Optionally, use a virtual environment:

```
python3 -m pip install virtualenv\npython3 -m venv env_pynsights
source env_pynsights/bin/activate
```

Finally, finish setup and resolve dependencies:

```
python3 setup.py install
```

# Installation from Pypi

Publication to pypi will come soon.

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

# Usage from a different repository

If you used the manual install and cloned the pynsights repo to your local device and want to invoke
it from another repository, you can tell Python where to find it:

```
import sys
sys.path.append('/path/to/pynsights')
import pynsights
```

# Enabling and Disabling Pynsights

To (temporarily) suspend pynsights, for instance to improve startup, run:

```
pynsights.stop_tracing()
```

To enable pynsights after disabling it, run:

```
pynsights.start_tracing()
```

# Zooming out

When you click on "Toplevel", all sub-modules are collapsed into their
parent module. This reduces the complexity of the graph quite a bit.

![Tracing toplevel modules using Pynsights](images/ikke-toplevel.gif)

# Trace Calls

Click on a graph node to print calls made to that module. 
Click in the background to disabling tracing again. 
Click in the background again to clear the current log.

# Animation

You can enable "counts" and "dots" to reduce the amount of information shown in the graph.

# Filter Modules

In the top-right of the Pynsights UI, you can enter a regex to filter the modules being shown. An example would be:

```
storage|elastic|importer-*|yourmodulenames
```