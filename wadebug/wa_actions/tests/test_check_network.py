# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import patch
from wadebug import results
from wadebug.wa_actions.implementations import check_network
from wadebug.wa_actions.implementations.check_network import docker_utils


class MockContainer:
    pass


class TestCheckNetwork(unittest.TestCase):
    @patch.object(docker_utils, "get_running_wacore_containers", return_value=[])
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_no_coreapp_running(self, *_):
        check_network.CheckNetworkAction().run(config=None)

        results.Problem.assert_called()

    @patch.object(
        docker_utils, "get_running_wacore_containers", return_value=[MockContainer()]
    )
    @patch.object(check_network, "is_server_in_warning_state", return_value=True)
    @patch.object(check_network, "is_server_in_error_state", return_value=False)
    @patch.object(results, "Warning", autospec=True)
    def test_should_return_warning_if_host_not_reachable_on_default_port(self, *_):
        check_network.CheckNetworkAction().run(config=None)

        results.Warning.assert_called()

    @patch.object(
        docker_utils, "get_running_wacore_containers", return_value=[MockContainer()]
    )
    @patch.object(check_network, "is_server_in_warning_state", return_value=True)
    @patch.object(
        check_network,
        "is_server_in_error_state",
        side_effect=[True, False, False, True, False, True],
    )
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_at_least_one_host_not_reachable_on_https_port(
        self, *_
    ):
        check_network.CheckNetworkAction().run(config=None)

        results.Problem.assert_called()

    @patch.object(
        docker_utils, "get_running_wacore_containers", return_value=[MockContainer()]
    )
    @patch.object(check_network, "is_server_in_warning_state", return_value=False)
    @patch.object(check_network, "is_server_in_error_state", return_value=False)
    @patch.object(results, "OK", autospec=True)
    def test_should_return_Ok_if_all_hosts_reachable(self, *_):
        check_network.CheckNetworkAction().run(config=None)

        results.OK.assert_called()
