# address to listen on
addr = ('', 8080)

# log locations
log = '/var/log/tmp/tmp.log'
httplog = '/var/log/tmp/http.log'

# template directory to use
import os.path
template = os.path.dirname(__file__) + '/html'

# where service is located
service = 'https://tmp.fooster.io'

# where store is located
store = 'store.fooster.io'
store_https = True
store_endpoint = '/'

# interval for storing files
interval = 604800  # 1 week
