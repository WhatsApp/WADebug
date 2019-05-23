# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import patch
from wadebug.wa_actions.curl_utils import (
    CURLExitCode,
    CURLTestResult,
    https_get_request_from_container,
)


class MockContainer:
    def exec_run(self):
        pass


mock_container = MockContainer()


class TestCurlUtils(unittest.TestCase):
    @patch.object(mock_container, "exec_run", return_value=(CURLExitCode.OK, b"404:1"))
    def test_request_should_return_non_http_ok_if_status_code_not_200(self, *_):
        result, response_time = https_get_request_from_container(
            mock_container, "url", "timeout"
        )
        assert result == CURLTestResult.HTTP_STATUS_NOT_OK

    @patch.object(mock_container, "exec_run", return_value=(CURLExitCode.OK, b"200:1"))
    def test_request_should_return_ok_if_http_200_exit_code_0(self, *_):
        result, response_time = https_get_request_from_container(
            mock_container, "url", "timeout"
        )
        assert result == CURLTestResult.OK

    @patch.object(
        mock_container, "exec_run", return_value=(CURLExitCode.TIMEOUT, b"200:1")
    )
    def test_request_should_return_timeout_if_exit_code_28(self, *_):
        result, response_time = https_get_request_from_container(
            mock_container, "url", "timeout"
        )
        assert result == CURLTestResult.CONNECTION_TIMEOUT

    @patch.object(
        mock_container,
        "exec_run",
        return_value=(CURLExitCode.SSL_CERT_UNKNOWN, b"200:1"),
    )
    def test_request_should_return_cert_unknown_if_exit_code_60(self, *_):
        result, response_time = https_get_request_from_container(
            mock_container, "url", "timeout"
        )
        assert result == CURLTestResult.SSL_CERT_UNKNOWN
