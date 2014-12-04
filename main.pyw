#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# TODO:
#   - Create a proper readme
#   - Add notebook with other widgets (userlist, poll, etc.)
#   - Add force update button to subscriberwidget
#   - Make sure character encoding is working properly
#
# Possible improvements:
#   - Minimum retry time for badges/emotes init.
#   - Don't download emotes list every time app is opened
#   - Predownload emotes
#   - Add option to display names the same way twitch's app does
#       First letter capitalized, rest lower case
#       Lowers delay when displaying names

import logging
import queue
import sys
import threading
from gi.repository import Gtk

from gui.mainwindow import MainApplication
from lib import config
from lib.irceventgenerator import IrcEventGenerator
from lib.ircsender import IrcSender


def gui_main(config, out_queue, retval):
    win = MainWindow(config, out_queue)
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    retval.append(win)
    return


def irc_main(config, func_queue):
    irc_event_generator = IrcEventGenerator(config, func_queue)
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
    func_queue = queue.Queue()
    irc_thread = threading.Thread(
        target=irc_main, daemon=True,
        args=(c, func_queue))
    irc_thread.start()
    irc_sender_thread = threading.Thread(
        target=irc_sender_main, daemon=True,
        args=(c, out_queue))
    irc_sender_thread.start()
    # Create GUI
    app = MainApplication(c, out_queue, func_queue)
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
