# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import patch
from wadebug.config import Config, ConfigLoadError
from yaml.parser import ParserError


class TestConfig(unittest.TestCase):
    def test_should_not_be_in_dev_mode(self):
        assert (
            Config().development_mode is False
        ), "Config().development_mode should be False before committing code"

    def test_network_should_not_be_disabled(self):
        assert (
            Config().disable_send_data is False
        ), "Config().disable_send_data should be False before committing code"

    def test_should_return_correct_config(self):
        mock_config = {"mock": "config"}

        with patch(
            "wadebug.config.Config._load_config_from_file", return_value=mock_config
        ):
            assert Config().values == mock_config
            assert Config().load_error == ConfigLoadError.NONE

    def test_should_return_config_invalid(self):
        mock_parse_exception = ParserError("something goes wrong!")

        with patch(
            "wadebug.config.Config._load_config_from_file",
            side_effect=mock_parse_exception,
        ):
            assert Config().load_error == ConfigLoadError.CONFIG_INVALID
            assert Config().values == {}

    def test_should_return_config_missing(self):
        mock_exception = Exception("something goes wrong!")

        with patch(
            "wadebug.config.Config._load_config_from_file", side_effect=mock_exception
        ):
            assert Config().load_error == ConfigLoadError.CONFIG_MISSING
            assert Config().values == {}
