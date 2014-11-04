#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk


class StatusBar(Gtk.Statusbar):
    def __init__(self):
        Gtk.Statusbar.__init__(self)
        self.set_halign(Gtk.Align.END)
        self.context_id = self.get_context_id('info')
        self.first_connection = True

    def notify(self, event, data):
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
