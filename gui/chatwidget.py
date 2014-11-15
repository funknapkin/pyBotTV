#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import json
import logging
import os
import os.path
import re
import urllib.request
import urllib.error
from gi.repository import Gtk, Pango, GdkPixbuf


class ChatWidget(Gtk.ScrolledWindow):
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
        self.display_names = {}
        self.usercolors = {}
        self.emotesets = {}
        self.specialusers = {}
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
            # Get display name
            try:
                display_name = self.display_names[data[0]]
            except KeyError:
                try:
                    request = urllib.request.Request(
                        'https://api.twitch.tv/kraken/users/{0}'
                        .format(data[0]),
                        headers={'Accept': 'application/vnd.twitchtv.v3+json'})
                    u = urllib.request.urlopen(request)
                    s = u.read().decode()
                    j = json.loads(s)
                    display_name = j['display_name']
                    self.display_names[data[0]] = display_name
                except urllib.error.URLError:
                    display_name = data[0]
            # Add chat message to buffer
            text_buffer = self.text_view.get_buffer()
            if self.msg_count != 0:
                text_buffer.insert(text_buffer.get_end_iter(), '\r\n')
            mark_begin = text_buffer.create_mark(
                None, text_buffer.get_end_iter(), True)
            text_buffer.insert(text_buffer.get_end_iter(),
                               '{0}:  {1}'.format(display_name, data[1]))
            text_iter = text_buffer.get_iter_at_mark(mark_begin)
            text_iter.forward_chars(len(display_name)+2)
            mark_message = text_buffer.create_mark(
                None, text_iter, True)
            # Apply color to username
            tag_iter_1 = text_buffer.get_iter_at_mark(mark_begin)
            tag_iter_2 = text_buffer.get_iter_at_mark(mark_begin)
            tag_iter_2.forward_chars(len(display_name))
            if data[0] in self.usercolors:
                text_tag = self.usercolors[data[0]]
            else:
                text_tag = self.default_tag
            text_buffer.apply_tag(text_tag, tag_iter_1, tag_iter_2)
            # Add turbo and subscriber icons
            if not self.badges_initialized:
                self._init_badges_data()
            if self.badges_initialized:
                status_order = ['admin', 'broadcaster', 'mod', 'staff',
                                'subscriber', 'turbo']
                statuses = self.specialusers[data[0]].copy() if data[0] in \
                    self.specialusers else set()
                if data[0] == self.config['irc']['channel'][1:]:
                    statuses.add('broadcaster')
                elif data[0] in self.moderators:
                    statuses.add('mod')
                for specialstatus in reversed(status_order):
                    if specialstatus in statuses:
                        image_path = os.path.join(
                            self.config['gui']['badges_path'],
                            self.config['irc']['channel'][1:],
                            '{0}.png'.format(specialstatus))
                        text_iter = text_buffer.get_iter_at_mark(mark_begin)
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
                        text_buffer.insert_pixbuf(text_iter, pixbuf)
            # Add emotes to chat
            to_replace = []  # List of tuples with format (index, name, path)
            if not self.emotes_initialized:
                self._init_emotes_data()
            if self.emotes_initialized:
                for globalemote in self.emotes_global.keys():
                    for match in re.finditer(globalemote, data[1]):
                        if self._download_global_emote(globalemote):
                            to_replace.append(tuple([
                                match.start(),
                                globalemote,
                                os.path.join(
                                    self.config['gui']['emote_globals_path'],
                                    '{0}.png'.format(globalemote))]))
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
                            if self._download_subscriber_emote(
                                    emoteset_name, emote):
                                to_replace.append(tuple([
                                    match.start(),
                                    emote,
                                    os.path.join(
                                        self.config['gui']
                                        ['emote_subscriber_path'],
                                        emoteset_name,
                                        '{0}.png'.format(emote))]))
            to_replace.sort(key=lambda x: x[0], reverse=True)
            for (index, emote, imagepath) in to_replace:
                text_iter_begin = text_buffer.get_iter_at_mark(mark_message)
                text_iter_begin.forward_chars(index+1)
                text_iter_end = text_buffer.get_iter_at_mark(mark_message)
                text_iter_end.forward_chars(index+len(emote)+1)
                text_buffer.delete(text_iter_begin, text_iter_end)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(imagepath)
                text_buffer.insert_pixbuf(text_iter_begin, pixbuf)
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
            if data[1][0] == '#':
                color = data[1]
            else:
                try:
                    color = self.default_colors[data[1]]
                except:
                    logging.warning('Chat: Invalid color: {0}'.format(data[1]))
                    color = '#000000'
            self.usercolors[data[0]] = self.text_view.get_buffer().create_tag(
                None, weight=Pango.Weight.BOLD, foreground=color)
        elif event == 'EMOTESET':
            self.emotesets[data[0]] = data[1:]
        elif event == 'SPECIALUSER':
            if data[0] in self.specialusers:
                self.specialusers[data[0]].add(data[1])
            else:
                self.specialusers[data[0]] = set([data[1]])
        elif event == 'MOD':
            self.moderators.add(data[0])
        elif event == 'DEMOD':
            self.moderators.discart(data[0])
        return

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
            self.badges_initialized = False
            return
        to_download = ['admin', 'broadcaster', 'mod', 'staff', 'turbo',
                       'subscriber']
        try:
            badges_dir = os.path.join(self.config['gui']['badges_path'],
                                      self.config['irc']['channel'][1:])
            os.makedirs(badges_dir, exist_ok=True)
            for badge_name in to_download:
                badge_path = os.path.join(
                    badges_dir, '{0}.png'.format(badge_name))
                if os.access(badge_path, os.F_OK):
                    continue  # File already exists
                badge_url = j[badge_name]['image']
                badge = urllib.request.urlopen(badge_url)
                badge_file = open(badge_path, 'wb')
                badge_file.write(badge.read())
                badge_file.close()
            self.badges_initialized = True
        except:
            logging.warning('Chat: failed to download badges')
            self.badges_initialized = False
            return

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
