# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug import results
from wadebug.wa_actions.implementations import check_webapp_port
from wadebug.wa_actions.implementations.check_webapp_port import docker_utils


def test_should_return_problem_if_no_waweb_running(mocker):
    mocker.patch.object(
        docker_utils, 'get_running_waweb_containers', return_value=[])
    mocker.patch.object(results, 'Problem', autospec=True)

    check_webapp_port.CheckWebappPortAction().run(config=None)

    results.Problem.assert_called()


def test_should_return_problem_if_no_port_binding_for_443(mocker):
    mocker.patch.object(
        docker_utils,
        'get_running_waweb_containers',
        return_value=[MockContainer()])
    mocker.patch.object(
        docker_utils, 'get_container_port_bindings', return_value={})
    mocker.patch.object(results, 'Problem', autospec=True)

    check_webapp_port.CheckWebappPortAction().run(config=None)

    results.Problem.assert_called()


def test_should_return_OK_if_port_443_has_host_binding(mocker):
    mocker.patch.object(
        docker_utils,
        'get_running_waweb_containers',
        return_value=[MockContainer()])
    mocker.patch.object(
        docker_utils,
        'get_container_port_bindings',
        return_value={
            '443/tcp': 'a valid host binding'
        })
    mocker.patch.object(results, 'OK', autospec=True)

    check_webapp_port.CheckWebappPortAction().run(config=None)

    results.OK.assert_called()


class MockContainer:
    pass
