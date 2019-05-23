# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
from io import BytesIO

from mock import Mock, patch
from wadebug import cli_utils
from wadebug.analytics import Analytics


class TestSendResultsToFB(unittest.TestCase):
    def test_should_append_run_id_to_result_if_succeed(self):
        mock_success_callback = Mock()
        mock_run_id = "1234abcd"
        mock_result = {"dummy_action": {"result": "OK"}}

        with patch.object(Analytics, "send_event", return_value=mock_run_id):
            cli_utils.send_results_to_fb(mock_result, mock_success_callback)

            Analytics.send_event.assert_called()
            mock_success_callback.assert_called()
            assert mock_result["run_id"] == mock_run_id

    def test_should_call_failure_callback_with_exception(self):
        mock_failure_callback = Mock()
        mock_result = {"dummy_action": {"result": "OK"}}
        mock_exception = Exception("something goes wrong!")

        with patch.object(Analytics, "send_event", side_effect=mock_exception):
            cli_utils.send_results_to_fb(
                mock_result, failure_callback=mock_failure_callback
            )

            mock_failure_callback.assert_called_with(mock_exception)


class TestSendLogsToFB(unittest.TestCase):
    def test_should_call_success_callback_with_run_id(self):
        mock_success_callback = Mock()
        mock_run_id = "1234abcd"
        dummy_zip_file = BytesIO(b"not important")

        with patch.object(Analytics, "send_logs_to_fb", return_value=mock_run_id):
            cli_utils.send_logs_to_fb(
                dummy_zip_file, success_callback=mock_success_callback
            )

            Analytics.send_logs_to_fb.assert_called()
            mock_success_callback.assert_called_with(mock_run_id)

    def test_should_call_failure_callback_with_exception(self):
        mock_failure_callback = Mock()
        mock_exception = Exception("something goes wrong!")
        dummy_zip_file = BytesIO(b"not important")

        with patch.object(Analytics, "send_logs_to_fb", side_effect=mock_exception):
            cli_utils.send_logs_to_fb(
                dummy_zip_file, failure_callback=mock_failure_callback
            )

            mock_failure_callback.assert_called_with(mock_exception)
