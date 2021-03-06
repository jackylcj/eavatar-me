# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import sys

from ava import APP_NAME


# helper function for constructing paths to resource files.
def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)

    abspath = os.path.abspath(os.path.join(__file__, "..", ".."))
    abspath = os.path.dirname(abspath)
    return os.path.join(abspath, relative)


# helper function for constructing paths to resource files.
def base_path():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    else:
        # assumes this file is located at src/ava/util/__init__.py
        abspath = os.path.abspath(os.path.join(__file__, "..", ".."))
        abspath = os.path.dirname(abspath)
        return abspath


def is_frozen():
    """ Checks if in frozen mode.
    :return:
    """
    return hasattr(sys, "frozen")


def get_app_dir(app_name=APP_NAME, roaming=True):
    folder = os.environ.get('AVA_POD')
    if folder is not None:
        return folder

    if sys.platform.startswith(b'win'):
        key = roaming and 'APPDATA' or 'LOCALAPPDATA'
        folder = os.environ.get(key)
        if folder is None:
            folder = os.path.expanduser('~')
        return os.path.join(folder, app_name)

    if sys.platform.startswith(b'darwin'):
        return os.path.join(os.path.expanduser(
            '~/Library/Application Support'), app_name)
    return os.path.join(
        os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
        '-'.join(app_name.split()).lower())
