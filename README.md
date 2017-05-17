T800.winthread
====

Extension of threading.Thread adding terminate method using Win32 API on Python

## How to use added terminate method

Just replace your use of `threading.Thread` with `T800.winthread.TerminatableThread`.

```
from T800.winthread import TerminatableThread as Thread

t = Thread(target=run_forever)  # e.g. sys.stdin.read
t.start()

...

t.terminate()
# You can even exit here though t.setDaemon(True) was not called.
```

## How to suppress annoying warning messages

```
import warnings
from T800.winthread import ThreadTerminationWarning

warnings.simplefilter("ignore", category=ThreadTerminationWarning)
```

## What's T800?

Just Google it. :)
