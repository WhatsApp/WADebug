# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from wadebug.wa_actions.curl_utils import (
    CURLExitCode,
    CURLTestResult,
    __exec_request_from_container,
)


TEST_EXEC_PARAMS = ["test", "params"]


def test_request_should_return_non_http_ok_if_status_code_not_200(mocker):
    def mockreturn(command):
        return (CURLExitCode.OK, b"404:1")

    mock_container = MockContainer()
    mocker.patch.object(mock_container, "exec_run", mockreturn)
    result, response_time = __exec_request_from_container(
        mock_container, TEST_EXEC_PARAMS
    )
    assert result == CURLTestResult.HTTP_STATUS_NOT_OK


def test_request_should_return_ok_if_http_200_exit_code_0(mocker):
    def mockreturn(command):
        return (CURLExitCode.OK, b"200:1")

    mock_container = MockContainer()
    mocker.patch.object(mock_container, "exec_run", mockreturn)
    result, response_time = __exec_request_from_container(
        mock_container, TEST_EXEC_PARAMS
    )
    assert result == CURLTestResult.OK


def test_request_should_return_timeout_if_exit_code_28(mocker):
    def mockreturn(command):
        return (CURLExitCode.TIMEOUT, b"200:1")

    mock_container = MockContainer()
    mocker.patch.object(mock_container, "exec_run", mockreturn)
    result, response_time = __exec_request_from_container(
        mock_container, TEST_EXEC_PARAMS
    )
    assert result == CURLTestResult.CONNECTION_TIMEOUT


def test_request_should_return_cert_unknown_if_exit_code_60(mocker):
    def mockreturn(command):
        return (CURLExitCode.SSL_CERT_UNKNOWN, b"200:1")

    mock_container = MockContainer()
    mocker.patch.object(mock_container, "exec_run", mockreturn)
    result, response_time = __exec_request_from_container(
        mock_container, TEST_EXEC_PARAMS
    )
    assert result == CURLTestResult.SSL_CERT_UNKNOWN


class MockContainer:
    def exec_run():
        pass
