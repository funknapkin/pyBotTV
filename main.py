#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# TODO:
#   - Change MainWindow to be Application(), and move it to main thread
#   - Add clear button + timestamps to subscriberwidget
#   - Add notebook with other widgets (userlist, poll, etc.)
#   - Cache pixbuf to avoid reading from disk at every emote
#   - Add force update button to subscriberwidget
#
# Possible improvements:
#   - Non-blocking emotes download for faster startup
#   - Don't download emotes list every time app is opened
#   - Predownload emotes
#   - Save display names to file
#   - Add option to display names the same way twitch's app does
#       First letter capitalized, rest lower case

import logging
import queue
import threading
from gi.repository import Gtk

from gui.mainwindow import MainWindow
from lib import config
from lib.irceventgenerator import IrcEventGenerator
from lib.ircsender import IrcSender


def gui_main(config, out_queue, retval):
    win = MainWindow(config, out_queue)
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    retval.append(win)
    return


def irc_main(config, glib_func):
    irc_event_generator = IrcEventGenerator(config, glib_func)
    irc_event_generator.run()
    return


def irc_sender_main(config, out_queue):
    irc_sender = IrcSender(config, out_queue)
    irc_sender.run()
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
    out_queue = queue.Queue()
    win = []
    gui_thread = threading.Thread(
        target=gui_main, daemon=False,
        args=(c, out_queue, win))
    gui_thread.start()
    gui_thread.join()
    irc_thread = threading.Thread(
        target=irc_main, daemon=True,
        args=(c, win[0].irchandler.receive_message))
    irc_thread.start()
    irc_sender_thread = threading.Thread(
        target=irc_sender_main, daemon=True,
        args=(c, out_queue))
    irc_sender_thread.start()
    Gtk.main()
