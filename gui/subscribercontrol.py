#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import time
from gi.repository import Gtk, Pango


class SubscriberControl(Gtk.Box):
    def __init__(self, text_buffer):
        """
        This widget shows the buttons to control the subscriber widget.

        Args:
            text_buffer: Text buffer of the subscriber widget.
        """
        Gtk.Box.__init__(self, spacing=6)
        self.text_buffer = text_buffer
        self.tag_clear = self.text_buffer.create_tag(
            'clear', weight=Pango.Weight.ULTRALIGHT)
        # Init buttons
        self.button_clear = Gtk.Button(label='Clear')
        self.button_clear.connect('clicked', self.on_clear_clicked)
        # Init layout
        self.add(self.button_clear)
        self.set_hexpand(True)
        self.set_vexpand(False)
        return

    def on_clear_clicked(self, *args, **kwargs):
        """
        Function called when the 'Clear' button is clicked.
        Sets the text in the TextBuffer
        """
        iter1 = self.text_buffer.get_start_iter()
        iter2 = self.text_buffer.get_end_iter()
        self.text_buffer.apply_tag(self.tag_clear, iter1, iter2)
        return
