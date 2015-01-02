pyBotTV
=======

*pyBotTV* is a python tool to connect to a Twitch.tv chat room and monitor chat.
It also offers some tools to keep track of subscribers, start polls, and more.

*pyBotTV* is currently in alpha. Some features are incomplete and/or broken.

Features
========

This is a listed of current and planned features.

* Display the chat room;
* Send messages to the chat room;
* Display new subscribers;
* Display a list of users in the chat room;
* Create polls, taking the users' answers from the chat;

Installation and requirements
=============================

* Install this application's requirements:
    * [Python 3](https://www.python.org/downloads/) or above;
    * [GTK+](http://www.gtk.org/download/);
    * [PyGObject](https://wiki.gnome.org/action/show/Projects/PyGObject);
    * [PyYAML](http://pyyaml.org/), also available on [pip](https://pypi.python.org/pypi/PyYAML).
* Download a copy of this repository. You can either use `git` or click the
  `Download ZIP` button on the right of this page;
* Modify the configuration file to your liking. See the section below;
* Launch `main.pyw`.


Configuration
=============

At the moment, *pyBotTV*'s configuration is made entirely through its configuration
file. First, start by copying *config.yaml.default* into *config.yaml*. Most options
have sensible default values, and you only need to change settings in the *irc*. section.

irc
---

Options related to the twitch IRC server, including login options.

* **server:** Server URL;
* **port:** Server port;
* **channel:** IRC channel to join after connecting to the server, usually the user name in lower case;
* **user:** Your user name to log in the server;
* **password:** Your login key. If you don't have one, get it [here](http://twitchapps.com/tmi/);
* **buffer_size:** Size of the buffer for communications with the server;
* **send_timeout:** Time to wait before a sent message is considered "lost";
* **log_folder:** Folder where the IRC logs are kept.

gui
---

Options related to the user interface and its multiple widgets.

* **emote_globals_path:** Folder where the global emotes are saved;
* **emote_subscriber_path:** Folder where subscriber emotes are saved;
* **badges_path:** Folder where badges are saved;
* **chat_maxmessage:** Maximum number of messages to keep on the chat window before older messages are deleted;
* **chat_linespacing:** Padding between messages in the chat window;
* **chat_cache_size:** Cache size for multiple caches, such as usercolor or emotes;
* **display_names_cache_size:** Number of display names to keep;
* **display_names_file:** File where the display names are saved;
* **display_names_save_interval:** Interval between the display names autosave, in seconds;
* **subscriber_maxmessages:** Maximum number of messages to keep on the subscriber window before older messages are deleted.

debug
-----

Debug options for the application to help find bugs.

* **log-level:** Type of messages to write to the log file. Possible values are *debug*, *info*, *warning*, *error*, *critical*;
* **log-file:** Path to the log file.
