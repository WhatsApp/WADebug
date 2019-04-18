# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.config import Config, ConfigLoadError
from yaml.parser import ParserError


def test_should_not_be_in_dev_mode(mocker):
    assert Config().development_mode is False, 'Config().development_mode should be False before commiting code'


def test_network_should_not_be_disabled(mocker):
    assert Config().disable_send_data is False, 'Config().disable_send_data should be False before commiting code'


def test_should_return_correct_config(mocker):
    mock_config = {'mock': 'config'}
    mocker.patch('wadebug.config.Config._load_config_from_file', return_value=mock_config)

    assert Config().values == mock_config
    assert Config().load_error == ConfigLoadError.NONE


def test_should_return_config_invalid(mocker):
    mock_exception = ParserError('something goes wrong!')
    mocker.patch('wadebug.config.Config._load_config_from_file', side_effect=mock_exception)

    assert Config().load_error == ConfigLoadError.CONFIG_INVALID
    assert Config().values == {}


def test_should_return_config_missing(mocker):
    mock_exception = Exception('something goes wrong!')
    mocker.patch('wadebug.config.Config._load_config_from_file', side_effect=mock_exception)

    assert Config().load_error == ConfigLoadError.CONFIG_MISSING
    assert Config().values == {}
