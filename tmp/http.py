import os
import time

import web, web.form, web.page

from tmp import config, log, tmp


alias = '([a-zA-Z0-9._-]+)'

http = None

routes = {}
error_routes = {}


class Interface(web.page.PageHandler, web.form.FormHandler):
    directory = os.path.dirname(__file__) + '/html'
    page = 'index.html'
    message = ''

    def format(self, page):
        return page.format(message=self.message)

    def do_post(self):
        try:
            alias = self.request.body['alias']
            upload = self.request.body['file']
        except (KeyError, TypeError):
            raise web.HTTPError(400)

        try:
            alias = tmp.put(alias, upload)

            self.message = 'Successfully created at <a href="' + config.service + '/' + alias + '">' + config.service + '/' + alias + '</a>.'
        except KeyError:
            self.message = 'This alias already exists. Wait until it expires or choose another.'

        return self.do_get()


class ErrorInterface(web.page.PageErrorHandler):
    directory = os.path.dirname(__file__) + '/html'
    page = 'error.html'


class File(web.HTTPHandler):
    def do_get(self):
        alias = self.groups[0]

        try:
            download = tmp.get(alias)
        except KeyError:
            raise web.HTTPError(404)

        # set headers
        self.response.headers['Content-Length'] = download['size']
        self.response.headers['Content-Type'] = download['type']
        self.response.headers['Content-Disposition'] = 'attachment; filename="' + download['filename'] + '"'
        self.response.headers['Last-Modified'] = download['mtime']
        self.response.headers['Expires'] = download['expire']

        # return file-like object
        return 200, download['file']


routes.update({'/': Interface, '/' + alias: File})
error_routes.update(web.page.new_error(handler=ErrorInterface))


def start():
    global http

    http = web.HTTPServer(config.addr, routes, error_routes, log=log.httplog)
    http.start()


def stop():
    global http

    http.stop()
    http = None
