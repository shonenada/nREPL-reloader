nREPL-reloader
==============

Auto reload class with `nREPL <(https://github.com/clojure/tools.nrepl>`_.

Quick Start
-----------

1. Install `nrepl` by `pip`::

    $ pip install nrepl

2. Start watching clojure files, Run `nrepl` with watch command:: 

    $ nrepl watch -p 59258 -w /path/to/project
    Start watching /home/shonenada/Projects/clojure/src
    Detected changes of /home/shonenada/Projects/clojure/src/route.clj, reloading

3. (or) Start clojure project (`lein run`) and watch clojure files::

    $ nrepl run -p 59258 -w /path/to/project
    [lein]: Compiling 1 source files...
    [lein]: Start server on 8080
    [nrepl]: Start watching /home/shonenada/Projects/clojure/src
    [nrepl]: Detected changes of /home/shonenada/Projects/clojure/src/route.clj, reloading

