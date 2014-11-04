#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# TODO:
#   - Finish twitchparser1 for all messages
#       - Mod demoted event
#   - Simple GTK chat viewer
#       - Mostly done, but need a max length on chat
#   - Finish and test twitchparser2 and twitchparser3
#   - Update UML and documentation
#   - Add a menubar with the option to quit

import logging
import threading
from gi.repository import Gtk

from gui.mainwindow import MainWindow
from lib import config
from lib.irceventgenerator import IrcEventGenerator


def gui_main(retval):
    win = MainWindow()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    retval.append(win)
    return


def irc_main(config, glib_func):
    irc_event_generator = IrcEventGenerator(config, glib_func)
    irc_event_generator.run()
    return

if __name__ == '__main__':
    # Load config file
    try:
        c = config.config('./config.yaml')
    except RuntimeError:
        print('Invalid config file')
        sys.exit(0)
    # Configure logger
    log_levels = {
        'debug': logging.DEBUG, 'info': logging.INFO,
        'warning': logging.WARNING, 'error': logging.ERROR,
        'critical': logging.CRITICAL}
    logging.basicConfig(
        filename=c['debug']['log-file'], filemode='w',
        level=log_levels[c['debug']['log-level']])
    # Create threads
    win = []
    gui_thread = threading.Thread(
        target=gui_main, daemon=False,
        args=(win,))
    gui_thread.start()
    gui_thread.join()
    irc_thread = threading.Thread(
        target=irc_main, daemon=True,
        args=(c, win[0].irchandler.receive_message))
    irc_thread.start()
    Gtk.main()
