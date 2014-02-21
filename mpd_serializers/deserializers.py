from __future__ import (absolute_import, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

from .introspection import all_text_is_unicode


class MPDError(Exception):
    pass


class CommandError(MPDError):
    pass


class ConnectionError(MPDError):
    pass


class ProtocolError(MPDError):
    pass


ErrorPrefix = 'ACK '
HelloPrefix = 'OK MPD '
Next = "list_OK"
Success = "OK"


def deserialize_version(text):

    decoded = _decode(text)

    if not decoded.endswith('\n'):
        raise ConnectionError('Connection lost while reading MPD hello')

    for line in _iter_lines(decoded, command_list=False):
        if not line.startswith(HelloPrefix):
            message = "Got invalid MPD hello: '{}'".format(line)
            raise ProtocolError(message)

        return line[len(HelloPrefix):].strip()


def deserialize_nothing(text):

    decoded = _decode(text)
    for line in _iter_lines(decoded, command_list=False):
        raise ProtocolError("Got unexpected return value: '{}'".format(line))


def deserialize_tuple(text):
    decoded = _decode(text)
    lines = _iter_lines(decoded, command_list=False)
    items = _iter_listitems(lines, separator=': ')
    return tuple(items)


def deserialize_dict(text):

    decoded = _decode(text)
    lines = _iter_lines(decoded, command_list=False)
    for obj in _iter_objects(lines, separator=': ', delimiters=[]):
        return obj
    return {}


def deserialize_songs(text):

    decoded = _decode(text)
    lines = _iter_lines(decoded, command_list=False)
    return tuple(_iter_objects(lines, separator=': ', delimiters=['file']))


def _iter_listitems(lines, separator):

    seen = None
    for key, value in _iter_pairs(lines, separator):
        if key != seen:
            if seen is not None:
                message = "Expected key '{}', got '{}'".format(seen, key)
                raise ProtocolError(message)
            seen = key
        yield value


def _iter_objects(lines, separator, delimiters):
    obj = {}
    for key, value in _iter_pairs(lines, separator):
        key = key.lower()
        if obj:
            if key.lower() in delimiters:
                yield obj
                obj = {}
            elif key.lower() in obj:
                if not isinstance(obj[key], list):
                    obj[key] = [obj[key], value]
                else:
                    obj[key].append(value)
                continue
        obj[key] = value
    if obj:
        yield obj


def _iter_lines(decoded_text, command_list=False):

    if not decoded_text.endswith('\n'):
        raise ConnectionError('Connection lost while reading line')

    for line in decoded_text.split('\n')[:-1]:
        if line.startswith(ErrorPrefix):
            error = line[len(ErrorPrefix):].strip()
            raise CommandError(error)
        if command_list:
            if line == Next:
                continue
            if line == Success:
                raise ProtocolError("Got unexpected '%s'".format(Success))
        elif line != Success:
            yield line


def _iter_pairs(lines, separator):

    for line in lines:
        pair = line.split(separator, 1)
        if len(pair) < 2:
            raise ProtocolError("Could not parse pair: '{}'".format(line))
        yield pair


def _decode(text):

    if all_text_is_unicode():
        return text

    return text.decode('utf-8')
