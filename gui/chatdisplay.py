#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import json
import logging
import os
import os.path
import random
import re
import urllib.request
import urllib.error
from collections import OrderedDict
from gi.repository import Gtk, Pango, GdkPixbuf


class ChatDisplay(Gtk.ScrolledWindow):
    def __init__(self, config):
        """
        This widget shows the chat messages in a text box.

        Args:
            config: A dictionnary with configuration options.
        """
        # Init ScrolledWindow
        Gtk.ScrolledWindow.__init__(self)
        self.config = config
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        # Init TextView
        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_justification(Gtk.Justification.LEFT)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_view.set_pixels_inside_wrap(
            self.config['gui']['chat_linespacing'])
        self.text_view.set_pixels_above_lines(
            self.config['gui']['chat_linespacing'])
        self.text_view.set_pixels_below_lines(
            self.config['gui']['chat_linespacing'])
        self.add(self.text_view)
        # Bind events and init misc stuff
        self.msg_count = 0
        self.text_view.connect('size-allocate', self.scroll_bottom)
        self.default_tag = self.text_view.get_buffer().create_tag(
            "default", weight=Pango.Weight.BOLD, foreground='#000000')
        self.display_names = OrderedDict()
        self.usercolors = OrderedDict()
        self.emotesets = OrderedDict()
        self.emotes = OrderedDict()
        self.specialusers = OrderedDict()
        self.moderators = set()
        # Init twitch default colors
        self.default_colors = {
            'Red': '#FF0000',
            'Blue': '#0000FF',
            'Green': '#00FF00',
            'FireBrick': '#B22222',
            'Coral': '#FF7F50',
            'YellowGreen': '#9ACD32',
            'OrangeRed': '#FF4500',
            'SeaGreen': '#2E8B57',
            'GoldenRod': '#DAA520',
            'Chocolate': '#D2691E',
            'CadetBlue': '#5F9EA0',
            'DodgerBlue': '#1E90FF',
            'HotPink': '#FF69B4',
            'BlueViolet': '#8A2BE2',
            'SpringGreen': '#00FF7F'}
        # Download emotes and badges data
        self._init_emotes_data()
        self._init_badges_data()

    def notify(self, event, data):
        """
        Notify this widget of an event.

        Args:
            event: Type of the event
            data: Additionnal data for this event
        """
        if event == 'MSG':
            # Add chat message to buffer
            text_buffer = self.text_view.get_buffer()
            if self.msg_count != 0:
                text_buffer.insert(text_buffer.get_end_iter(), '\r\n')
            mark_begin = text_buffer.create_mark(
                None, text_buffer.get_end_iter(), True)
            text_buffer.insert(text_buffer.get_end_iter(),
                               '{0}:  {1}'.format(data[0], data[1]))
            text_iter = text_buffer.get_iter_at_mark(mark_begin)
            text_iter.forward_chars(len(data[0])+2)
            mark_message = text_buffer.create_mark(
                None, text_iter, True)
            # Get display name
            try:
                display_name = self.display_names[data[0]]
            except KeyError:
                display_name = data[0][0].upper() + data[0][1:]
            mark = text_buffer.create_mark(
                None, text_buffer.get_iter_at_mark(mark_begin), False)
            self.change_display_name(mark, data[0], new_name=display_name)
            # Add turbo and subscriber icons
            if not self.badges_initialized:
                self._init_badges_data()
            statuses = self.specialusers[data[0]].copy() if data[0] in \
                self.specialusers else set()
            if data[0] == self.config['irc']['channel'][1:]:
                statuses.add('broadcaster')
            elif data[0] in self.moderators:
                statuses.add('mod')
            if self.badges_initialized:
                mark = text_buffer.create_mark(
                    None, text_buffer.get_iter_at_mark(mark_begin), True)
                self.add_user_icons(mark, statuses)
            # Add emotes to chat
            to_replace = []  # List of tuples with format (index, name, path)
            if not self.emotes_initialized:
                self._init_emotes_data()
            if self.emotes_initialized:
                for globalemote in self.emotes_global.keys():
                    for match in re.finditer(globalemote, data[1]):
                        to_replace.append(tuple([
                            match.start(),
                            globalemote,
                            None]))
            if self.emotes_initialized and data[0] in self.emotesets:
                for emoteset in self.emotesets[data[0]]:
                    if str(emoteset) not in self.emotes_sets:
                        continue
                    emoteset_name = self.emotes_sets[str(emoteset)]
                    if emoteset_name not in self.emotes_subscriber.keys():
                        continue
                    for emote in self.\
                            emotes_subscriber[emoteset_name]['emotes'].keys():
                        for match in re.finditer(emote, data[1]):
                            to_replace.append(tuple([
                                match.start(),
                                emote,
                                emoteset_name]))
            to_replace.sort(key=lambda x: x[0], reverse=True)
            for (index, emote, emoteset) in to_replace:
                image_exists = \
                    (emoteset is None
                     and self._download_global_emote(emote)) or \
                    (emoteset is not None and
                     self._download_subscriber_emote(emoteset, emote))
                if not image_exists:
                    continue
                text_iter_begin = text_buffer.get_iter_at_mark(mark_message)
                text_iter_begin.forward_chars(index+1)
                mark = text_buffer.create_mark(
                    None, text_iter_begin, True)
                self.add_emote(mark, emote, emoteset)
            # Cleanup mark and old messages
            text_buffer.delete_mark(mark_begin)
            text_buffer.delete_mark(mark_message)
            self.msg_count += 1
            if self.msg_count > self.config['gui']['chat_maxmessages']:
                iter_1 = text_buffer.get_start_iter()
                iter_2 = text_buffer.get_iter_at_line(1)
                text_buffer.delete(iter_1, iter_2)
                self.msg_count -= 1
        elif event == 'USERCOLOR':
            self._set_usercolor(data[0], data[1])
        elif event == 'EMOTESET':
            if data[0] in self.emotesets:
                self.emotesets.move_to_end(data[0])
            self.emotesets[data[0]] = data[1:]
            cache_size = self.config['gui']['chat_cache_size']
            if len(self.emotesets) > cache_size:
                self.emotesets.popitem(last=False)
        elif event == 'SPECIALUSER':
            if data[0] in self.specialusers:
                self.specialusers[data[0]].add(data[1])
                self.specialusers.move_to_end(data[0])
            else:
                self.specialusers[data[0]] = set([data[1]])
                cache_size = self.config['gui']['chat_cache_size']
                if len(self.specialusers) > cache_size:
                    self.specialusers.popitem(last=False)

        elif event == 'MOD':
            self.moderators.add(data[0])
        elif event == 'DEMOD':
            self.moderators.discard(data[0])
        return

    def add_user_icons(self, mark, statuses):
        """
        Add icons to indicate a user's statuses.

        Args:
            mark: Mark at the beginning of the username.
            statuses: Set containing the user's statuses.
        """
        text_buffer = self.text_view.get_buffer()
        for specialstatus in reversed(self.status_order):
            if specialstatus in statuses:
                image_path = os.path.join(
                    self.config['gui']['badges_path'],
                    self.config['irc']['channel'][1:],
                    '{0}.png'.format(specialstatus))
                text_iter = text_buffer.get_iter_at_mark(mark)
                pixbuf = self.badges[specialstatus]
                text_buffer.insert_pixbuf(text_iter, pixbuf)
        text_buffer.delete_mark(mark)

    def add_emote(self, mark, name, emoteset):
        """
        Add an emote to the text view.

        Args:
            mark: Mark at the emote's position.
            name: Name of the emote.
            emoteset: Emoteset of the emote, or None for global emotes.
        """
        text_buffer = self.text_view.get_buffer()
        if (name, emoteset) in self.emotes:
            pixbuf = self.emotes[(name, emoteset)]
            self.emotes.move_to_end((name, emoteset))
        else:
            if emoteset is None:
                image_path = os.path.join(
                    self.config['gui']['emote_globals_path'],
                    '{0}.png'.format(name))
            else:
                image_path = os.path.join(
                    self.config['gui']['emote_subscriber_path'],
                    emoteset_name,
                    '{0}.png'.format(name))
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
            self.emotes[(name, emoteset)] = pixbuf
            cache_size = self.config['gui']['chat_cache_size']
            if len(self.emotes) > cache_size:
                self.emotes.popitem(last=False)
        text_iter_begin = text_buffer.get_iter_at_mark(mark)
        text_iter_end = text_buffer.get_iter_at_mark(mark)
        text_iter_end.forward_chars(len(name))
        text_buffer.delete(text_iter_begin, text_iter_end)
        text_buffer.insert_pixbuf(text_iter_begin, pixbuf)
        text_buffer.delete_mark(mark)

    def change_display_name(self, mark, username, new_name=None):
        """
        Function to change a user's display name. Also applies usercolor.

        Args:
            mark: Mark at the beginning of the username.
            username: Name of the user.
            new_name: New name to set for the user. Optional.
        """
        text_buffer = self.text_view.get_buffer()
        # Set display name
        if new_name is not None:
            if username in self.display_names:
                self.display_names.move_to_end(username)
            else:
                self.display_names[username] = new_name
            text_iter_begin = text_buffer.get_iter_at_mark(mark)
            found = text_iter_begin.forward_search(
                ':', Gtk.TextSearchFlags.TEXT_ONLY, None)
            if found:
                text_iter_end = found[0]
                text_buffer.delete(text_iter_begin, text_iter_end)
                text_buffer.insert(text_iter_begin, new_name)
                text_iter_begin.backward_chars(len(new_name))
                text_buffer.move_mark(mark, text_iter_begin)
        # Set color
        if username not in self.usercolors:
            self._set_usercolor(username, None)
        text_tag = self.usercolors[username]
        text_iter_begin = text_buffer.get_iter_at_mark(mark)
        found = text_iter_begin.forward_search(
            ':', Gtk.TextSearchFlags.TEXT_ONLY, None)
        if found:
            text_iter_end = found[0]
            text_buffer.apply_tag(
                text_tag, text_iter_begin, text_iter_end)
        text_buffer.delete_mark(mark)

    def scroll_bottom(self, event, data=None):
        """
        Scroll to the bottom of the window.

        Args:
            event: Event that called this function
            data: Additionnal data for this event
        """
        adj = self.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        self.text_view.queue_draw()
        return

    def _download_global_emote(self, name):
        """
        Download a single global emote to a PNG file. If the file already
        exists, download is skipped.

        Args:
            name: A string that describes the emote's name.

        Returns:
            True if the file exists after this function was called,
            False otherwise.
        """
        os.makedirs(self.config['gui']['emote_globals_path'], exist_ok=True)
        if os.access(os.path.join(self.config['gui']['emote_globals_path'],
                     '{0}.png'.format(name)), os.F_OK):
            return True
        else:
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
            return True

    def _download_subscriber_emote(self, emoteset, emotename):
        """
        Download a single subscriber emote to a PNG file. If the file already
        exists, download is skipped.

        Args:
            emoteset: Name of the emoteset (i.e. channel name).
            emotename: A string that describes the emote's name.

        Returns:
            True if the file exists after this function was called,
            False otherwise.
        """
        emote_dir = os.path.join(self.config['gui']['emote_subscriber_path'],
                                 emoteset)
        emote_path = os.path.join(emote_dir, '{0}.png'.format(emotename))
        os.makedirs(emote_dir, exist_ok=True)
        if os.access(emote_path, os.F_OK):
            return True
        else:
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
            return True

    def _init_badges_data(self):
        """
        Download badges data and icons.
        """
        self.badges_initialized = False
        self.badges = {}
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
            logging.warning('Chat: failed to get badges data')
            return
        # Download badges
        to_download = ['admin', 'broadcaster', 'mod', 'staff', 'subscriber',
                       'turbo']
        self.status_order = []
        badges_dir = os.path.join(self.config['gui']['badges_path'],
                                  self.config['irc']['channel'][1:])
        os.makedirs(badges_dir, exist_ok=True)
        for badge_name in to_download:
            try:
                badge_path = os.path.join(
                    badges_dir, '{0}.png'.format(badge_name))
                if os.access(badge_path, os.F_OK):
                    self.status_order.append(badge_name)
                    continue  # File already exists
                badge_url = j[badge_name]['image']
                badge = urllib.request.urlopen(badge_url)
                badge_file = open(badge_path, 'wb')
                badge_file.write(badge.read())
                badge_file.close()
                self.status_order.append(badge_name)
            except:
                logging.warning(
                    'Chat: Failed to download badge {0}'.format(badge_name))
        # Load badges bitmaps
        for specialstatus in reversed(self.status_order):
            image_path = os.path.join(
                self.config['gui']['badges_path'],
                self.config['irc']['channel'][1:],
                '{0}.png'.format(specialstatus))
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
            self.badges[specialstatus] = pixbuf
        self.badges_initialized = True

    def _init_emotes_data(self):
        """
        Download emotes data.
        """
        try:
            u = urllib.request.urlopen('http://twitchemotes.com/global.json')
            s = u.read().decode()
            self.emotes_global = json.loads(s)
            u = urllib.request.urlopen(
                'http://twitchemotes.com/subscriber.json')
            s = u.read().decode()
            self.emotes_subscriber = json.loads(s)
            u = urllib.request.urlopen('http://twitchemotes.com/sets.json')
            s = u.read().decode()
            self.emotes_sets = json.loads(s)
            self.emotes_initialized = True
        except urllib.error.URLError:
            logging.warning('Chat: failed to download emotes data')
            self.emotes_global = {}
            self.emotes_subscriber = {}
            self.emotes_sets = {}
            self.emotes_initialized = False

    def _set_usercolor(self, user, color=None):
        """
        Set a user's usercolor.

        Args:
            user: username
            color: Color to set, or None to choose a default colot
        """
        if color is None:
            color = random.choice(list(self.default_colors.values()))
        if color[0] != '#':
            try:
                color = self.default_colors[color]
            except:
                logging.warning('Chat: Invalid color: {0}'.format(data[1]))
                color = '#000000'
        if user in self.usercolors:
            self.usercolors.move_to_end(user)
        self.usercolors[user] = self.text_view.get_buffer().create_tag(
            None, weight=Pango.Weight.BOLD, foreground=color)
        cache_size = self.config['gui']['chat_cache_size']
        if len(self.usercolors) > cache_size:
            self.usercolors.popitem(last=False)
