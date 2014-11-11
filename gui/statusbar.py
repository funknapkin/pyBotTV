#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk


class StatusBar(Gtk.Statusbar):
    def __init__(self, config):
        """
        This widget creates a status bar meant to be displayed at the bottom of
        the screen. It shows the state of the IRC connection.

        Args:
            config: A dictionnary with configuration options.
        """
        Gtk.Statusbar.__init__(self)
        self.config = config
        self.set_halign(Gtk.Align.END)
        self.context_id = self.get_context_id('info')
        self.first_connection = True

    def notify(self, event, data):
        """
        Notify this widget of an event.

        Args:
            event: Type of the event
            data: Additionnal data for this event
        """
        self.pop(self.context_id)
        if event == 'CONNECTING':
            if self.first_connection:
                self.push(self.context_id, 'Connecting.')
            else:
                self.push(self.context_id, 'Connection lost. Reconnecting.')
        elif event == 'CONNECTED':
            self.push(self.context_id, 'Connected.')
        elif event == 'DISCONNECTED':
            self.first_connection = False
            self.push(self.context_id, 'Connection lost.')
