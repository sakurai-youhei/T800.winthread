'''
Created on 2017/05/11
Licensed under MIT

@author: sakurai
'''

from contextlib import contextmanager
from ctypes import c_int
from ctypes import POINTER
from ctypes import windll
from ctypes import WinError
from ctypes import wintypes
from threading import _active
from threading import _active_limbo_lock
from threading import Lock
from threading import Thread
import warnings


__all__ = ["ThreadTerminationWarning", "TerminatableThread"]


def assertNotNULL(result, func, args):
    if result == POINTER(c_int)():
        raise WinError()
    return args


def assertTrue(result, func, args):
    if not result:
        raise WinError()
    return args


# https://msdn.microsoft.com/en-US/library/windows/apps/ms684335.aspx
OpenThread = windll.kernel32.OpenThread
OpenThread.restype = wintypes.HANDLE
OpenThread.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
OpenThread.errcheck = assertNotNULL
OpenThread.__doc__ = """\
HANDLE OpenThread(
  DWORD dwDesiredAccess,
  BOOL bInheritHandle,
  DWORD dwThreadId
);
"""

# https://msdn.microsoft.com/en-US/library/windows/desktop/ms686717.aspx
TerminateThread = windll.kernel32.TerminateThread
TerminateThread.restype = wintypes.BOOL
TerminateThread.argtypes = (wintypes.HANDLE, wintypes.DWORD)
TerminateThread.errcheck = assertTrue
TerminateThread.__doc__ = """\
BOOL WINAPI TerminateThread(
  _Inout_ HANDLE hThread,
  _In_    DWORD  dwExitCode
);
"""

# https://msdn.microsoft.com/en-US/library/windows/desktop/ms724211.aspx
CloseHandle = windll.kernel32.CloseHandle
CloseHandle.restype = wintypes.BOOL
CloseHandle.argtypes = (wintypes.HANDLE, )
CloseHandle.errcheck = assertTrue
CloseHandle.__doc__ = """\
BOOL WINAPI CloseHandle(
  _In_ HANDLE hObject
);
"""

# https://msdn.microsoft.com/en-us/library/windows/apps/ms686769.aspx
THREAD_TERMINATE = 0x0001


@contextmanager
def closing(handle):
    yield handle
    CloseHandle(handle)


class ThreadTerminationWarning(RuntimeWarning):
    pass


class TerminatableThread(Thread):
    __termination_lock = Lock()

    def terminate(self, exit_code=1):
        """Terminate thread using Win32 API with freeing *less* resources"""
        with self.__termination_lock:
            warnings.warn(
                "Be aware that thread (ident=%s, name=%s) is being terminated "
                "by non-standard way, it would cause various problems such as "
                "generating uncollectable objects bounded to the thread and "
                "so on." % (self.ident, self.name),
                category=ThreadTerminationWarning, stacklevel=2)

            # Terminating native thread by Win32 API.
            with closing(OpenThread(THREAD_TERMINATE, False, self.ident)) as h:
                TerminateThread(h, exit_code)

            with _active_limbo_lock:
                # Updating table recording all active threads.
                del _active[self.ident]

                # Masquerading as stopped
                if hasattr(self, "_is_stopped"):  # Py3.6
                    self._is_stopped = True
                    self._tstate_lock.release()
                elif hasattr(self, "_Thread__stop"):  # Py2.7
                    self._Thread__stop()
