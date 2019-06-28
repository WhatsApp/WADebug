# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import call, patch
from wadebug import results, ui


class TestUi(unittest.TestCase):
    @patch("click.echo")
    def test_result_details_are_properly_indented(self, mock_echo):
        mock_result = results.Problem(
            "mock_action",
            "message line 1\nmessage line 2",
            "details line 1\ndetails line 2",
            "remediation line 1\nremediation line 2",
            "traceback line 1\ntraceback line 2",
        )

        ui.print_result_details(mock_result)

        mock_echo.assert_has_calls(
            [
                call("    message line 1\n    message line 2"),
                call("    details line 1\n    details line 2"),
                call("    remediation line 1\n    remediation line 2"),
            ]
        )

    @patch("click.echo")
    @patch("wadebug.config.Config.development_mode", return_value=True)
    def test_traceback_are_printed_in_dev_mode(self, mock_dev_mode, mock_echo):
        mock_result = results.Problem(
            "mock_action",
            "message line 1\nmessage line 2",
            Exception("error details line 1\nerror details line 2"),
            "remediation line 1\nremediation line 2",
            "traceback line 1\ntraceback line 2",
        )

        ui.print_result_details(mock_result)

        mock_echo.assert_has_calls(
            [
                call("    message line 1\n    message line 2"),
                call("    error details line 1\n    error details line 2"),
                call("    remediation line 1\n    remediation line 2"),
                call("    traceback line 1\n    traceback line 2"),
            ]
        )
