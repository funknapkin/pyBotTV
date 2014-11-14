#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk, Gio, Gdk

from gui.chatwidget import ChatWidget
from gui.irchandler import IrcHandler
from gui.statusbar import StatusBar
from gui.subscriberwidget import SubscriberWidget
from gui.menubar import MenuBar


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, config):
        """
        This class creates the main window for this program's GUI. It
        initializes relevant widgets.

        Args:
            config: A dictionnary with configuration options.
        """
        Gtk.Window.__init__(self, title='pyBotTV')
        self.config = config
        # Set window options
        self.set_default_size(640, 480)
        # Init widgets
        self._init_chat_widget()
        self._init_subscriber_widget()
        self._init_status_bar()
        self._init_menu_bar()
        self._init_irc_handler()
        self._init_layout()

    def on_app_quit(self, *args):
        """
        Function called when the 'quit' action is activated. Calls GTK
        to close the window.
        """
        Gtk.main_quit()

    def _init_chat_widget(self):
        self.chat = ChatWidget(self.config)

    def _init_irc_handler(self):
        self.irchandler = IrcHandler(self.config)
        self.irchandler.register_observer(self.chat, 'MSG')
        self.irchandler.register_observer(self.chat, 'USERCOLOR')
        self.irchandler.register_observer(self.chat, 'EMOTESET')
        self.irchandler.register_observer(self.chat, 'SPECIALUSER')
        self.irchandler.register_observer(self.chat, 'MOD')
        self.irchandler.register_observer(self.chat, 'DEMOD')
        self.irchandler.register_observer(self.subscriber, 'SUBSCRIBER')
        self.irchandler.register_observer(self.status, 'CONNECTING')
        self.irchandler.register_observer(self.status, 'CONNECTED')
        self.irchandler.register_observer(self.status, 'DISCONNECTED')

    def _init_layout(self):
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(6)
        self.grid.set_column_spacing(6)
        self.grid.set_margin_top(0)
        self.grid.set_margin_bottom(0)
        self.grid.set_margin_left(3)
        self.grid.set_margin_right(3)
        self.grid.attach(self.menu.menubar, 0, 0, 1, 1)
        frame_chat = Gtk.Frame.new('Chat')
        frame_chat.add(self.chat)
        self.grid.attach(frame_chat, 0, 1, 1, 4)
        frame_subscriber = Gtk.Frame.new('New subscribers')
        frame_subscriber.add(self.subscriber)
        self.grid.attach(frame_subscriber, 0, 5, 1, 1)
        self.grid.attach(self.status, 0, 6, 1, 1)
        self.add(self.grid)

    def _init_menu_bar(self):
        action_group = Gio.SimpleActionGroup()
        self.menu = MenuBar(self.config, action_group, 'app')
        self.insert_action_group('app', action_group)
        action_group.lookup_action('quit').connect(
            'activate', self.on_app_quit)
        accel_group = Gtk.AccelGroup()
        accel_group.connect(Gdk.KEY_q, Gdk.ModifierType.CONTROL_MASK,
                            0, self.on_app_quit)
        self.add_accel_group(accel_group)

    def _init_status_bar(self):
        self.status = StatusBar(self.config)

    def _init_subscriber_widget(self):
        self.subscriber = SubscriberWidget(self.config)
