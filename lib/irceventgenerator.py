#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from lib.irc import Irc
from lib.twitchparser1 import TwitchParser1 as IrcParser

from gi.repository import GLib


class IrcEventGenerator:
    def __init__(self, config, glib_func):
        self.config = config
        self.glib_func = glib_func

    def run(self):
        while True:
            # Connect to IRC
            irc_sock = Irc(self.config)
            irc_sock.set_parser(IrcParser())
            try:
                irc_sock.connect('TWITCHCLIENT 1\r\n')
            except IrcError as e:
                logging.error('IRC error: {0}'.format(e.value))
                sys.exit(0)
            # Receive messages untill disconnect
            try:
                while(True):
                    if irc_sock.receive_message():
                        messages = irc_sock.parse_message()
                        for msg in messages:
                            GLib.idle_add(self.glib_func, msg)
            except IrcError:
                pass
