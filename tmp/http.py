import html
import re
import urllib.parse

import fooster.web
import fooster.web.form
import fooster.web.page

from tmp import config, tmp


fooster.web.form.max_file_size = config.max_size


alias_regex = '(?P<alias>[a-zA-Z0-9._-]+)'

http = None

routes = {}
error_routes = {}


class Interface(fooster.web.form.FormMixIn, fooster.web.page.PageHandler):
    reader = True

    directory = config.template
    page = 'index.html'
    message = ''

    def format(self, page):
        return page.format(message=self.message)

    def respond(self):
        try:
            return super().respond()
        except fooster.web.HTTPError as err:
            if err.code == 413:
                self.message = 'Upload is too large.'
                return super().do_get()

            raise

    def do_post(self):
        try:
            alias = self.request.body['alias']
            upload = self.request.body['file']
        except (KeyError, TypeError):
            raise fooster.web.HTTPError(400)

        if alias == '.' or alias == '..':
            raise fooster.web.HTTPError(400)

        try:
            if alias and not re.fullmatch(alias_regex, alias):
                raise NameError('alias ' + repr(alias) + ' invalid')

            alias = tmp.put(alias, upload)

            self.message = 'Successfully created at <a href="' + config.service.rstrip('/') + '/' + urllib.parse.quote(alias) + '">' + config.service.rstrip('/') + '/' + html.escape(alias) + '</a>.'
        except TypeError:
            self.message = 'No file specified. Choose a file.'
        except KeyError:
            self.message = 'This alias already exists. Wait until it expires or choose another.'
        except NameError:
            self.message = 'This alias is not valid. Choose one made up of alphanumeric characters only.'
        except ValueError:
            self.message = 'Upload is too large.'
        except RuntimeError:
            self.message = 'Could not upload data for some reason. Perhaps you should try again.'

        return self.do_get()


class ErrorInterface(fooster.web.page.PageErrorHandler):
    directory = config.template
    page = 'error.html'


class File(fooster.web.HTTPHandler):
    def do_get(self):
        alias = self.groups['alias']

        if alias == '.' or alias == '..':
            raise fooster.web.HTTPError(400)

        try:
            if not re.fullmatch(alias_regex, alias):
                raise KeyError(alias)

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


routes.update({'/': Interface, '/' + alias_regex: File})
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
