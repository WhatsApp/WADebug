# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.wa_actions.network_utils import (
    hostname_reachable_from_container
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


class MockContainer:
    def exec_run():
        pass
