#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import yaml


def config(yaml_path):
    """
    Create a dictionary that contains all options from a yaml file.

    Args:
        yaml_path: Path to the yaml file.

    Returns:
        A dictionary with the data from the yaml file.

    Raises:
        RuntimeError if some options are missing from the config file.
        Note that having no error this doesn't mean all options are correct,
        although some sanity checks are made.
    """
    yaml_file = open(yaml_path, 'r')
    try:
        data = yaml.load(yaml_file, yaml.Loader)
    except AttributeError:
        data = yaml.load(yaml_file, yaml.CLoader)
    try:
        data['irc']['server'] = str(data['irc']['server'])
        data['irc']['port'] = int(data['irc']['port'])
        data['irc']['channel'] = str(data['irc']['channel'])
        data['irc']['channel'] = data['irc']['channel'] if \
            data['irc']['channel'][0] == '#' else \
            '#{0}'.format(data['irc']['channel'])
        data['irc']['channel'] = data['irc']['channel'].lower()
        data['irc']['user'] = str(data['irc']['user'])
        data['irc']['password'] = str(data['irc']['password'])
        data['irc']['buffer_size'] = int(data['irc']['buffer_size'])
        data['irc']['log_file'] = str(data['irc']['log_file'])
        data['gui']['emote_globals_path'] = str(
            data['gui']['emote_globals_path'])
        data['gui']['emote_subscriber_path'] = str(
            data['gui']['emote_subscriber_path'])
        data['gui']['badges_path'] = str(data['gui']['badges_path'])
        data['gui']['chat_maxmessages'] = int(data['gui']['chat_maxmessages'])
        data['gui']['chat_linespacing'] = int(data['gui']['chat_linespacing'])
        data['gui']['chat_cache_size'] = int(data['gui']['chat_cache_size'])
        data['gui']['subscriber_maxmessages'] = int(
            data['gui']['subscriber_maxmessages'])
        data['debug']['log-level'] = str(data['debug']['log-level'])
        data['debug']['log-file'] = str(data['debug']['log-file'])
    except KeyError:
        raise RuntimeError('Options missing from the config file')
    except ValueError:
        raise RuntimeError('Invalid option in the config file')
    return data

if __name__ == '__main__':
    # Simple test script
    c = config('./config.yaml')
    print(c)
