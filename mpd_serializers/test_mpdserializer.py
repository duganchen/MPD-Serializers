'''
As with the code that it's testing, these unit tests are adapted from
python-mpd2.
'''

from __future__ import (absolute_import, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)


from . import serializers, deserializers
from nose.tools import eq_, raises


def test_serialize_command_1():

    expected = 'list "album"\n'
    actual = serializers.serialize_command('list', 'album')
    eq_(expected, actual)


def test_serialize_command_2():

    expected = 'delete "1:"\n'
    actual = serializers.serialize_command('delete', (1,))
    eq_(expected, actual)


def test_serialize_command_3():

    expected = 'delete "1:2"\n'
    actual = serializers.serialize_command('delete', (1, 2))
    eq_(expected, actual)


def test_deserialize_version():

    raw = u'OK MPD 0.18.0\n'
    expected = '0.18.0'
    actual = deserializers.deserialize_version(raw)
    eq_(expected, actual)


@raises(deserializers.ProtocolError)
def test_deserialize_version_invalid():

    raw = u'This is an invalid string\n'
    expected = '0.18.0'
    actual = deserializers.deserialize_version(raw)
    assert actual


@raises(deserializers.ConnectionError)
def test_deserialize_version_disconnect():

    raw = u'OK MPD 0.18.0'
    expected = '0.18.0'
    actual = deserializers.deserialize_version(raw)
    assert actual


def test_deserialize_nothing():
    eq_(None, deserializers.deserialize_nothing('OK\n'))


def test_deserialize_tuple():
    expected = ('J-Pop', 'Metal')
    raw_text = '\n'.join(['Genre: J-Pop', 'Genre: Metal', 'OK', ''])
    actual = deserializers.deserialize_tuple(raw_text)
    eq_(expected, actual)


def test_deserialize_dict():

    raw_text = '\n'.join(['volume: 63', 'OK', ''])
    expected = {'volume': '63'}
    actual = deserializers.deserialize_dict(raw_text)
    eq_(expected, actual)


def test_deserialize_dicts():

    raw_text = '\n'.join(['file: my-song.ogg', 'Pos: 0', 'Id: 66', 'OK', ''])
    expected = ({'file': 'my-song.ogg', 'pos': '0', 'id': '66'},)
    actual = deserializers.deserialize_dicts(raw_text)
    eq_(expected, actual)
