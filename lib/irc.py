import logging
import re
import socket


class ircException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class irc:
    def __init__(self, config):
        """Build an irc object to interact with a single IRC chat room.

        This class contains multiple utilities to handle an IRC chat room, such
        as connecting to a predefined chat room specified in the config file,
        receiving messages and parsing messages.

        Args:
            config: config object. See config.py and config.yaml.
        """
        self.config = config

    def connect(self):
        """
        Args:
        Returns:
        Raises:
        """
        # Connect to server
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.config['server'], self.config['port']))
            logging.info(
                'IRC: connected to the server {0}:{1}'.format(
                    self.config['server'], self.config['port']))
        except Exception as e:
            raise ircException('Cannot connect to the server')
        # Login to the IRC chat room
        sock.settimeout(5)
        send_data = 'USER {0}\r\n'.format(self.config['user']).encode()
        if sock.send(send_data) != len(send_data):
            raise ircException('Failed to send login data to the server')
        send_data = 'PASS {0}\r\n'.format(self.config['password']).encode()
        if sock.send(send_data) != len(send_data):
            raise ircException('Failed to send login data to the server')
        send_data = 'NICK {0}\r\n'.format(self.config['user']).encode()
        if sock.send(send_data) != len(send_data):
            raise ircException('Failed to send login data to the server')
        response = sock.recv(self.config['buffer_size']).decode().rstrip()
        if re.match(r'^:[a-zA-Z0-9\.]+ NOTICE \* :Login unsuccessful',
                    response) is None:
            logging.info('IRC: successfully logged in with username {0}'
                         .format(self.config['user']))
        else:
            raise ircException('Login failed with message {0}'
                               .format(response))
        # Join channel
        channel = self.config['channel'] if self.config['channel'][0] == '#' \
            else '#{0}'.format(self.config['channel'])
        sock.send('JOIN {0}\r\n'.format(channel).encode())
        logging.info('IRC: joined channel {0}'.format(self.config['channel']))
        # Change self variable and return
        self.sock = sock
        return

    def parseMessage(self):
        """
        Parse a message, doing any IRC-related work and returns a list with
        parsed data related to the event. Ex: ['subscription', 'funknapkin']
        """
        logging.debug('IRC chat: {0}'.format(self.message))
        return

    def receiveMessage(self):
        """Wait for a message on the IRC channel.

        Returns:
            true if a message was received, false otherwise
            (i.e.: connection lost)
        """
        if not self.sock:
            return false
        self.sock.settimeout(None)
        self.message = self.sock.recv(
            self.config['buffer_size']).decode().rstrip()
        if len(self.message) == 0:
            return False
        else:
            return True
