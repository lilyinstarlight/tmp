import time
import http.client

from tmp import config


def get(alias):
    # connect to API
    conn = http.client.HTTPSConnection(config.store)

    # request given alias
    conn.request('GET', '/store/tmp/' + alias)

    # get response
    response = conn.getresponse()

    # check for 404
    if response.status == 404:
        raise KeyError()

    # get metadata
    download = {'type': response.getheader('Content-Type'), 'filename': response.getheader('Content-Filename'), 'mtime': response.getheader('Last-Modified'), 'expire': response.getheader('Expires')}

    # store a file-like object
    download['file'] = response

    return download


def put(alias, upload):
    # connect to API
    conn = http.client.HTTPSConnection(config.store)

    # request given alias
    conn.request('GET', '/store/tmp/' + alias)

    # get response
    response = conn.getresponse()

    # check for existing alias
    if response.status != 404:
        raise KeyError()

    # determine if this is a put or a post
    if alias:
        method = 'PUT'
    else:
        method = 'POST'

    # make a metadata request
    conn.request(method, '/api/tmp/' + alias, body=json.dumps({'filename': upload['filename'], 'size': upload['length'], 'type': upload['type'], 'expire': time.time() + config.interval, 'locked': True}).encode('utf-8'))

    # get response
    response = json.loads(conn.getresponse())

    # make a data request
    conn.request('PUT', '/store/tmp/' + response['alias'], body=upload['file'])

    # get response
    conn.getresponse()
