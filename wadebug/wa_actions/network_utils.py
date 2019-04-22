# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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


def hostname_reachable_from_container(container, hostname, port, timeout):
    try:
        exec_result = container.exec_run(
            ['nc', '-zv', hostname,
             str(port), '-w',
             str(timeout)])
        exit_code = exec_result[0]
        return exit_code == 0
    except Exception:
        return False


def hostname_not_reachable_from_container(container, hostname, port, timeout):
    return not hostname_reachable_from_container(container, hostname, port,
                                                 timeout)


# returns tuple (CURLTestResult, response time in secs)
def curl_test_url_from_container(container, webhook_url, timeout, ss_cert_path=None):
    exec_params = [
        'curl', str(webhook_url), '-s',  # remove progress bar
        '-o', '/dev/null',  # remove html output
        '-w', '%{http_code}:%{time_total}',  # output total req time
        '--connect-timeout', str(timeout)
    ]

    if ss_cert_path:
        exec_params.extend(['--cacert', ss_cert_path])
    try:
        exec_result = container.exec_run(exec_params)
        if ss_cert_path:
            container.exec_run(['rm', '-f', ss_cert_path])  # clean up cert from container
        exit_code = exec_result[0]  # https://ec.haxx.se/usingcurl-returns.html
        [http_code, response_time] = exec_result[1].decode().split(':')

        if exit_code == CURLExitCode.OK:
            if int(http_code) != 200:
                return [CURLTestResult.HTTP_STATUS_NOT_OK, None]
            return CURLTestResult.OK, float(response_time)
        elif exit_code == CURLExitCode.TIMEOUT:
            return CURLTestResult.CONNECTION_TIMEOUT, None
        elif exit_code == CURLExitCode.SSL_CERT_UNKNOWN:
            return CURLTestResult.SSL_CERT_UNKNOWN, None
    except Exception:
        pass

    return CURLTestResult.CONNECTION_ERROR, None
