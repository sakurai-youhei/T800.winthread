'''
Created on 2017/05/16

@author: sakurai
'''

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from textwrap import dedent


HOMEPAGE = "https://github.com/sakurai-youhei/T800.winthread"
setup(
    version="2017.5.17",
    name="T800.winthread",
    packages=["T800"],
    license="MIT",
    author="Youhei Sakurai",
    author_email="sakurai.youhei@gmail.com",
    url=HOMEPAGE,
    description=(
        "Extension of threading.Thread adding terminate method "
        "using Win32 API on Python"
    ),
    long_description="See README on %s" % HOMEPAGE,
    classifiers=dedent("""\
        License :: OSI Approved :: MIT License
        Development Status :: 4 - Beta
        Environment :: Win32 (MS Windows)
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3.3
        Programming Language :: Python :: 3.4
        Programming Language :: Python :: 3.5
        Programming Language :: Python :: 3.6
        Operating System :: Microsoft :: Windows
        Intended Audience :: Developers
    """).splitlines(),
    keywords=dedent("""\
        Windows
        Win32
        ctypes
        threading
        Thread
        threading.Thread
        TerminatableThread
        OpenThread
        TerminateThread
        CloseHandle
    """).splitlines(),
)
