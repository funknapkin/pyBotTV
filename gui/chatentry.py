#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk, Pango, GdkPixbuf


class ChatEntry(Gtk.Entry):
    def __init__(self, config, out_queue, *args, **kwargs):
        """
        This widget is an input box that allows the user to send chat messages
        to the IRC channel.
        """
        Gtk.Entry.__init__(self, *args, **kwargs)
        self.config = config
        self.out_queue = out_queue
        self.set_hexpand(True)
        self.set_vexpand(False)
        self.set_max_length(500)
        self.connect('activate', self.on_activate)

    def on_activate(self, *args, **kwargs):
        """
        Function called by GTK when the user presses the Enter key.
        Sends the chat message and clears the entry box.
        """
        text_buffer = self.get_buffer()
        self.out_queue.put(text_buffer.get_text())
        text_buffer.delete_text(0, -1)
