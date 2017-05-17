'''
Created on 2017/05/16

@author: sakurai
'''
from contextlib import closing
from multiprocessing.connection import Pipe
from multiprocessing.dummy import Pool
try:
    from queue import Queue  # Py3
except ImportError:
    from Queue import Queue  # Py2
from subprocess import Popen
import sys
import threading
import time
from unittest import main
from unittest import TestCase
from unittest import TestLoader
import warnings

from T800.winthread import TerminatableThread
from T800.winthread import ThreadTerminationWarning


class T800WinThreadTest(TestCase):
    WAITSEC = 1
    PYSCRIPT_SYS_EXIT = (
        "import sys;"
        "from T800.winthread import TerminatableThread as T;"
        "t = T(target=sys.stdin.read);"
        "t.start();"
        "t.terminate();"
        "sys.exit(0);"
    )

    def setUp(self):
        warnings.simplefilter("ignore", category=ThreadTerminationWarning)

        # Preserving current statuses
        self.active_count = threading.active_count()
        self.all_threads = threading.enumerate()

    def tearDown(self):
        # Comparing current statuses with preserved ones
        self.assertEqual(self.active_count, threading.active_count())
        self.assertEqual(set(self.all_threads), set(threading.enumerate()))

        warnings.resetwarnings()

    def _start_threads(self, target, num_threads):
        """Overwrite here when you reuse the test case with your own thread"""
        threads = []
        for _ in range(num_threads):
            t = TerminatableThread(target=target)
            t.start()
            threads.append(t)
        return threads

    def _terminate_still_alive(self, threads):
        """Invoke terminate() method concurrently"""
        with closing(Pool(len(threads) // 4)) as pool:
            for t in filter(lambda t: t.is_alive(), threads):
                pool.apply_async(t.terminate)
        pool.join()
        pool.terminate()

    def assertNumAliveThreads(self, num_threads, threads, msg=None):
        self.assertEqual(
            num_threads, len([t for t in threads if t.is_alive()]), msg)

    def test_terminate_method_with_Pipe(self, num_threads=50):
        readable, writable = Pipe(duplex=False)
        threads = self._start_threads(readable.recv_bytes, num_threads)

        writable.send_bytes(b"spam")
        time.sleep(self.WAITSEC)
        self.assertNumAliveThreads(
            num_threads - 1, threads, "No thread has ended, %r" % threads)

        self._terminate_still_alive(threads)
        for t in threads:
            self.assertRaises(OSError, t.terminate)
        self.assertNumAliveThreads(
            0, threads, "Some threads are still alive, %r" % threads)

        for i in range(num_threads):
            writable.send_bytes(b"%d" % i)
            self.assertEqual(b"%d" % i, readable.recv_bytes(),
                             "Someone seems to intercept pipe, %r" % threads)

    def test_terminate_method_with_Queue(self, num_threads=50):
        q = Queue()
        threads = self._start_threads(q.get, num_threads)

        q.put(None)
        time.sleep(self.WAITSEC)
        self.assertNumAliveThreads(
            num_threads - 1, threads, "No thread has ended, %r" % threads)

        self._terminate_still_alive(threads)
        for t in threads:
            self.assertRaises(OSError, t.terminate)
        self.assertNumAliveThreads(
            0, threads, "Some threads are still alive, %r" % threads)

        for i in range(num_threads):
            q.put(i)
            self.assertEqual(i, q.get(timeout=self.WAITSEC),
                             "Someone seems to intercept queue, %r" % threads)

    def test_terminate_method_with_join_method(self):
        t1 = self._start_threads(sys.stdin.read, 1)[0]
        t2 = self._start_threads(t1.join, 1)[0]

        self.assertTrue(t2.is_alive(), t2)  # t2 is blocked due to running t1
        t1.terminate()
        time.sleep(self.WAITSEC)

        self.assertFalse(t2.is_alive(), t2)  # t2 stops due to terminated t1

    def test_terminate_method_with_sys_exit(self):
        args = [sys.executable, "-W", "ignore", "-c", self.PYSCRIPT_SYS_EXIT]
        p = Popen(args)
        for _ in range(int(2 * self.WAITSEC + 1)):
            returncode = p.poll()
            if returncode is not None:
                self.assertEqual(0, returncode, p)
                break
            else:
                time.sleep(1)
        else:
            p.terminate()
            self.fail("Python hasn't stopped expectedly, %r" % p)


def suite():
    return TestLoader().loadTestsFromTestCase(T800WinThreadTest)


if __name__ == "__main__":
    main()
