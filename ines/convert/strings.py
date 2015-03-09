# -*- coding: utf-8 -*-

import re

from ines import CAMELCASE_UPPER_WORDS


REPLACE_CAMELCASE_REGEX = re.compile(u'[^A-Z0-9_.]').sub
NULLS = frozenset([u'null', u'', u'none'])


def force_unicode(value, encoding='utf-8', errors='strict'):
    if isinstance(value, unicode):
        return value
    elif isinstance(value, str):
        return value.decode(encoding, errors)
    else:
        return unicode(str(value), encoding, errors)


def force_string(value, encoding='utf-8', errors='strict'):
    if isinstance(value, str):
        return value
    elif isinstance(value, unicode):
        return value.encode(encoding, errors)
    else:
        return str(value)


def maybe_integer(value):
    try:
        result = int(value)
    except (TypeError, ValueError):
        pass
    else:
        return result


def maybe_null(value):
    if value is None:
        return None
    elif force_unicode(value).strip().lower() in NULLS:
        return None
    else:
        return value


def maybe_unicode(value, encoding='utf-8', errors='strict'):
    if value or value is 0:
        return force_unicode(value, encoding, errors)


def camelcase(value):
    value = force_unicode(value).strip()
    if not value:
        return value
    elif u'+' in value:
        return u'+'.join(camelcase(key) for key in value.split(u'+'))

    words = [w for w in REPLACE_CAMELCASE_REGEX(u'_', value.upper()).split(u'_') if w]
    if not words:
        return u''
    else:
        camelcase_words = [words.pop(0).lower()]
        for word in words:
            if word in CAMELCASE_UPPER_WORDS:
                camelcase_words.append(word)
            else:
                camelcase_words.append(word.title())
        return u''.join(camelcase_words)


def uncamelcase(value):
    count = 0
    words = {}
    previous_is_upper = False
    for letter in force_unicode(value):
        if letter.isupper():
            if not previous_is_upper:
                count += 1
            else:
                maybe_upper_name = (u''.join(words[count]) + letter).upper()
                if maybe_upper_name not in CAMELCASE_UPPER_WORDS:
                    count += 1
            previous_is_upper = True

        else:
            if previous_is_upper:
                maybe_upper_name = (u''.join(words[count]) + letter).upper()
                if maybe_upper_name not in CAMELCASE_UPPER_WORDS:
                    words[count + 1] = [words[count].pop()]
                    count += 1
            previous_is_upper = False

        words.setdefault(count, []).append(letter)

    words = words.items()
    words.sort()

    final_words = []
    for count, letters in words:
        if letters:
            final_words.append(u''.join(letters))
    return u'_'.join(final_words).lower()
