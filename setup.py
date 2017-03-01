import os
from setuptools import setup, find_packages

from nrepl import __version__


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(CURRENT_DIR, "README.rst")) as long_description_file:
    long_description = long_description_file.read()

setup(
    name="nrepl",
    version=__version__,
    url="https://github.com/shonenada/nREPL-reloader",
    author="shonenada",
    author_email="shonenada@gmail.com",
    description="Auto reload class with Clojure nREPL",
    long_description=long_description,
    platforms='any',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'nrepl = nrepl.cli:cli',
        ]
    },
    classifiers=[
        'Environment :: Console',
        'Topic :: System :: Shells',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
    ]
)
