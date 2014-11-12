#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import logging
from gi.repository import Gtk, Pango


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
        self.add(self.text_view)
        # Bind events and init misc stuff
        self.msg_count = 0
        self.text_view.connect('size-allocate', self.scroll_bottom)
        self.default_tag = self.text_view.get_buffer().create_tag(
            "default", weight=Pango.Weight.BOLD, foreground='#000000')
        self.color_username = ''
        self.color_tag = self.default_tag
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

    def notify(self, event, data):
        """
        Notify this widget of an event.

        Args:
            event: Type of the event
            data: Additionnal data for this event
        """
        if event == 'MSG':
            text_buffer = self.text_view.get_buffer()
            if self.msg_count != 0:
                text_buffer.insert(text_buffer.get_end_iter(), '\r\n')
            mark = text_buffer.create_mark(
                None, text_buffer.get_end_iter(), True)
            text_buffer.insert(text_buffer.get_end_iter(),
                               '{0}:  {1}'.format(data[0], data[1]))
            tag_iter_1 = text_buffer.get_iter_at_mark(mark)
            tag_iter_2 = text_buffer.get_iter_at_mark(mark)
            tag_iter_2.forward_chars(len(data[0]))
            if data[0] == self.color_username:
                text_tag = self.color_tag
            else:
                text_tag = self.default_tag
            text_buffer.apply_tag(text_tag, tag_iter_1, tag_iter_2)
            text_buffer.delete_mark(mark)
            self.msg_count += 1
            if self.msg_count > self.config['gui']['chat_maxmessages']:
                iter_1 = text_buffer.get_start_iter()
                iter_2 = text_buffer.get_iter_at_line(1)
                text_buffer.delete(iter_1, iter_2)
                self.msg_count -= 1
        elif event == 'USERCOLOR':
            self.color_username = data[0]
            if data[1][0] == '#':
                color = data[1]
            else:
                try:
                    color = self.default_colors[data[1]]
                except:
                    logging.warning('Chat: Invalid color: {0}'.format(data[1]))
                    color = '#000000'
            self.color_tag = self.text_view.get_buffer().create_tag(
                None, weight=Pango.Weight.BOLD, foreground=color)
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
