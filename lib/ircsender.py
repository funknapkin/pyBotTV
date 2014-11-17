#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import logging
import queue
import time
from lib.irc import Irc, IrcError
from lib.twitchparser1 import TwitchParser1 as IrcParser


class IrcSender:
    def __init__(self, config, out_queue):
        """
        This class handles the Irc subclass to send messages. Messages
        are taken from a queue and sent as chat messages to the IRC channel.
        """
        self.config = config
        self.out_queue = out_queue

    def run(self):
        """
        Connect to the IRC server and wait for messages to send. If connection
        is lost, automatically reconnect.
        """
        while True:
            # Connect to IRC
            irc_sock = Irc(self.config)
            irc_sock.set_parser(IrcParser())
            try:
                irc_sock.connect()
            except IrcError as e:
                logging.error('IRC error: {0}'.format(e.value))
                time.sleep(1)
                continue
            # Send messages until disconnect
            while(True):
                out_msg = self.out_queue.get(block=True)
                out_str = 'PRIVMSG {0} : {1}\r\n'.format(
                    self.config['irc']['channel'],
                    out_msg)
                timeout = self.config['irc']['send_timeout']
                sent_success = irc_sock.send_message(out_str, timeout=timeout)
                if not sent_success:
                    logging.warning(
                        'IRC: failed to send chat message {0}'.format(out_str))
                    break
            GLib.idle_add(self.glib_func, ['DISCONNECTED'])
