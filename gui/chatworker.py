#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import json
import logging
import os
import os.path
import urllib.request
import urllib.error
from collections import OrderedDict
from gi.repository import GLib


class ChatWorker():
    def __init__(self, config, queue):
        """
        This class is a worker thread that completes tasks for ChatDisplay.

        Args:
            config: A dictionnary with configuration options.
            queue: A queue to receive commands.
        """
        self.config = config
        self.queue = queue
        self.badges_initialized = False
        self.emotes_initialized = False
        self.display_names = OrderedDict()

    def run(self):
        """
        Wait for a message from ChatDisplay, and process it. Supported format
        for messages is:
            ['INIT_BADGES', callback_function]
            Init badges data.
            ['INIT_EMOTES', callback_function]
            Init emotes data.
            ['DISPLAY_NAME', callback_function, mark, username]
            Get the display name for a user.
            ['BADGE', callback_function, mark, statuses]
            Call after initializing badges data to add badges to text.
            ['EMOTE', callback_function, mark, emote, emoteset]
            Download an emote.
        """
        while(True):
            msg = self.queue.get()
            if msg[0] == 'INIT_BADGES':
                self.get_badge_data(msg[1])
            elif msg[0] == 'INIT_EMOTES':
                self.get_emotes_data(msg[1])
            elif msg[0] == 'DISPLAY_NAME':
                self.get_display_name(msg[1], msg[2], msg[3])
            elif msg[0] == 'BADGE':
                self.on_badge(msg[1], msg[2], msg[3])
            elif msg[0] == 'EMOTE':
                self.on_emote(msg[1], msg[2], msg[3], msg[4])

    def get_badge_data(self, callback_func):
        if not self.badges_initialized:
            # Get badges data
            try:
                request = urllib.request.Request(
                    'https://api.twitch.tv/kraken/chat/{0}/badges'
                    .format(self.config['irc']['channel'][1:]),
                    headers={'Accept': 'application/vnd.twitchtv.v3+json'})
                u = urllib.request.urlopen(request)
                s = u.read().decode()
                j = json.loads(s)
            except:
                logging.warning('ChatWorker: failed to get badges data')
                return
            # Download badges
            to_download = ['admin', 'broadcaster', 'mod', 'staff',
                           'subscriber', 'turbo']
            self.badges_order = []
            badges_dir = os.path.join(self.config['gui']['badges_path'],
                                      self.config['irc']['channel'][1:])
            os.makedirs(badges_dir, exist_ok=True)
            for badge_name in to_download:
                try:
                    badge_path = os.path.join(
                        badges_dir, '{0}.png'.format(badge_name))
                    if os.access(badge_path, os.F_OK):
                        self.badges_order.append(badge_name)
                        continue  # File already exists
                    badge_url = j[badge_name]['image']
                    badge = urllib.request.urlopen(badge_url)
                    badge_file = open(badge_path, 'wb')
                    badge_file.write(badge.read())
                    badge_file.close()
                    self.badges_order.append(badge_name)
                except:
                    logging.warning('Chat: Failed to download badge {0}'
                                    .format(badge_name))
            self.badges_initialized = True
        # Call callback function
        GLib.idle_add(callback_func, self.badges_order)
        return

    def get_emotes_data(self, callback_function):
        try:
            u = urllib.request.urlopen('http://twitchemotes.com/global.json')
            s = u.read().decode()
            emotes_global = json.loads(s)
            u = urllib.request.urlopen(
                'http://twitchemotes.com/subscriber.json')
            s = u.read().decode()
            emotes_subscriber = json.loads(s)
            u = urllib.request.urlopen('http://twitchemotes.com/sets.json')
            s = u.read().decode()
            emotes_sets = json.loads(s)
            self.emotes_initialized = True
            self.emotes_global = emotes_global
            self.emotes_subscriber = emotes_subscriber
            self.emotes_sets = emotes_sets
            GLib.idle_add(callback_function, emotes_global,
                          emotes_subscriber, emotes_sets)
        except urllib.error.URLError:
            logging.warning('ChatWorker: failed to download emotes data')
        return

    def get_display_name(self, callback_function, mark, username):
        if username in self.display_names:
            display_name = self.display_names[username]
            self.display_names.move_to_end(username)
        else:
            try:
                request = urllib.request.Request(
                    'https://api.twitch.tv/kraken/users/{0}'
                    .format(username),
                    headers={'Accept': 'application/vnd.twitchtv.v3+json'})
                u = urllib.request.urlopen(request)
                s = u.read().decode()
                j = json.loads(s)
                display_name = j['display_name']
                self.display_names[username] = display_name
                cache_size = self.config['gui']['chat_cache_size']
                if len(self.display_names) > cache_size:
                    self.display_names.popitem(last=False)
            except urllib.error.URLError:
                logging.warning(
                    'ChatWorker: Failed to get display name for user {0}'
                    .format(username))
                display_name = username[0].upper() + username[1:]
        GLib.idle_add(callback_function, mark, username, display_name)

    def on_badge(self, callback_func, mark, statuses):
        if self.badges_initialized:
            GLib.idle_add(callback_func, mark, statuses)

    def on_emote(self, callback_func, mark, emote, emoteset):
        if not self.emotes_initialized:
            return
        if emoteset is None:
            emote_dir = self.config['gui']['emote_globals_path']
        else:
            emote_dir = os.path.join(
                self.config['gui']['emote_subscriber_path'], emoteset)
        emote_path = os.path.join(emote_dir, '{0}.png'.format(emote))
        os.makedirs(emote_dir, exist_ok=True)
        if not os.access(emote_path, os.F_OK):
            if emoteset is None and not self._download_global_emote(emote):
                logging.warning('ChatWorker: Failed to download emote {0},{1}'
                                .format(emote, emoteset))
                return
            elif emoteset is not None and \
                    not self._download_subscriber_emote(emoteset, emote):
                logging.warning('ChatWorker: Failed to download emote {0},{1}'
                                .format(emote, emoteset))
                return
        GLib.idle_add(callback_func, mark, emote, emoteset)

    def _download_global_emote(self, name):
        """
        Download a single global emote to a PNG file.

        Args:
            name: A string that describes the emote's name.

        Returns:
            True if the file exists after this function was called,
            False otherwise.
        """
        os.makedirs(self.config['gui']['emote_globals_path'], exist_ok=True)
        try:
            emote_url = 'http:' + self.emotes_global[name]['url']
            emote = urllib.request.urlopen(emote_url)
            emote_file = open(
                os.path.join(self.config['gui']['emote_globals_path'],
                             '{0}.png'.format(name)),
                'wb')
            emote_file.write(emote.read())
            emote_file.close()
        except urllib.error.URLError:
            return False
        except OSError:
            return False
        except KeyError:
            return False
        return True

    def _download_subscriber_emote(self, emoteset, emotename):
        """
        Download a single subscriber emote to a PNG file.

        Args:
            emoteset: Name of the emoteset (i.e. channel name).
            emotename: A string that describes the emote's name.

        Returns:
            True if the file exists after this function was called,
            False otherwise.
        """
        emote_dir = os.path.join(
            self.config['gui']['emote_subscriber_path'], emoteset)
        emote_path = os.path.join(emote_dir, '{0}.png'.format(emotename))
        try:
            emote_url = 'http:' + \
                self.emotes_subscriber[emoteset]['emotes'][emotename]
            emote = urllib.request.urlopen(emote_url)
            emote_file = open(emote_path, 'wb')
            emote_file.write(emote.read())
            emote_file.close()
        except urllib.error.URLError:
            return False
        except OSError:
            return False
        except KeyError:
            return False
        return True
