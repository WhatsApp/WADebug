# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug import results
from wadebug.wa_actions.implementations import check_network
from wadebug.wa_actions.implementations.check_network import docker_utils


def test_should_return_problem_if_no_coreapp_running(mocker):
    mocker.patch.object(
        docker_utils, 'get_running_wacore_containers', return_value=[])
    mocker.patch.object(results, 'Problem', autospec=True)

    check_network.CheckNetworkAction().run(config=None)

    results.Problem.assert_called()


def test_should_return_warning_if_host_not_reachable_on_default_port(mocker):
    mocker.patch.object(
        docker_utils,
        'get_running_wacore_containers',
        return_value=[MockContainer()])
    mocker.patch.object(
        check_network, 'is_server_in_warning_state', return_value=True)
    mocker.patch.object(
        check_network, 'is_server_in_error_state', return_value=False)
    mocker.patch.object(results, 'Warning', autospec=True)

    check_network.CheckNetworkAction().run(config=None)

    results.Warning.assert_called()


def test_should_return_problem_if_at_least_one_host_not_reachable_on_https_port(
        mocker):
    mocker.patch.object(
        docker_utils,
        'get_running_wacore_containers',
        return_value=[MockContainer()])
    mocker.patch.object(
        check_network, 'is_server_in_warning_state', return_value=True)
    mocker.patch.object(
        check_network,
        'is_server_in_error_state',
        side_effect=[True, False, False, True, False, True])
    mocker.patch.object(results, 'Problem', autospec=True)

    check_network.CheckNetworkAction().run(config=None)

    results.Problem.assert_called()


def test_should_return_Ok_if_all_hosts_reachable(mocker):
    mocker.patch.object(
        docker_utils,
        'get_running_wacore_containers',
        return_value=[MockContainer()])
    mocker.patch.object(
        check_network, 'is_server_in_warning_state', return_value=False)
    mocker.patch.object(
        check_network, 'is_server_in_error_state', return_value=False)
    mocker.patch.object(results, 'OK', autospec=True)

    check_network.CheckNetworkAction().run(config=None)

    results.OK.assert_called()


class MockContainer:
    pass
