# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import patch
from wadebug import results
from wadebug.wa_actions.common import common_results
from wadebug.wa_actions.implementations import check_mysql_connection
from wadebug.wa_actions.mysql_utils import MySQLUtil


class TestMySQLConnection(unittest.TestCase):
    @patch.object(common_results, "missing_config")
    def test_should_return_missing_config_result_if_no_db_config(self, *_):
        check_mysql_connection.CheckMySQLConnection().run(config={})

        common_results.missing_config.assert_called()

    @patch.object(
        MySQLUtil, "try_connect", side_effect=Exception("Cannot connect to db")
    )
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_cannot_connect_to_db(self, *_):
        mock_config = {
            "db": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "secret",
            }
        }
        check_mysql_connection.CheckMySQLConnection().run(config=mock_config)

        results.Problem.assert_called()

    @patch.object(MySQLUtil, "try_connect", autospec=True)
    @patch.object(results, "OK", autospec=True)
    def test_should_return_OK_if_can_connect_to_db(self, *_):
        mock_config = {
            "db": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "secret",
            }
        }
        check_mysql_connection.CheckMySQLConnection().run(config=mock_config)

        results.OK.assert_called()
