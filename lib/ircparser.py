import re


class IrcParser:
    def __init__(self):
        """
        This class is the parent class for an IRC chat parser.
        """
        self.connection_re = None
        self.join_re = None
        self.names_re = None
        self.part_re = None
        self.msg_re = None
        self.mod_re = None
        self.demod_re = None
        self.subscribe_re = None
        self.usercolor_re = None
        self.emoteset_re = None
        self.specialuser_re = None
        self.timeout_re = None
        self.clearchat_re = None
        self.ping_re = None
        self.pong_message = None
        return

    def check_connection_success(self, msg):
        """
        Parse a message to check if the connection failed.

        Args:
            msg: Message the server replied with after the connection.

        Returns:
            True if the connection was successful, false otherwise.
        """
        return (self.connection_re.match(msg) is None)

    def parse_message(self, msg):
        """
        Parse a message.

        Args:
            msg: Message to parse.

        Returns:
        A list with information on what the message contains. Possible formats
        are:
        - JOIN: ['JOIN', 'username 1', 'username 2', ...]
            One or more user(s) joined the channel. This also includes the
            'NAMES' message sent when joining the channel.
        - PART: ['PART', 'username 1', 'username 2', ...]
            One or more user(s) left the channel.
        - MSG: ['MSG', 'username', 'message']
            A user sent a message to the channel.
        - MOD: ['MOD', 'username']
            A user was given mod status on the channel.
        - SUBSCRIBER: ['SUBSCRIBER', 'username']
            A user subscribed to the channel.
        - USERCOLOR: ['USERCOLOR', 'username', 'color']
            Information on a user's color. Format for the color is either
            hexadecimal (#FFFFFF) or a word.
        - EMOTESET: ['EMOTESET', 'username', emoteset1, emoteset2, ...]
            A list of emoteset a user has access to.
        - SPECIALUSER: ['SPECIALUSER', 'username', 'type']
            Information on a user's special status.
        - TIMEOUT: ['TIMEOUT', 'username']
            A user has been banned or timed out.
        - CLEARCHAT: ['CLEARCHAT']
            A moderator has cleared the chat.
        - PING: ['PING']
            The server sent a PING.
        """
        match = self.join_re.match(msg)
        if match:
            username = match.group('username')
            return ['JOIN', username]
        match = self.names_re.match(msg)
        if match:
            usernames = match.group('usernames')
            return ['JOIN'] + usernames.split(' ')
        match = self.part_re.match(msg)
        if match:
            username = match.group('username')
            return ['PART', username]
        match = self.msg_re.match(msg)
        if match:
            username, message = match.group('username', 'message')
            return ['MSG', username, message]
        match = self.mod_re.match(msg)
        if match:
            username = match.group('username')
            return ['MOD', username]
        match = self.demod_re.match(msg)
        if match:
            username = match.group('username')
            return ['DEMOD', username]
        match = self.subscribe_re.match(msg)
        if match:
            username = match.group('username')
            return ['SUBSCRIBER', username]
        match = self.usercolor_re.match(msg)
        if match:
            username, color = match.group('username', 'color')
            return ['USERCOLOR', username, color]
        match = self.emoteset_re.match(msg)
        if match:
            username, emoteset = match.group('username', 'emoteset')
            return ['EMOTESET', username] + list(map(int, emoteset.split(',')))
        match = self.specialuser_re.match(msg)
        if match:
            username, usertype = match.group('username', 'usertype')
            return ['SPECIALUSER', username, usertype]
        match = self.timeout_re.match(msg)
        if match:
            username = match.group('username')
            return ['TIMEOUT', username]
        match = self.clearchat_re.match(msg)
        if match:
            return ['CLEARCHAT']
        match = self.ping_re.match(msg)
        if match:
            return ['PING']
        return None
