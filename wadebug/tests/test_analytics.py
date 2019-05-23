# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
from io import BytesIO

from mock import patch
from wadebug.analytics import Analytics, Events


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data):
            self.json_data = json_data

        def json(self):
            return self.json_data

    return MockResponse({"run_id": "1234"})


class TestAnalytics(unittest.TestCase):
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_send_event(self, mock_request_post):
        expected_post_data = {
            "access_token": Analytics.CLIENT_TOKEN,
            "event_type": Events.RUN_ACTIONS_AND_SEND_RESULTS,
            "event_data": "test_payload",
            "phone_number": None,
            "version": Analytics.VERSION,
        }
        run_id = Analytics.send_event(
            Events.RUN_ACTIONS_AND_SEND_RESULTS, "test_payload"
        )
        assert mock_request_post.call_count == 1
        mock_request_post.assert_called_with(
            url=Analytics.API_ENDPOINT,
            data=expected_post_data,
            timeout=Analytics.TIMEOUT,
            files=None,
        )
        assert run_id is not None

    @patch("requests.post", side_effect=mocked_requests_post)
    def test_send_logs_to_fb(self, mock_request_post):
        dummy_log_file = BytesIO(b"not important")
        expected_post_data = {
            "access_token": Analytics.CLIENT_TOKEN,
            "event_type": Events.SEND_LOGS,
            "event_data": "none",
            "phone_number": None,
            "version": Analytics.VERSION,
        }
        expected_files_param = {
            "logs_archive": ("wadebug_logs.zip", dummy_log_file, "application/zip")
        }
        run_id = Analytics.send_logs_to_fb(dummy_log_file)
        assert mock_request_post.call_count == 1
        mock_request_post.assert_called_with(
            url=Analytics.API_ENDPOINT,
            data=expected_post_data,
            timeout=Analytics.TIMEOUT,
            files=expected_files_param,
        )
        assert run_id is not None
