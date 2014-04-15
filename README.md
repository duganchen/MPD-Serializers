MPD-Serializers
===============

Routines to serialize commands to send to [MPD](http://www.mpd.org) (the Music
Player Daemon), and to deserialize strings returned from MPD.

The code is extracted (and slightly adapted) from python-mpd2. Here, it is
completely decoupled from any socket operations.

For documentation, please see the docstrings in serializers.py and
deserializers.py, as welell as the unit tests.
