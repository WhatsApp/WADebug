# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug import cli_utils
from wadebug.analytics import Analytics

from io import BytesIO


class TestSendResultsToFB:
    def test_should_append_run_id_to_result_if_succeed(self, mocker):
        mock_success_callback = mocker.Mock()
        mock_run_id = '1234abcd'
        mock_result = {'dummy_action': {'result': 'OK'}}

        mocker.patch.object(
            Analytics, 'send_event', return_value=mock_run_id)

        cli_utils.send_results_to_fb(mock_result, mock_success_callback)

        Analytics.send_event.assert_called()
        mock_success_callback.assert_called()
        assert mock_result['run_id'] == mock_run_id

    def test_should_call_failure_callback_with_exception(self, mocker):
        mock_exception = Exception('something goes wrong!')
        mock_failure_callback = mocker.Mock()
        mock_result = {'dummy_action': {'result': 'OK'}}

        mocker.patch.object(
            Analytics, 'send_event', side_effect=mock_exception)

        cli_utils.send_results_to_fb(
            mock_result, failure_callback=mock_failure_callback)

        mock_failure_callback.assert_called_with(mock_exception)


class TestSendLogsToFB:
    def test_should_call_success_callback_with_run_id(self, mocker):
        mock_success_callback = mocker.Mock()
        mock_run_id = '1234abcd'

        mocker.patch.object(
            Analytics, 'send_logs_to_fb', return_value=mock_run_id)

        dummy_zip_file = BytesIO(b'not important')

        cli_utils.send_logs_to_fb(dummy_zip_file, success_callback=mock_success_callback)

        Analytics.send_logs_to_fb.assert_called()
        mock_success_callback.assert_called_with(mock_run_id)

    def test_should_call_failure_callback_with_exception(self, mocker):
        mock_exception = Exception('something goes wrong!')
        mock_failure_callback = mocker.Mock()

        mocker.patch.object(
            Analytics, 'send_logs_to_fb', side_effect=mock_exception)

        dummy_zip_file = BytesIO(b'not important')

        cli_utils.send_logs_to_fb(dummy_zip_file, failure_callback=mock_failure_callback)

        mock_failure_callback.assert_called_with(mock_exception)
