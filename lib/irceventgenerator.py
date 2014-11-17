#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import queue
from lib.irc import Irc, IrcError
from lib.twitchparser1 import TwitchParser1 as IrcParser

from gi.repository import GLib


class IrcEventGenerator:
    def __init__(self, config, glib_func, out_queue):
        """
        This class handles the Irc subclass to receive messages, and sends
        signals to the GUI after parsing those messages.
        """
        self.config = config
        self.glib_func = glib_func
        self.out_queue = out_queue

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
        while True:
            # Connect to IRC
            GLib.idle_add(self.glib_func, ['CONNECTING'])
            irc_sock = Irc(self.config)
            irc_sock.set_parser(IrcParser())
            try:
                irc_sock.connect('TWITCHCLIENT 2\r\n')
            except IrcError as e:
                logging.error('IRC error: {0}'.format(e.value))
                sys.exit(0)
            GLib.idle_add(self.glib_func, ['CONNECTED'])
            # Receive/send messages until disconnect
            try:
                while(True):
                    poll_time = self.config['irc']['poll_time']
                    if irc_sock.receive_message(timeout=poll_time):
                        messages = irc_sock.parse_message()
                        for msg in messages:
                            GLib.idle_add(self.glib_func, msg)
                    try:
                        out_msg = self.out_queue.get(block=False)
                        out_str = 'PRIVMSG {0} : {1}\r\n'.format(
                            self.config['irc']['channel'],
                            out_msg)
                        irc_sock.send_message(out_str, timeout=None)
                        event = ['MSG', self.config['irc']['user'], out_msg]
                        GLib.idle_add(self.glib_func, event)
                    except queue.Empty:
                        pass
            except IrcError:
                pass
            GLib.idle_add(self.glib_func, ['DISCONNECTED'])
