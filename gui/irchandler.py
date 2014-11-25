#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import GLib


class IrcHandler():
    def __init__(self, config):
        """
        This class receives message from the irc thread and notifies the
        widgets.

        Args:
            config: A dictionnary with configuration options.
        """
        self.config = config
        self.observers = {}

    def notify_observers(self, event, data):
        """
        Notify all observers of an event if they subscribed to that event's
        type.

        Args:
            event: Event type.
            data: Additionnal data for that event.
        """
        for observer, subscriptions in self.observers.items():
            if event in subscriptions:
                GLib.idle_add(observer.notify, event, data)

    def receive_message(self, msg):
        """
        Receive a message from the irc thread.
        """
        self.notify_observers(msg[0], msg[1:])

    def register_observer(self, observer, event):
        """
        Register a new observer to an event type.

        Args:
            observer: New observer.
            event: Event type to subscribe.
        """
        if observer in self.observers.keys():
            self.observers[observer].add(event)
        else:
            self.observers[observer] = set([event])

    def unregister_observer(self, observer, event):
        """
        Unregister an observer from an event type.

        Args:
            observer: New observer.
            event: Event type to subscribe.
        """
        if observer in self.observer.keys():
            try:
                self.observers[observer].remove(event)
                if len(observers[observer]) == 0:
                    del self.observers[observer]
            except KeyError:
                pass
        return
