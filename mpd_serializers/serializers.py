from __future__ import (absolute_import, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)


from .introspection import all_text_is_unicode


def serialize_command(command, *args):
    '''
    Takes the name of a command and its *args list. Returns the command,
    serialized and ready to write to the socket.

    To specify ranges, pass in tuples of either one integer (to omit the end of
    the range), or two integers (to include the end of the range).
    '''

    parts = (command,) + tuple(_command_arg(arg) for arg in args)
    cmdline = ' '.join(parts)
    return '{}\n'.format(cmdline)


def _command_arg(arg):
    if type(arg) is tuple:
        if len(arg) == 1:
            return '"{}:"'.format(int(arg[0]))
        return '"{}:{}"'.format(int(arg[0]), int(arg[1]))
    return '"{}"'.format(_escape(_encode(arg)))


def _escape(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _encode(text):
    if all_text_is_unicode():
        return str(text)

    if type(text) is str:
        return text
    return (unicode(text)).encode("utf-8")
