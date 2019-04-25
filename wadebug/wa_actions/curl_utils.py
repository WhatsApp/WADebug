# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from enum import IntEnum


class CURLTestResult(IntEnum):
    OK = 1
    SSL_CERT_UNKNOWN = 2
    CONNECTION_ERROR = 3
    CONNECTION_TIMEOUT = 4
    HTTP_STATUS_NOT_OK = 5


class CURLExitCode(IntEnum):
    OK = 0
    TIMEOUT = 28
    SSL_CERT_UNKNOWN = 60


def https_get_request_from_container(container, url, timeout, ssl_cert_path=None):
    exec_params = __form_basic_exec_params(url, timeout)

    if ssl_cert_path:
        exec_params.extend(["--cacert", ssl_cert_path])

    return __exec_request_from_container(container, exec_params, ssl_cert_path)


def https_post_request_from_container(
    container, url, post_data_string, timeout, ssl_cert_path=None
):
    exec_params = __form_basic_exec_params(url, timeout)
    exec_params.extend(
        ["-X", "POST", "-d", post_data_string, "-H", "Content-Type: application/json"]
    )

    if ssl_cert_path:
        exec_params.extend(["--cacert", ssl_cert_path])

    return __exec_request_from_container(container, exec_params, ssl_cert_path)


def __form_basic_exec_params(url, timeout):
    return [
        "curl",
        str(url),
        "-s",  # remove progress bar
        "-o",
        "/dev/null",  # remove html output
        "-w",
        "%{http_code}:%{time_total}",  # output total req time
        "--connect-timeout",
        str(timeout),
    ]


# returns tuple (CURLTestResult, response time in secs)
def __exec_request_from_container(container, exec_params, ssl_cert_path=None):
    try:
        exec_result = container.exec_run(exec_params)

        exit_code = exec_result[0]  # https://ec.haxx.se/usingcurl-returns.html
        [http_code, response_time] = exec_result[1].decode().split(":")

        if exit_code == CURLExitCode.OK:
            if int(http_code) != 200:
                return [CURLTestResult.HTTP_STATUS_NOT_OK, None]
            return CURLTestResult.OK, float(response_time)
        elif exit_code == CURLExitCode.TIMEOUT:
            return CURLTestResult.CONNECTION_TIMEOUT, None
        elif exit_code == CURLExitCode.SSL_CERT_UNKNOWN:
            return CURLTestResult.SSL_CERT_UNKNOWN, None

        __clean_up_cert_file_from_container(container, ssl_cert_path)
    except Exception:
        pass

    return CURLTestResult.CONNECTION_ERROR, None


def __clean_up_cert_file_from_container(container, ssl_cert_path=None):
    if ssl_cert_path:
        try:
            container.exec_run(["rm", "-f", ssl_cert_path])
        except Exception:
            pass
