from __future__ import (absolute_import, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

from .text_encoding import decode


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
    '''
    Given the results of a connection to MPD returns the version that was
    deserialized (as a string).
    '''

    decoded = decode(text)

    if not decoded.endswith('\n'):
        raise ConnectionError('Connection lost while reading MPD hello')

    for line in _iter_lines(decoded, command_list=False):
        if not line.startswith(HelloPrefix):
            message = "Got invalid MPD hello: '{}'".format(line)
            raise ProtocolError(message)

        return line[len(HelloPrefix):].strip()


def deserialize_nothing(text):
    '''
    Given a block of text returned from MPD, which is expected to be empty,
    validates it and returns None.
    '''

    decoded = decode(text)
    for line in _iter_lines(decoded, command_list=False):
        raise ProtocolError("Got unexpected return value: '{}'".format(line))


def deserialize_tuple(text):
    '''
    Given a block of text returned from MPD, deserializes it into a tuple.
    '''

    decoded = decode(text)
    lines = _iter_lines(decoded, command_list=False)
    items = _iter_items(lines, separator=': ')
    return tuple(items)


def deserialize_dict(text):
    '''
    Given a block of text returned from MPD, deserializes it into a dictionary.
    '''

    decoded = decode(text)
    lines = _iter_lines(decoded, command_list=False)
    for obj in _iter_objects(lines, separator=': ', delimiters=[]):
        return obj
    return {}


def deserialize_dicts(text):

    '''
    Given a block of text returned from MPD, deserializes it into a tuple of
    dictionaries.
    '''

    decoded = decode(text)
    lines = _iter_lines(decoded, command_list=False)
    return tuple(_iter_objects(lines, separator=': ', delimiters=['file']))


def _iter_items(lines, separator):

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
                if not isinstance(obj[key], tuple):
                    obj[key] = (obj[key], value)
                else:
                    obj[key] += (value,)
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
