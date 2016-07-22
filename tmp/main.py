import signal

from tmp import name, version
from tmp import log, http


log.tmplog.info(name + ' ' + version + ' starting...')

# start everything
http.start()


# cleanup function
def exit():
    http.stop()


# use the function for both SIGINT and SIGTERM
for sig in signal.SIGINT, signal.SIGTERM:
    signal.signal(sig, exit)
