# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.analytics import Analytics
from wadebug.analytics import Events

from io import BytesIO


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data):
            self.json_data = json_data

        def json(self):
            return self.json_data

    return MockResponse({"run_id": "1234"})


def test_send_event(mocker):
    mocked_call = mocker.patch('requests.post', side_effect=mocked_requests_post)
    expected_post_data = {
        'access_token': Analytics.CLIENT_TOKEN,
        'event_type': Events.RUN_ACTIONS_AND_SEND_RESULTS,
        'event_data': "test_payload",
        'phone_number': None,
        'version': Analytics.VERSION,
    }
    run_id = Analytics.send_event(Events.RUN_ACTIONS_AND_SEND_RESULTS, "test_payload")
    assert mocked_call.call_count == 1
    mocked_call.assert_called_with(
        url=Analytics.API_ENDPOINT,
        data=expected_post_data,
        timeout=Analytics.TIMEOUT,
        files=None
    )
    assert run_id is not None


def test_send_logs_to_fb(mocker):
    mocked_call = mocker.patch('requests.post', side_effect=mocked_requests_post)
    dummy_log_file = BytesIO(b'not important')
    expected_post_data = {
        'access_token': Analytics.CLIENT_TOKEN,
        'event_type': Events.SEND_LOGS,
        'event_data': "none",
        'phone_number': None,
        'version': Analytics.VERSION,
    }
    expected_files_param = {
        'logs_archive': (
            'wadebug_logs.zip',
            dummy_log_file,
            'application/zip'
        )
    }
    run_id = Analytics.send_logs_to_fb(dummy_log_file)
    assert mocked_call.call_count == 1
    mocked_call.assert_called_with(
        url=Analytics.API_ENDPOINT,
        data=expected_post_data,
        timeout=Analytics.TIMEOUT,
        files=expected_files_param
    )
    assert run_id is not None
