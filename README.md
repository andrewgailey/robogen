robogen
=======
### A Machine Learning approach to [Robot Game](http://robotgame.net/)

Usage
-----

    usage: robogen.py [-h] [-l LOAD_FILE] [-s SAVE_FILE] [-g GENS] [-p PROCESSES]

    Robogen execution script.

    optional arguments:
      -h, --help            show this help message and exit
      -l LOAD_FILE, --load_file LOAD_FILE
                            File containing a previously saved Generation.
      -s SAVE_FILE, --save_file SAVE_FILE
                            File to save last Generation to.
      -g GENS, --gens GENS  Number of generations to run.
      -p PROCESSES, --processes PROCESSES
                            Number of worker processes allowed to run simultaneously.

Acknowledgements
---------------

**rgkit**

This software uses a modified version of 
[rgkit](https://github.com/RobotGame/rgkit), the game engine for Robot Game.

**robotgame-bots**

This software includes open-source bots from 
[robotgame-bots](https://github.com/mpeterv/robotgame-bots).
