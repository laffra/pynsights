# Pynsights
Understand Python code by visualizing how modules interact

# Installation
Clone the repo. Publication to pypy will come soon.

# Usage
Simply at this to the very top of your main module:

```
import pynsights
```

Pynsights will open a new browser window and render a graph:

![Tracing modules using Pynsight](images/ikke.gif)

# Zooming out

When you click on "Toplevel", all sub-modules are collapsed into their
parent module. This reduces the complexity of the graph quite a bit.

![Tracing toplevel modules using Pynsight](images/ikke-toplevel.gif)

# Trace Calls

Click on a graph node to print calls made to this module. 
Click in the background to disabling tracing. 
Click in the background again to clear the current log.
