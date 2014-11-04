#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk


class StatusBar(Gtk.Statusbar):
    def __init__(self):
        Gtk.Statusbar.__init__(self)
        self.context_id = self.get_context_id('info')
        self.push(self.context_id, 'Hello World!')

    def notify(self, event, data):
        if event == 'SUBSCRIBER':
            self.pop(self.context_id)
