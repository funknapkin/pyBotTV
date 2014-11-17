#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from gi.repository import Gtk, Gio


class MenuBar():
    def __init__(self, config, action_group, action_prefix):
        """
        This widget defines a menu bar for the main application.

        Note that modification of the menu's items might require modifications
        to the MainWindow class to handle the Actions.

        Args:
            config: A dictionnary with configuration options.
            action_group: A Gio.ActionGroup to add actions to
            action_prefix: Prefix to add to the action's name on the menu items
        """
        self.config = config
        # Create file menu
        filemenu = Gio.Menu()
        menuitem = Gio.MenuItem.new('Quit', '{0}.quit'.format(action_prefix))
        menuitem.set_attribute([['accel', 's', '<Ctrl>q']])
        filemenu.append_item(menuitem)
        # Create menu bar
        menumodel = Gio.Menu()
        menumodel.append_submenu('File', filemenu)
        self.menubar = Gtk.MenuBar.new_from_model(menumodel)
        # Create actions
        quit_action = Gio.SimpleAction.new('quit', None)
        action_group.add_action(quit_action)
