# -*- coding: utf-8 -*-

from pyramid.compat import is_nonstr_iter

from ines.convert.codes import (inject_junk,
                                make_sha256,
                                make_sha256_no_cache)

from ines.convert.dates import (calculate_age,
                                convert_timezone,
                                date_to_timestamp,
                                guess_datetime,
                                maybe_date,
                                maybe_datetime,
                                total_seconds,
                                total_time_seconds)

from ines.convert.strings import (bytes_to_string,
                                  camelcase,
                                  clear_spaces,
                                  compact_dump,
                                  encode_and_decode,
                                  json_dumps,
                                  maybe_bytes,
                                  maybe_decimal,
                                  maybe_float,
                                  maybe_integer,
                                  maybe_null,
                                  maybe_string,
                                  maybe_string,
                                  pluralizing_key,
                                  pluralizing_word,
                                  prepare_for_json,
                                  to_bytes,
                                  to_string,
                                  uncamelcase)


def maybe_list(value):
    if value is None:
        return []
    elif not is_nonstr_iter(value):
        return [value]
    else:
        return list(value)


def maybe_set(value):
    if value is None:
        return set()
    elif not is_nonstr_iter(value):
        return set([value])
    else:
        return set(value)


def clear_price(number):
    return maybe_decimal(number, scale=2)
