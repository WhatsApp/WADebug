# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import ANY, patch
from wadebug import results
from wadebug.wa_actions.implementations import check_mysql_permissions
from wadebug.wa_actions.mysql_utils import MySQLUtil


class TestCheckMySQLPermissions(unittest.TestCase):
    @patch.object(results, "OK", autospec=True)
    def test_should_return_ok_when_all_privs_granted(self, mock_ok):
        mock_positive_result = {
            "Select_priv": "Y",
            "Insert_priv": "Y",
            "Update_priv": "Y",
            "Delete_priv": "Y",
            "Create_priv": "Y",
            "Alter_priv": "Y",
            "Index_priv": "Y",
            "Drop_priv": "Y",
        }
        mock_config = {
            "db": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "secret",
            }
        }

        with patch.object(
            MySQLUtil, "user_has_privileges", return_value=mock_positive_result
        ):
            check_mysql_permissions.CheckMySQLPermissions().run(config=mock_config)
            mock_ok.assert_called()

    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_when_some_privs_missing(self, mock_problem):
        mock_negative_result = {
            "Select_priv": "Y",
            "Insert_priv": "Y",
            "Update_priv": "Y",
            "Delete_priv": "Y",
            "Create_priv": "Y",
            "Alter_priv": "N",
            "Index_priv": "N",
            "Drop_priv": "Y",
        }
        mock_config = {
            "db": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "secret",
            }
        }

        with patch.object(
            MySQLUtil, "user_has_privileges", return_value=mock_negative_result
        ):
            check_mysql_permissions.CheckMySQLPermissions().run(config=mock_config)
            mock_problem.assert_called_with(
                ANY,
                "Some required db permisions are missing",
                "Missing Permissions : Alter_priv , Index_priv",
                ANY,
            )

    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_cannot_connect_to_db(self, mock_problem):
        mock_exception = Exception("Cannot connect to db")
        mock_config = {
            "db": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "secret",
            }
        }

        with patch.object(MySQLUtil, "user_has_privileges", side_effect=mock_exception):
            check_mysql_permissions.CheckMySQLPermissions().run(config=mock_config)
            mock_problem.assert_called_with(
                ANY, "Unable to connect to db to check permisions", mock_exception, ANY
            )

    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_empty_result_returned(self, mock_problem):
        mock_config = {
            "db": {
                "host": "localhost",
                "port": 3306,
                "user": "testuser",
                "password": "secret",
            }
        }

        with patch.object(MySQLUtil, "user_has_privileges", return_value=None):
            check_mysql_permissions.CheckMySQLPermissions().run(config=mock_config)
            mock_problem.assert_called_with(
                ANY,
                "Checking permissions returns empty result",
                "User testuser doesn't exist",
                "Make sure the correct db user is set in the config file",
            )
