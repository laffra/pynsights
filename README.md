# Pynsights

Understand Python code by visualizing how modules interact

# Installation using Pip

Run the following:

```
pip install git+https://github.com/laffra/pynsights
```

# Make a Recording

To enable Pynsights, import the module and start the recorder:

```
import pynsights

if __name__ == "__main__":
    with pynsights.Recorder():
        App().run()
```

Tracing is active for the duration of the context manager. 
You can manually toggle the tracer using
`Pynsights.start_tracing()` and `Pynsights.stop_tracing()`.

# Change the Recording Location

If your main script is named `main`, the recording is save in `~/pynsight_trace_main.txt`.
By passing a different file path to the recorder, you can change where the recording is saved:

```
if __name__ == "__main__":
    with pynsights.Recorder("~/main.txt"):
        App().run()
```

# Viewing the Recording

To view the recording, run the following:

```
python pynsights/view.py ~/pynsights_trace_main.txt
```

This does two things: 1. convert the recording into HTML format and 2. open it.
The resulting output can be found in `~/pynsights_trace_main.html`, or
whatever location where you chose to save the recording. This HTML file
is fully standalone and can be hosted. 

Here is [an example recording](https://chrislaffra.com/pynsights_trace_main.html).

# Zooming out

When you click on "Toplevel", all sub-modules are collapsed into their
parent module. This reduces the complexity of the graph quite a bit.

![Tracing toplevel modules using Pynsights](images/ikke-toplevel.gif)

# Bloom

Enable or disable `Bloom` to change the graph rendering.

# Counts and Dots

With `Counts` and `Dots` the links in the graph can be annotated with 
number of calls made between the two modules it links and when messages
are sent between the modules.
