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
        data['server'] = str(data['server'])
        data['port'] = int(data['port'])
        data['channel'] = str(data['channel'])
        data['channel'] = data['channel'] if data['channel'][0] == '#' \
            else '#{0}'.format(data['channel'])
        data['user'] = str(data['user'])
        data['password'] = str(data['password'])
        data['buffer_size'] = int(data['buffer_size'])
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
