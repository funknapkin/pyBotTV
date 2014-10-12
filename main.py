#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import logging
import sys

import lib.config as config
import lib.irc as irc


def main():
    c = config.config('./config.yaml')
    # Configure logger
    log_levels = {
        'debug': logging.DEBUG, 'info': logging.INFO,
        'warning': logging.WARNING, 'error': logging.ERROR,
        'critical': logging.CRITICAL}
    logging.basicConfig(
        filename=c['debug']['log-file'], filemode='w',
        level=log_levels[c['debug']['log-level']])
    # Main loop
    while True:
        # Connect to IRC
        irc_sock = irc.irc(c)
        try:
            irc_sock.connect()
        except irc.ircException as e:
            logging.error('IRC error: {0}'.format(e.value))
        # Receive messages
        while(irc_sock.receiveMessage()):
            irc_sock.parseMessage()

if __name__ == "__main__":
    main()
