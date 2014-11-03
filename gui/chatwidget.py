#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk, Pango


class ChatWidget(Gtk.TextView):
    def __init__(self):
        Gtk.TextView.__init__(self)
        self.set_editable(False)
        self.set_cursor_visible(False)
        self.set_justification(Gtk.Justification.LEFT)
        self.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.tag_bold = self.get_buffer().create_tag(
            "bold", weight=Pango.Weight.BOLD)

    def notify(self, event, data):
        if event == 'MSG':
            buffer = self.get_buffer()
            if buffer.get_char_count() != 0:
                buffer.insert_at_cursor('\r\n')
            mark = buffer.create_mark(None, buffer.get_end_iter(), True)
            buffer.insert_at_cursor('{0}:  {1}'.format(data[0], data[1]))
            tag_iter_1 = buffer.get_iter_at_mark(mark)
            tag_iter_2 = buffer.get_iter_at_mark(mark)
            tag_iter_2.forward_chars(len(data[0]))
            buffer.apply_tag(self.tag_bold, tag_iter_1, tag_iter_2)
            buffer.delete_mark(mark)
        elif event == 'SUBSCRIBER':
            buffer = self.get_buffer()
            if buffer.get_char_count() != 0:
                buffer.insert_at_cursor('\r\n')
            mark = buffer.create_mark(None, buffer.get_end_iter(), True)
            buffer.insert_at_cursor('{0} has subscriber!'.format(data[0]))
            tag_iter_1 = buffer.get_iter_at_mark(mark)
            tag_iter_2 = buffer.get_end_iter()
            buffer.apply_tag(self.tag_bold, tag_iter_1, tag_iter_2)
            buffer.delete_mark(mark)
        return
