import html
import urllib.parse

import fooster.web, fooster.web.form, fooster.web.page

from tmp import config, tmp


alias = '(?P<alias>[a-zA-Z0-9._-]+)'

http = None

routes = {}
error_routes = {}


class Interface(fooster.web.page.PageHandler, fooster.web.form.FormHandler):
    nonatomic = True

    directory = config.template
    page = 'index.html'
    message = ''

    def format(self, page):
        return page.format(message=self.message)

    def do_post(self):
        try:
            alias = self.request.body['alias']
            upload = self.request.body['file']
        except (KeyError, TypeError):
            raise fooster.web.HTTPError(400)

        try:
            alias = tmp.put(alias, upload)

            self.message = 'Successfully created at <a href="' + config.service + '/' + urllib.parse.quote(alias) + '">' + config.service + '/' + html.escape(alias) + '</a>.'
        except TypeError:
            self.message = 'No file specified. Choose a file.'
        except KeyError:
            self.message = 'This alias already exists. Wait until it expires or choose another.'
        except NameError:
            self.message = 'This alias is not valid. Choose one made up of alphanumeric characters only.'
        except ValueError:
            self.message = 'Could not upload data for some reason. Perhaps you should try again.'

        return self.do_get()


class ErrorInterface(fooster.web.page.PageErrorHandler):
    directory = config.template
    page = 'error.html'


class File(fooster.web.HTTPHandler):
    def do_get(self):
        alias = self.groups['alias']

        try:
            download = tmp.get(alias)
        except KeyError:
            raise fooster.web.HTTPError(404)

        # set headers
        self.response.headers['Content-Length'] = download['size']
        self.response.headers['Content-Type'] = download['type']
        self.response.headers['Content-Disposition'] = 'attachment; filename="' + download['filename'] + '"'
        self.response.headers['Last-Modified'] = download['mtime']
        self.response.headers['Expires'] = download['expire']

        # return file-like object
        return 200, download['file']


routes.update({'/': Interface, '/' + alias: File})
error_routes.update(fooster.web.page.new_error(handler=ErrorInterface))


def start():
    global http

    http = fooster.web.HTTPServer(config.addr, routes, error_routes)
    http.start()


def stop():
    global http

    http.stop()
    http = None


def join():
    global http

    http.join()
