#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import logging
import re
import socket


class IrcError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Irc:
    def __init__(self, config):
        """Build an irc object to interact with a single IRC chat room.

        This class contains multiple utilities to handle an IRC chat room, such
        as connecting to a predefined chat room specified in the config file,
        receiving messages and parsing messages.

        Args:
            config: config object. See config.py and config.yaml.
        """
        self.config = config

    def connect(self, post_init_msg=None):
        """
        Connect to the server defined in the config file.

        Raises:
            IrcError if the connection failed for any reason.
            IrcError.value is a string describing the reason the connection
            failed.
        """
        if not self.parser:
            raise IrcError('No parser defined before connecting')
        # Connect to server
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.config['irc']['server'],
                          self.config['irc']['port']))
            logging.info(
                'IRC: connected to the server {0}:{1}'.format(
                    self.config['irc']['server'], self.config['irc']['port']))
        except Exception as e:
            raise IrcError('Cannot connect to the server')
        # Login to the IRC chat room
        sock.settimeout(5)
        send_data = 'USER {0}\r\n'.format(self.config['irc']['user']).encode()
        if sock.send(send_data) != len(send_data):
            raise IrcError('Failed to send login data to the server')
        send_data = 'PASS {0}\r\n'.format(
            self.config['irc']['password']).encode()
        if sock.send(send_data) != len(send_data):
            raise IrcError('Failed to send login data to the server')
        send_data = 'NICK {0}\r\n'.format(self.config['irc']['user']).encode()
        if sock.send(send_data) != len(send_data):
            raise IrcError('Failed to send login data to the server')
        response = sock.recv(
            self.config['irc']['buffer_size']).decode().rstrip()
        if self.parser.check_connection_success(response):
            logging.info('IRC: successfully logged in with username {0}'
                         .format(self.config['irc']['user']))
        else:
            raise IrcError('Login failed with message {0}'.format(response))
        # Send post-init message to the server
        if type(post_init_msg) == str or type(post_init_msg) == bytes:
            sock.settimeout(None)
            try:
                if type(post_init_msg) == str:
                    post_init_msg = post_init_msg.encode()
                bytes_sent = sock.send(post_init_msg)
                if bytes_sent != len(post_init_msg):
                    raise IrcError(
                        'Failed to send post-init message to the server')
            except socket.timeout:
                raise IrcError(
                    'Failed to send post-init message to the server')
        # Join channel
        sock.send('JOIN {0}\r\n'.format(
            self.config['irc']['channel']).encode())
        logging.info('IRC: joined channel {0}'.format(
            self.config['irc']['channel']))
        # Change self variable and return
        self.sock = sock
        self.message = ''
        return

    def parse_message(self):
        """
        Parse a message, doing any IRC-related work before returning.
        (ex: sending PONG after a PING).

        Returns:
            A list with parsed data related to the event. The list has 1 item
            per event (i.e. [event1, event2, etc.]). Each event is also
            represented by a list. The possible events, as well as their list's
            structure, are the following:
            - JOIN: ['JOIN', 'username 1', 'username 2', ...]
                One or more user(s) joined the channel. This also includes the
                'NAMES' message sent when joining the channel.
            - PART: ['PART', 'username 1', 'username 2', ...]
                One or more user(s) left the channel.
            - MSG: ['MSG', 'username', 'message']
                A user sent a message to the channel.
            - MOD: ['MOD', 'username']
                A user was given mod status on the channel.
            - DEMOD: ['DEMOD', 'username']
                A mod was demoted on the channel.
            - SUBSCRIBER: ['SUBSCRIBER', 'username']
                A user subscribed to the channel.
            - USERCOLOR: ['USERCOLOR', 'username', 'color']
                Information on a user's color. Format for the color is #FFFFFF.
            - EMOTESET: ['EMOTESET', 'username', emoteset1, emoteset2, ...]
                A list of emoteset a user has access to.
            - SPECIALUSER: ['SPECIALUSER', 'username', 'type']
                Information on a user's special status.
            - TIMEOUT: ['TIMEOUT', 'username']
                A user has been banned or timed out.
            - CLEARCHAT: ['CLEARCHAT']
                A moderator has cleared the chat.
        """
        # Split messages for parsing
        messages = self.message.split('\r\n')
        if self.message[-2:] != '\r\n':
            self.message = messages[-1]
        else:
            self.message = ''
        messages = messages[:-1]
        # Pass messages to the parser
        retval = []
        for msg in messages:
            logging.debug('IRC chat in: {0}'.format(msg))
            parsed_msg = self.parser.parse_message(msg)
            if parsed_msg is None:
                logging.warning('IRC could not parse message: {0}'.format(msg))
            elif parsed_msg[0] == 'PING':
                self.sock.send(self.parser.pong_message.encode())
                logging.debug('IRC chat out: {0}'
                              .format(self.parser.pong_message).rstrip())
            else:
                logging.debug('IRC event: {0}'.format(parsed_msg))
                retval.append(parsed_msg)
        return retval

    def receive_message(self, timeout=None):
        """
        Wait for a message on the IRC channel.

        Args:
            Timeout in seconds, or None for no timeout.

        Returns:
            True if a message was received, False otherwise

        Raises:
            IrcError if the connection was lost.
        """
        if not self.sock:
            return False
        self.sock.settimeout(timeout)
        try:
            new_message = self.sock.recv(
                self.config['irc']['buffer_size']).decode()
        except socket.timeout:
            return False
        self.message = self.message + new_message
        if len(new_message) == 0:
            logging.warning('IRC: connection lost')
            raise IrcError('Connection lost')
        else:
            return True

    def send_message(self, msg, timeout=None):
        """
        Send a message to the IRC server.

        Args:
            msg: Message to send. Can be type 'str' or 'bytes'.
            timeout: Timeout for the message, or None for no timeout.

        Returns:
            True if the data was sent successfully, False otherwise.
        """
        if not self.sock:
            return False
        else:
            self.sock.settimeout(timeout)
            try:
                if type(msg) == str:
                    bytes_sent = self.sock.send(msg.encode())
                    return bytes_sent == len(msg.encode())
                elif type(msg) == bytes:
                    bytes_sent = self.sock.send(msg)
                    return bytes_sent == len(msg)
                else:
                    return False
            except socket.timeout:
                return False

    def set_parser(self, parser):
        """
        Set the parser for this IRC connection.
        """
        self.parser = parser

if __name__ == '__main__':
    """
    This is a simple example of an IRC connection that parses messages and
    prints debug messages to the log file. If the connection is lost, it
    tries to reconnect automatically. It shows proper initialization and
    exception handling for this class.
    """
    # Imports
    import logging
    import sys
    import config
    import twitchparser1
    try:
        c = config.config('./config.yaml')
    except RuntimeError:
        print('Invalid config file')
        sys.exit(0)
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
        irc_sock = Irc(c)
        irc_sock.set_parser(twitchparser1.TwitchParser1())
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
                        if msg[0] == 'SUBSCRIBER':
                            print('{0} has subscribed!'.format(msg[1]))
        except IrcError:
            pass
