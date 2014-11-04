#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from lib.irc import Irc, IrcError
from lib.twitchparser1 import TwitchParser1 as IrcParser

from gi.repository import GLib


class IrcEventGenerator:
    def __init__(self, config, glib_func):
        self.config = config
        self.glib_func = glib_func

    def run(self):
        """
        Connect to the IRC server and send events to the GUI. In addition to
        the events defined by Irc, the following events are also sent:
        - CONNECTING: ['CONNECTING']
            Connecting to the server.
        - CONNECTED: ['CONNECTED']
            Connected to the server.
        - DISCONNECTED: ['DISCONNECTED']
            Connection to the server lost.
        """
        while True:
            # Connect to IRC
            GLib.idle_add(self.glib_func, ['CONNECTING'])
            irc_sock = Irc(self.config)
            irc_sock.set_parser(IrcParser())
            try:
                irc_sock.connect('TWITCHCLIENT 1\r\n')
            except IrcError as e:
                logging.error('IRC error: {0}'.format(e.value))
                sys.exit(0)
            GLib.idle_add(self.glib_func, ['CONNECTED'])
            # Receive messages until disconnect
            try:
                while(True):
                    if irc_sock.receive_message():
                        messages = irc_sock.parse_message()
                        for msg in messages:
                            GLib.idle_add(self.glib_func, msg)
            except IrcError:
                pass
            GLib.idle_add(self.glib_func, ['DISCONNECTED'])
