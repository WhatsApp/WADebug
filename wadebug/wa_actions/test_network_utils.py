# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.wa_actions.network_utils import (
    hostname_reachable_from_container,
    curl_test_url_from_container,
    CURLTestResult,
    CURLExitCode,
)


def test_should_return_true_if_exit_code_is_0(mocker):
    def mockreturn(command):
        return (0, "a valid output")

    mock_container = MockContainer()
    mocker.patch.object(mock_container, 'exec_run', mockreturn)

    is_reachable = hostname_reachable_from_container(
        mock_container, "hostname", "port", "timeout")
    assert is_reachable


def test_should_return_false_if_exit_code_is_not_0(mocker):
    def mockreturn(command):
        return (1, "an invalid output")

    mock_container = MockContainer()
    mocker.patch.object(mock_container, 'exec_run', mockreturn)
    is_reachable = hostname_reachable_from_container(
        mock_container, "hostname", "port", "timeout")
    assert not is_reachable


def test_should_return_false_if_exec_throws(mocker):
    def mockreturn(command):
        raise
    mock_container = MockContainer()
    mocker.patch.object(mock_container, 'exec_run', mockreturn)
    is_reachable = hostname_reachable_from_container(
        mock_container, "hostname", "port", "timeout")
    assert not is_reachable


def test_curl_should_return_non_http_ok_if_status_code_not_200(mocker):
    def mockreturn(command):
        return (CURLExitCode.OK, b'404:1')
    mock_container = MockContainer()
    mocker.patch.object(mock_container, 'exec_run', mockreturn)
    result, response_time = curl_test_url_from_container(mock_container, 'webhook', 'timeout')
    assert result == CURLTestResult.HTTP_STATUS_NOT_OK


def test_curl_should_return_ok_if_http_200_exit_code_0(mocker):
    def mockreturn(command):
        return (CURLExitCode.OK, b'200:1')
    mock_container = MockContainer()
    mocker.patch.object(mock_container, 'exec_run', mockreturn)
    result, response_time = curl_test_url_from_container(mock_container, 'webhook', 'timeout')
    assert result == CURLTestResult.OK


def test_curl_should_return_timeout_if_exit_code_28(mocker):
    def mockreturn(command):
        return (CURLExitCode.TIMEOUT, b'200:1')
    mock_container = MockContainer()
    mocker.patch.object(mock_container, 'exec_run', mockreturn)
    result, response_time = curl_test_url_from_container(mock_container, 'webhook', 'timeout')
    assert result == CURLTestResult.CONNECTION_TIMEOUT


def test_curl_should_return_cert_unknown_if_exit_code_60(mocker):
    def mockreturn(command):
        return (CURLExitCode.SSL_CERT_UNKNOWN, b'200:1')
    mock_container = MockContainer()
    mocker.patch.object(mock_container, 'exec_run', mockreturn)
    result, response_time = curl_test_url_from_container(mock_container, 'webhook', 'timeout')
    assert result == CURLTestResult.SSL_CERT_UNKNOWN


class MockContainer:
    def exec_run():
        pass
