# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.wa_actions import mysql_utils


def test_should_throw_valueerror_for_wrong_config_input(mocker):
    mock_wrong_config = {
        'host': 'localhost',
        'port': 443,
        'user': 'admin'
    }

    try:
        mysql_utils.MySQLUtil(**mock_wrong_config)
    except ValueError:
        assert True


def test_should_throw_valueerror_if_cannot_convert_port_to_int(mocker):
    mock_wrong_config = {
        'host': 'localhost',
        'port': 'port',
        'user': 'admin',
        'password': 'secret'
    }

    try:
        mysql_utils.MySQLUtil(**mock_wrong_config)
    except ValueError:
        assert True
