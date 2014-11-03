import re
import ircparser


class TwitchParser3(ircparser.IrcParser):
    def __init__(self):
        """
        This class implements a parser for IRC messages on the twitch server
        when connecting using the 'TWITCHCLIENT 3' message.
        TWITCHCLIENT 3 exists without documentation. Some information can be
        found on the wiki: http://twitch-tv.wikia.com/wiki/Developer_info
        """
        super().__init__()
        self.connection_re = re.compile(
            r'\A:[a-zA-Z0-9\.]+ NOTICE \* :Login unsuccessful')
        self.join_re = re.compile(
            r'\A:(?P<username>[a-zA-Z0-9_]+)!(?P=username)@(?P=username)'
            r'\.tmi\.twitch\.tv JOIN #(?P<channel>[a-zA-Z0-9_]+)\Z')
        self.names_re = re.compile(
            r'\A:(?P<username>[a-zA-Z0-9_]+)\.tmi\.twitch\.tv 353 '
            r'(?P=username) = #(?P<channel>[a-zA-Z0-9_]+) :'
            r'(?P<usernames>[a-zA-Z0-9_ ]+)\Z')
        self.part_re = re.compile(r'\A(?!x)x')  # Never match anything
        self.msg_re = re.compile(
            r'\A:(?P<username>[a-zA-Z0-9_]+)!(?P=username)@(?P=username)'
            r'\.tmi\.twitch\.tv PRIVMSG #(?P<channel>[a-zA-Z0-9_]+) :'
            r'(?P<message>.+?)\Z')
        self.mod_re = re.compile(
            r'\A:jtv MODE #(?P<channel>[a-zA-Z0-9_]+) \+o '
            r'(?P<username>[a-zA-Z0-9_]+)\Z')
        self.subscribe_re = re.compile(
            r'\A:jtv!jtv@jtv\.tmi\.twitch\.tv PRIVMSG '
            r'#(?P<channel>[a-zA-Z0-9_]+) :SPECIALUSER '
            r'(?P<username>[a-zA-Z0-9_]+) subscriber\Z')
        self.ping_re = re.compile(r'\APING.+')
        self.pong_message = 'PONG tmi.twitch.tv\r\n'
        return
