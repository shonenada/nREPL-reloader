import os
from setuptools import setup


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


setup(
    name="repl",
    version="0.1.0",
    url="https://github.com/shonenada/nREPL-reloader",
    author="shonenada",
    platforms='any',
    entry_points={
        'console_scripts': [
            'nrepl = nrepl.core:cli',
        ]
    },
    classifiers=[
        'Environment :: Console',
        'Topic :: System :: Shells'
    ]
)
