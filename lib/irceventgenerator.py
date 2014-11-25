#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from lib.irc import Irc, IrcError
from lib.twitchparser1 import TwitchParser1 as IrcParser
import logging
import time

from gi.repository import GLib


class IrcEventGenerator:
    def __init__(self, config, func_queue):
        """
        This class handles the Irc subclass to receive messages, and sends
        signals to the GUI after parsing those messages.
        """
        self.config = config
        self.func_queue = func_queue
        self.glib_func = None

    def run(self):
        """
        Connect to the IRC server and send events to the GUI. This funtion is
        an endless loop that never exits, as it waits for a message before
        sending a signal to the GUI. If the connection to the server is lost,
        the connection is automatically re-established.

        In addition to the events defined by Irc, the following events are
        also sent:
        - CONNECTING: ['CONNECTING']
            Connecting to the server.
        - CONNECTED: ['CONNECTED']
            Connected to the server.
        - DISCONNECTED: ['DISCONNECTED']
            Connection to the server lost.
        """
        self.glib_func = self.func_queue.get()
        while True:
            # Connect to IRC
            GLib.idle_add(self.glib_func, ['CONNECTING'])
            irc_sock = Irc(self.config)
            irc_sock.set_parser(IrcParser())
            try:
                irc_sock.connect('TWITCHCLIENT 1\r\n')
            except IrcError as e:
                logging.error('IRC error: {0}'.format(e.value))
                time.sleep(1)
                continue
            GLib.idle_add(self.glib_func, ['CONNECTED'])
            # Receive messages until disconnect
            try:
                while(True):
                    if irc_sock.receive_message(timeout=None):
                        messages = irc_sock.parse_message()
                        for msg in messages:
                            GLib.idle_add(self.glib_func, msg)
            except IrcError:
                pass
            GLib.idle_add(self.glib_func, ['DISCONNECTED'])
