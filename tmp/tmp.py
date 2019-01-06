import json
import os
import time
import http.client

from tmp import config


def get(alias):
    # connect to API
    if config.store_https:
        conn = http.client.HTTPSConnection(config.store)
    else:
        conn = http.client.HTTPConnection(config.store)

    # request given alias
    conn.request('GET', config.store_endpoint + 'store/tmp/' + alias)

    # get response
    response = conn.getresponse()

    # check for 404
    if response.status == 404:
        raise KeyError()

    # get metadata
    download = {'size': response.getheader('Content-Length'), 'type': response.getheader('Content-Type'), 'filename': response.getheader('Content-Filename'), 'mtime': response.getheader('Last-Modified'), 'expire': response.getheader('Expires')}

    # store a file-like object
    download['file'] = response

    return download


def put(alias, upload):
    # connect to API
    if config.store_https:
        conn = http.client.HTTPSConnection(config.store)
    else:
        conn = http.client.HTTPConnection(config.store)

    # determine if this is a put or a post
    if alias:
        method = 'PUT'
    else:
        method = 'POST'

    # make a metadata request
    conn.request(method, config.store_endpoint + 'api/tmp/' + alias, headers={'Content-Type': 'application/json'}, body=json.dumps({'filename': upload['filename'], 'size': upload['length'], 'type': upload['type'], 'expire': time.time() + config.interval, 'locked': True}).encode('utf-8'))

    # get response
    response = conn.getresponse()

    # load data response
    data = json.loads(response.read().decode('utf-8'))

    # note bad requests - existing alias, bad name, and unknown error
    if response.status == 403:
        raise KeyError()
    elif response.status == 404:
        raise NameError()
    elif response.status != 201:
        raise ValueError()

    # make a data request
    conn.request('PUT', config.store_endpoint + 'store/tmp/' + data['alias'], body=upload['file'], headers={'Content-Length': str(os.fstat(upload['file'].fileno()).st_size)})

    # get response
    response = conn.getresponse()
    response.read()

    # note bad requests
    if response.status != 204:
        raise ValueError()

    return data['alias']
