#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk

from gui.chatwidget import ChatWidget
from gui.irchandler import IrcHandler
from gui.statusbar import StatusBar
from gui.subscriberwidget import SubscriberWidget


class MainWindow(Gtk.Window):
    def __init__(self):
        """
        This class creates the main window for this program's GUI. It
        initializes relevant widgets.
        """
        Gtk.Window.__init__(self, title='pyBotTV')
        self._init_chat_widget()
        self._init_subscriber_widget()
        self._init_status_bar()
        self._init_irc_handler()
        self._init_layout()

    def _init_chat_widget(self):
        self.chat = ChatWidget()

    def _init_irc_handler(self):
        self.irchandler = IrcHandler()
        self.irchandler.register_observer(self.chat, 'MSG')
        self.irchandler.register_observer(self.subscriber, 'SUBSCRIBER')
        self.irchandler.register_observer(self.status, 'CONNECTING')
        self.irchandler.register_observer(self.status, 'CONNECTED')
        self.irchandler.register_observer(self.status, 'DISCONNECTED')

    def _init_layout(self):
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(6)
        self.grid.set_column_spacing(6)
        self.grid.attach(self.chat, 1, 1, 1, 4)
        self.grid.attach(self.subscriber, 1, 5, 1, 1)
        self.grid.attach(self.status, 1, 6, 1, 1)
        self.add(self.grid)

    def _init_status_bar(self):
        self.status = StatusBar()

    def _init_subscriber_widget(self):
        self.subscriber = SubscriberWidget()
