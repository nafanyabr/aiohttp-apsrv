# aiohttp-apsrv
Example of aiohttp-server for async counting AP (arithmetic progression)

Stack: Python 3.6, aiohttp

This project uses [poetry](https://python-poetry.org/) for dependency management, so after activating
virtualenv, run:
```
poetry install
```

Usage: 
```
run.py [-h] [-w WORKERS] [-m]

optional arguments:
  -h, --help            show this help message and exit
  -w WORKERS, --workers WORKERS
                        Setup workers count for async tasks (default and
                        minimum workers = 3)
  -m, --monitor         Start monitoring tasks queue in cli every 1 second
```