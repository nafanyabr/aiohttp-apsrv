# aiohttp-apsrv
Example implementation of an API for async counting AP (arithmetic progression) with aiohttp server.

Stack: Python 3.6, aiohttp

This project uses [poetry](https://python-poetry.org/) for dependency management, so, after activating virtualenv, run:
```
poetry install --no-dev
```
or, if you want install some dev libs like flake8, mypy and other (see poetry.lock file), just type
```
poetry install
```

Usage:
```
run.py [-h] [-w WORKERS] [-m]

optional arguments:
  -h, --help            show this help message and exit
  -w WORKERS, --workers WORKERS
                        Setup workers count for async tasks (default and minimum workers = 3)
  -m, --monitor         Start monitoring tasks queue in cli every second
```
You can define number of workers for async counting AP. One worker can do one AP cycle. If task's queue gt number of workers, new task will be waiting for first free worker with status 'SHEDULED'.

After running server works on http://127.0.0.1:8080/tasks and ready for POST and GET requests.

## Parameters
Add task (POST request) - JSON:
- count - count of AP elements (int) > 0
- delta - AP delta (float)
- start - start value (float)
- interval - sleep time between iterations in seconds (float)

Example:
```
>>> import requests

>>> # Add task of counting AP with some parameters
>>> res = requests.post('http://127.0.0.1:8080/tasks', json={"count": 10, "delta": 1.2, "start": 0.8, "interval": 1.4})
```

2. Get list of tasks with statuses (GET request) - JSON:
- task id
- status: In progress/Sheduled
- count
- delta
- start
- interval
- current value
- task's start date

Example:
```
>>> import requests
>>> res = requests.get('http://127.0.0.1:8080/tasks')
>>> print(res.json())

[
    {
        "count": 10,
        "date_start": "2020-11-27T16:09:24Z",
        "delta": 1.2,
        "interval": 1.4,
        "start": 1.0,
        "status": "IN PROGRESS",
        "uid": 6,
        "value": 2.4
    }
]
```

## TBD
- tests with pytest-aiohttp
