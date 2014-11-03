#!/usr/bin/env python
# -*- encoding:utf-8 -*-


class IrcHandler():
    def __init__(self):
        self.observers = {}

    def notify_observers(self, event, data):
        for observer, subscriptions in self.observers.items():
            if event in subscriptions:
                observer.notify(event, data)

    def receive_message(self, msg):
        self.notify_observers(msg[0], msg[1:])

    def register_observer(self, observer, event):
        if observer in self.observers.keys():
            self.observers[observer].add(event)
        else:
            self.observers[observer] = set([event])

    def unregister_observer(self, observer, event):
        if observer in self.observer.keys():
            try:
                self.observers[observer].remove(event)
                if len(observers[observer]) == 0:
                    del self.observers[observer]
            except KeyError:
                pass
        return
