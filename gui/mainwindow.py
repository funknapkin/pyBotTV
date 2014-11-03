#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk

from gui.chatwidget import ChatWidget
from gui.irchandler import IrcHandler


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='Hello World')
        self.irchandler = IrcHandler()
        self.chat = ChatWidget()
        self.add(self.chat)
        self.irchandler.register_observer(self.chat, 'MSG')
        self.irchandler.register_observer(self.chat, 'SUBSCRIBER')

    def on_button_clicked(self, widget):
        print('Hello World')
