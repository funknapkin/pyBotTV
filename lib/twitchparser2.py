import re
from lib.ircparser import IrcParser


class TwitchParser2(IrcParser):
    def __init__(self):
        """
        This class implements a parser for IRC messages on the twitch server
        when connecting using the 'TWITCHCLIENT 2' message.
        TWITCHCLIENT 2 prevents you from seeing channel joins and parts.
        """
        super().__init__()
        self.connection_re = re.compile(
            r'\A:[a-zA-Z0-9\.]+ NOTICE \* :Login unsuccessful')
        self.join_re = re.compile(r'\A(?!x)x')  # Never match anything
        self.names_re = re.compile(
            r'\A:(?P<username>[a-zA-Z0-9_]+)\.tmi\.twitch\.tv 353 '
            r'(?P=username) = #(?P<channel>[a-zA-Z0-9_]+) :'
            r'(?P<usernames>[a-zA-Z0-9_ ]+)\Z')
        self.part_re = re.compile(r'\A(?!x)x')
        self.msg_re = re.compile(
            r'\A:(?!twitchnotify)(?P<username>[a-zA-Z0-9_]+)!(?P=username)@'
            r'(?P=username)\.tmi\.twitch\.tv PRIVMSG '
            r'#(?P<channel>[a-zA-Z0-9_]+) :(?P<message>.+?)\Z')
        self.mod_re = re.compile(
            r'\A:jtv MODE #(?P<channel>[a-zA-Z0-9_]+) \+o '
            r'(?P<username>[a-zA-Z0-9_]+)\Z')
        self.demod_re = re.compile(
            r'\A:jtv MODE #(?P<channel>[a-zA-Z0-9_]+) \-o '
            r'(?P<username>[a-zA-Z0-9_]+)\Z')
        self.subscribe_re = re.compile(
            r'\A:twitchnotify!twitchnotify@twitchnotify\.tmi\.twitch\.tv '
            r'PRIVMSG #(?P<channel>[a-zA-Z0-9_]+) :(?P<username>[a-zA-Z0-9_]+)'
            r' just subscribed!\Z')
        self.usercolor_re = re.compile(
            r'\A:jtv PRIVMSG [a-zA-Z0-9_]+ :USERCOLOR '
            r'(?P<username>[a-zA-Z0-9_]+) (?P<color>#[0-9A-F]{6}|'
            r'[a-zA-Z0-9_ ]+)\Z')
        self.emoteset_re = re.compile(
            r'\A:jtv PRIVMSG [a-zA-Z0-9_]+ :EMOTESET '
            r'(?P<username>[a-zA-Z0-9_]+) \[(?P<emoteset>[0-9,]+)\]\Z')
        self.specialuser_re = re.compile(
            r'\A:jtv PRIVMSG [a-zA-Z0-9_]+ :SPECIALUSER '
            r'(?P<username>[a-zA-Z0-9_]+) (?P<usertype>[a-zA-Z0-9_]+)\Z')
        self.timeout_re = re.compile(
            r'\A:jtv PRIVMSG [a-zA-Z0-9_]+ :CLEARCHAT '
            r'(?P<username>[a-zA-Z0-9_]+)\Z')
        self.clearchat_re = re.compile(
            r'\A:jtv PRIVMSG [a-zA-Z0-9_]+ :CLEARCHAT\Z')
        self.ping_re = re.compile(r'\APING.+')
        self.pong_message = 'PONG tmi.twitch.tv\r\n'
        return
