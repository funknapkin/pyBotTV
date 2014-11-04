#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk, Pango


class ChatWidget(Gtk.ScrolledWindow):
    def __init__(self):
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
        self.text_view.connect('size-allocate', self.on_text_changed)
        self.tag_bold = self.text_view.get_buffer().create_tag(
            "bold", weight=Pango.Weight.BOLD)

    def notify(self, event, data):
        if event == 'MSG':
            text_buffer = self.text_view.get_buffer()
            if text_buffer.get_char_count() != 0:
                text_buffer.insert(text_buffer.get_end_iter(), '\r\n')
            mark = text_buffer.create_mark(
                None, text_buffer.get_end_iter(), True)
            text_buffer.insert(text_buffer.get_end_iter(),
                               '{0}:  {1}'.format(data[0], data[1]))
            tag_iter_1 = text_buffer.get_iter_at_mark(mark)
            tag_iter_2 = text_buffer.get_iter_at_mark(mark)
            tag_iter_2.forward_chars(len(data[0]))
            text_buffer.apply_tag(self.tag_bold, tag_iter_1, tag_iter_2)
            text_buffer.delete_mark(mark)
        elif event == 'SUBSCRIBER':
            text_buffer = self.get_buffer()
            if text_buffer.get_char_count() != 0:
                text_buffer.insert(text_buffer.get_end_iter(), '\r\n')
            mark = text_buffer.create_mark(
                None, text_buffer.get_end_iter(), True)
            text_buffer.insert(text_buffer.get_end_iter(),
                               '{0} has subscriber!'.format(data[0]))
            tag_iter_1 = text_buffer.get_iter_at_mark(mark)
            tag_iter_2 = text_buffer.get_end_iter()
            text_buffer.apply_tag(self.tag_bold, tag_iter_1, tag_iter_2)
            text_buffer.delete_mark(mark)
        return

    def on_text_changed(self, event, data):
        adj = self.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        return
