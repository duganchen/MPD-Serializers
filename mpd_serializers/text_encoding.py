from __future__ import (absolute_import, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import sys


def decode(text):

    if all_text_is_unicode():
        return text

    return text.decode('utf-8')


def encode(text):
    if all_text_is_unicode():
        return str(text)

    if type(text) is str:
        return text
    return (unicode(text)).encode("utf-8")


def all_text_is_unicode():
    return sys.version_info.major > 2
