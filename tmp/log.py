import log

from tmp import config

tmplog = log.Log(config.log)
httplog = log.HTTPLog(config.log, config.httplog)
