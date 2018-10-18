# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.wa_actions.implementations import check_mysql_connection
from wadebug.wa_actions.common import common_results
from wadebug.wa_actions.mysql_utils import MySQLUtil
from wadebug import results


def test_should_return_missing_config_result_if_no_db_config(mocker):
    mocker.patch.object(common_results, 'missing_config')

    check_mysql_connection.CheckMySQLConnection().run(config={})

    common_results.missing_config.assert_called()


def test_should_return_problem_if_cannot_connect_to_db(mocker):
    mocker.patch.object(
        MySQLUtil,
        'try_connect',
        side_effect=Exception('Cannot connect to db'))
    mocker.patch.object(results, 'Problem', autospec=True)

    mock_config = {
        'db': {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'secret'
        }
    }
    check_mysql_connection.CheckMySQLConnection().run(config=mock_config)

    results.Problem.assert_called()


def test_should_return_OK_if_can_connect_to_db(mocker):
    mocker.patch.object(MySQLUtil, 'try_connect', autospec=True)
    mocker.patch.object(results, 'OK', autospec=True)

    mock_config = {
        'db': {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'secret'
        }
    }
    check_mysql_connection.CheckMySQLConnection().run(config=mock_config)

    results.OK.assert_called()
