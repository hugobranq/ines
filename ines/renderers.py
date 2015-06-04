# -*- coding: utf-8 -*-

import datetime
from json import dumps

from colander import Mapping
from colander import Sequence

from ines import DEFAULT_RENDERERS
from ines.convert import camelcase
from ines.convert import force_unicode


DATE = datetime.date
DATETIME = datetime.datetime


class CSVResponse(list):
    def append_header(self, title):
        if not self:
            self[0] = []
        self[0].append(title)

    def append_item(self, position, value):
        if not self:
            self[0] = []
        self[position].append(value)

    def join(self, response):
        if response:
            add_items = len(response) - len(self)
            if add_items > 0:
                for i in xrange(add_items):
                    self.append([])

            for i, values in enumerate(response):
                self[i].extend(values)


class CSV(object):
    def lookup_header(self, node):
        if isinstance(node.typ, Sequence):
            return self.lookup_row(node.children[0])

        elif isinstance(node.typ, Mapping):
            header = []
            for child in node.children:
                header.extend(self.lookup_header(child))
            return header

        else:
            return [node.title]

    def lookup_row(self, node, value):
        if isinstance(node.typ, Sequence):
            return self.lookup_row(node.children[0], value)

        elif isinstance(node.typ, Mapping):
            row = []
            for child in node.children:
                if isinstance(value, dict):
                    row.extend(self.lookup_row(child, value.get(camelcase(node.name))))
                else:
                    row.extend(self.lookup_row(child, getattr(value, child.name, None)))
            return row

        else:
            return [value]

    def lookup_rows(self, node, values):
        rows = [self.lookup_header(node)]
        for value in values:
            rows.append(self.lookup_row(node, value))
        return rows

    def __call__(self, info):
        def _render(value, system):
            request = system.get('request')
            if request is not None:
                response = request.response
                ct = response.content_type
                if ct == response.default_content_type:
                    response.content_type = 'text/csv'

                output = request.registry.config.lookup_output_schema(
                    request.matched_route.name,
                    request_method=request.method)
                if output:
                    value = self.lookup_rows(output[0].schema.children[0], value)

            separator = u';'
            separator_replace = u','
            line_break = u'\n'
            line_break_replace = u' '

            lines = []
            for value_items in value:
                row = []
                for item in value_items:
                    if item is None:
                        item = u''

                    elif isinstance(item, bool):
                        if item:
                            item = u'true'
                        else:
                            item = u'false'

                    elif isinstance(item, (int, basestring, long)):
                        item = force_unicode(item)

                    elif isinstance(item, (DATE, DATETIME)):
                        item = item.isoformat()

                    else:
                        item = dumps(item)

                    if u'"' in item:
                        item = u'"%s"' % item.replace(u'"', u'\\"')

                    item = item.replace(separator, separator_replace)
                    item = item.replace(line_break, line_break_replace)
                    row.append(item)

                lines.append(separator.join(row))
            return line_break.join(lines)

        return _render


csv_renderer_factory = CSV()  # bw compat
DEFAULT_RENDERERS['csv'] = csv_renderer_factory
