#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# TODO:
#   - Add clear button + timestamps to subscriberwidget
#   - Add ability to send chat messages to IRC, via a Queue
#   - Add notebook with other widgets (userlist, poll, etc.)
#
# Possible improvements:
#   - Non-blocking emotes download for faster startup
#   - Don't download emotes list every time app is opened
#   - Predownload emotes
#   - Save display names to file

import logging
import threading
from gi.repository import Gtk

from gui.mainwindow import MainWindow
from lib import config
from lib.irceventgenerator import IrcEventGenerator


def gui_main(config, retval):
    win = MainWindow(config)
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
        args=(c, win))
    gui_thread.start()
    gui_thread.join()
    irc_thread = threading.Thread(
        target=irc_main, daemon=True,
        args=(c, win[0].irchandler.receive_message))
    irc_thread.start()
    Gtk.main()
