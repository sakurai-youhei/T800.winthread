T800.winthread
====

Extension of threading.Thread adding terminate method using Win32 API on Python

[![Build status](https://img.shields.io/appveyor/ci/sakurai_youhei/t800-winthread/master.svg?label=Python%202.7%2C%203.3%20to%203.6%20%2F%20win32%20%26%20win_amd64)](https://ci.appveyor.com/project/sakurai_youhei/t800-winthread/branch/master)

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
