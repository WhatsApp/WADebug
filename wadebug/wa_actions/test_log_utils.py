# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug import exceptions
from wadebug.wa_actions import docker_utils
from wadebug.wa_actions import log_utils


def test_should_makedir_if_have_access(mocker):
    mocker.patch('os.access', return_value=True)
    mocked_makedirs_call = mocker.patch('os.makedirs', return_value=True)

    log_utils.check_access()

    assert mocked_makedirs_call.call_count == 1


def test_should_return_true_if_get_logs_has_no_exceptions(mocker):
    mock_containers = [
        docker_utils.WAContainer(MockContainer(), 'container_type'),
        docker_utils.WAContainer(MockContainer(), 'container_type'),
    ]
    mocker.patch.object(
        docker_utils, 'get_wa_containers', return_value=mock_containers
    )
    mocker.patch.object(
        docker_utils, 'get_container_logs', return_value='Fake container logs'
    )
    mocker.patch.object(
        docker_utils, 'get_inspect_result', return_value='Fake inspect results'
    )
    mocker.patch.object(
        docker_utils, 'write_to_file_in_binary', return_value=None
    )
    mocker.patch.object(
        docker_utils, 'write_to_file', return_value=None
    )

    try:
        log_utils.get_logs()
        assert True
    except exceptions.LogsNotCompleteError:
        assert False


def test_should_write_webcontainer_log_to_file(mocker):
    mock_container = MockContainer()
    mocker.patch.object(
        docker_utils, 'get_archive_from_container', return_value='Mock logs'
    )
    mocked_write_call = mocker.patch.object(
        docker_utils, 'write_to_file', return_value=None
    )

    log_utils.copy_additional_logs_for_webcontainer(mock_container, 'mock path', 'mock file name')
    assert mocked_write_call.call_count == 1


class MockContainer:
    def __init__(self):
        self.name = 'MockContainer'
