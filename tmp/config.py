# address to listen on
addr = ('', 8000)

# log locations
log = '/var/log/tmp/tmp.log'
http_log = '/var/log/tmp/http.log'

# template directory to use
import os.path
template = os.path.dirname(__file__) + '/html'

# where service is located
service = 'https://tmp.lily.flowers'

# where store is located
store = 'https://store.lily.flowers'

# interval for storing files
interval = 604800  # 1 week

# maximum file size
max_size = 33554432  # 32 MB
