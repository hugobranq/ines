# -*- coding: utf-8 -*-

from json import dumps
from json import loads
from urllib2 import quote

from webob.request import environ_add_POST

from ines.convert import force_string
from ines.convert import maybe_list
from ines.exceptions import HTTPInvalidJSONPayload
from ines.middlewares import Middleware
from ines.utils import get_content_type
from ines.utils import format_error_to_json


class Payload(Middleware):
    name = 'payload'

    def __call__(self, environ, start_response):
        content_type = get_content_type(environ.get('CONTENT_TYPE'))
        if content_type == 'application/json' and 'wsgi.input' in environ:
            body = environ['wsgi.input'].read()
            if body:
                arguments = []
                try:
                    body_json = loads(body)
                    for key, values in dict(body_json).items():
                        key = force_string(key)
                        values = maybe_list(values)
                        for value in values:
                            if value is None:
                                arguments.append('%s=' % key)
                            else:
                                arguments.append('%s=%s' % (key, quote(dump_query_value(value))))
                    body = '&'.join(arguments)
                except (ValueError, UnicodeEncodeError):
                    headers = [('Content-type', 'application/json')]
                    error = HTTPInvalidJSONPayload()
                    start_response(error.status, headers)
                    return format_error_to_json(error)

            environ_add_POST(environ, body or '')

        return self.application(environ, start_response)


def dump_query_value(value):
    if isinstance(value, basestring):
        return force_string(value)
    else:
        return force_string(dumps(value))
