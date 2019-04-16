# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from enum import Enum
from six import with_metaclass

import pkg_resources
import yaml
import os


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigLoadError(Enum):
    NONE = 1
    CONFIG_MISSING = 2
    CONFIG_INVALID = 3


class Config(with_metaclass(Singleton)):
    SAMPLE_CONFIG_FILE = 'wadebug.conf.yml.SAMPLE'
    CONFIG_FILE = 'wadebug.conf.yml'

    _disable_send_data = False

    _config_load_error = ConfigLoadError.NONE
    _config_load_exception = None
    _config_create_exception = None
    _config = {}

    def __init__(self):
        try:
            self._development_mode = (
                os.environ.get("WADEBUG_DEV_MODE", "False") == "True"
            )
            self._config = self._load_config_from_file()
        except yaml.parser.ParserError as e:
            self._config_load_error = ConfigLoadError.CONFIG_INVALID
            self._config_load_exception = e
        except Exception:
            self._config_load_error = ConfigLoadError.CONFIG_MISSING

    def _load_config_from_file(self):
        with open(self.CONFIG_FILE, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        return config

    @property
    def development_mode(self):
        return self._development_mode

    @property
    def disable_send_data(self):
        return self._disable_send_data

    @property
    def values(self):
        return self._config

    @property
    def load_error(self):
        return self._config_load_error

    @property
    def load_exception(self):
        return self._config_load_exception

    def create_default_config_file(self):
        try:
            config_file_stream = pkg_resources.resource_string(__name__, self.SAMPLE_CONFIG_FILE)
            with open(self.CONFIG_FILE, 'wb') as f:
                f.write(config_file_stream)
            return True
        except Exception as e:
            self._config_create_exception = e
            return False

    @property
    def create_exception(self):
        return self._config_create_exception
