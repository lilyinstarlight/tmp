import json
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

    # request given alias
    conn.request('HEAD', config.store_endpoint + 'store/tmp/' + alias)

    # get response
    response = conn.getresponse()
    response.read()

    # check for existing alias
    if response.status != 404:
        raise KeyError()

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

    # note bad requests
    if response.status != 201:
        raise NameError()

    # make a data request
    conn.request('PUT', config.store_endpoint + 'store/tmp/' + data['alias'], body=upload['file'])

    # get response
    response = conn.getresponse()
    response.read()

    # note bad requests
    if response.status != 204:
        raise ValueError()

    return data['alias']
