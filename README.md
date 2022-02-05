# Pynsights

Understand Python code by visualizing how modules interact

# Installation using Pip

Run the following:

```
pip install git+https://github.com/laffra/pynsights
```

# Make a Recording

To make a recording, run:

```
python -m pynsights record [-o <tracefilename>] <modulename>
```

# View the Recording

To view the recording, run:

```
python -m pynsights render [-w] <tracefilename>
```

This CLI command converts the recording into a standalone HTML format. When
you pass `-w`, the HTML will also be launched in a browser. The resulting HTML file
can be hosted and run at any time by loading it into a browser. 

# Pynsights Example Recording

![Pynsights timeline](images/timeline.gif)

Pynsights shows the modules in your program and how they interact.

The timeline shows a subset of the modules active in the graph over time. The white labels
under the timeline are created using `pynsights.annotate(message)`, see below.
The labels and timeline show the different phases in the program execution.

Here is [the interactive HTML version](https://chrislaffra.com/pynsights_timeline.html). 
You can interact with it in the browser to stop/start the animation, for instance. Use the left mouse button to rotate the graph, right mouse button to pan, and scroll wheel to zoom.

# Hiding Details

When you click on "Toplevel", all sub-modules are collapsed into their
parent module. This reduces the complexity of the graph quite a bit.

![Tracing toplevel modules using Pynsights](images/ikke-toplevel.gif)

# Bloom

Enable or disable `Bloom` to change the graph rendering.

# Counts and Dots

With `Counts` and `Dots` the links in the graph can be annotated with 
number of calls made between the two modules it links and when messages
are sent between the modules.

# Make a Recording by Changing your Code

Above we showed how to use the CLI.
To enable Pynsights from within your module source itself, import `pynsights` and start the recorder:

```
import pynsights

if __name__ == "__main__":
    with pynsights.Recorder():
        App().run()
```

Tracing is active for the duration of the context manager. 

You can manually toggle the tracer using `Pynsights.start_tracing()` and `Pynsights.stop_tracing()`.

# Change the Recording Location

If your main script is named `main`, the recording is save in `~/pynsight_trace_main.txt`.
By passing a different file path to the recorder, you can change where the recording is saved:

```
if __name__ == "__main__":
    with pynsights.Recorder("~/main.txt"):
        App().run()
```
