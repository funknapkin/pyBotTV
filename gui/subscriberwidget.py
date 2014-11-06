#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk, Pango


class SubscriberWidget(Gtk.ScrolledWindow):
    def __init__(self):
        """
        This widget shows new subscribers in a text box.
        """
        # Init ScrolledWindow
        Gtk.ScrolledWindow.__init__(self)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        # Init TextView
        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_justification(Gtk.Justification.LEFT)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.add(self.text_view)
        # Bind events and init misc stuff
        self.msg_count = 0
        self.max_messages = 30
        self.text_view.connect('size-allocate', self.scroll_bottom)
        self.tag_bold = self.text_view.get_buffer().create_tag(
            "bold", weight=Pango.Weight.BOLD)

    def notify(self, event, data):
        """
        Notify this widget of an event.

        Args:
            event: Type of the event
            data: Additionnal data for this event
        """
        if event == 'SUBSCRIBER':
            text_buffer = self.text_view.get_buffer()
            if self.msg_count != 0:
                text_buffer.insert_at_cursor('\r\n')
            mark = text_buffer.create_mark(
                None, text_buffer.get_end_iter(), True)
            text_buffer.insert_at_cursor('{0} has subscribed!'.format(data[0]))
            tag_iter_1 = text_buffer.get_iter_at_mark(mark)
            tag_iter_2 = text_buffer.get_end_iter()
            text_buffer.apply_tag(self.tag_bold, tag_iter_1, tag_iter_2)
            text_buffer.delete_mark(mark)
            self.msg_count += 1
            if self.msg_count > self.max_messages:
                iter_1 = text_buffer.get_start_iter()
                iter_2 = text_buffer.get_iter_at_line(1)
                text_buffer.delete(iter_1, iter_2)
                self.msg_count -= 1
        return

    def scroll_bottom(self, event, data=None):
        """
        Scroll to the bottom of the window.

        Args:
            event: Event that called this function
            data: Additionnal data for this event
        """
        adj = self.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        self.text_view.queue_draw()
        return
