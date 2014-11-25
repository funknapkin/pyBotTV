#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk, Gio, Gdk

from gui.chatdisplay import ChatDisplay
from gui.chatentry import ChatEntry
from gui.irchandler import IrcHandler
from gui.statusbar import StatusBar
from gui.subscriberwidget import SubscriberWidget
from gui.subscribercontrol import SubscriberControl
from gui.menubar import MenuBar


class MainApplication(Gtk.Application):
    def __init__(self, config, out_queue, func_queue):
        Gtk.Application.__init__(self)
        self.config = config
        self.out_queue = out_queue
        self.func_queue = func_queue

    def do_activate(self):
        win = MainWindow(self, self.config, self.out_queue)
        win.show_all()
        self.func_queue.put(win.irchandler.receive_message)

    def do_startup(self):
        Gtk.Application.do_startup(self)


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app, config, out_queue):
        """
        This class creates the main window for this program's GUI. It
        initializes relevant widgets.

        Args:
            config: A dictionnary with configuration options.
        """
        Gtk.Window.__init__(self, title='pyBotTV', application=app)
        self.config = config
        self.out_queue = out_queue
        self.app = app
        # Set window options
        self.set_default_size(640, 480)
        # Init widgets
        self._init_chat_display()
        self._init_chat_entry()
        self._init_subscriber_widget()
        self._init_subscriber_control()
        self._init_status_bar()
        self._init_menu_bar()
        self._init_irc_handler()
        self._init_layout()

    def on_app_quit(self, *args):
        """
        Function called when the 'quit' action is activated. Calls GTK
        to close the window.
        """
        self.app.quit()

    def _init_chat_display(self):
        self.chat = ChatDisplay(self.config)

    def _init_chat_entry(self):
        self.chat_entry = ChatEntry(self.config, self.out_queue)

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
        vbox_chat = Gtk.Box.new(Gtk.Orientation.VERTICAL, 2)
        vbox_chat.add(self.chat)
        vbox_chat.add(self.chat_entry)
        frame_chat = Gtk.Frame.new('Chat')
        frame_chat.add(vbox_chat)
        self.grid.attach(frame_chat, 0, 1, 1, 4)
        vbox_subscriber = Gtk.Box.new(Gtk.Orientation.VERTICAL, 2)
        vbox_subscriber.add(self.subscriber)
        vbox_subscriber.add(self.subscriber_control)
        frame_subscriber = Gtk.Frame.new('New subscribers')
        frame_subscriber.add(vbox_subscriber)
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

    def _init_subscriber_control(self):
        text_buffer = self.subscriber.text_view.get_buffer()
        self.subscriber_control = SubscriberControl(text_buffer)
