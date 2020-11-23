import json as _json
import logging as _logging
import os as _os
import os.path as _path
import sys as _sys

import fooster.web as _web


# address to listen on
addr = ('', 8000)

# log locations
log = '/var/log/tmp/tmp.log'
http_log = '/var/log/tmp/http.log'

# template directory to use
template = _path.dirname(__file__) + '/html'

# where service is located
service = 'https://tmp.lily.flowers'

# where store is located
store = 'https://store.lily.flowers'

# interval for storing files
interval = 604800  # 1 week

# maximum file size
max_size = 33554432  # 32 MB


# store config in env var
def _store():
    config = {key: val for key, val in globals().items() if not key.startswith('_')}

    _os.environ['TMP_CONFIG'] = _json.dumps(config)


# load config from env var
def _load():
    config = _json.loads(_os.environ['TMP_CONFIG'])

    globals().update(config)

    # automatically apply
    _apply()


# apply special config-specific logic after changes
def _apply():
    # setup logging
    if log:
        _logging.getLogger('tmp').addHandler(_logging.FileHandler(log))
    else:
        _logging.getLogger('tmp').addHandler(_logging.StreamHandler(_sys.stdout))

    if http_log:
        http_log_handler = _logging.FileHandler(http_log)
        http_log_handler.setFormatter(_web.HTTPLogFormatter())

        _logging.getLogger('http').addHandler(http_log_handler)

    # automatically store if not already serialized
    if 'TMP_CONFIG' not in _os.environ:
        _store()


# load if config already serialized in env var
if 'TMP_CONFIG' in _os.environ:
    _load()
