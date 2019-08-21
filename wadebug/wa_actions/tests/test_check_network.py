# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import ANY, patch
from wadebug import results
from wadebug.wa_actions.implementations import check_network
from wadebug.wa_actions.implementations.check_network import (
    WA_SERVER_TYPE,
    docker_utils,
    network_utils,
)


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
    @patch.object(
        check_network,
        "get_hosts_not_reachable_from_container",
        return_value=[
            ("host1", WA_SERVER_TYPE.WA_SERVER),
            ("host2", WA_SERVER_TYPE.WA_REPOSITORY),
        ],
    )
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_at_least_one_host_not_reachable_on_https_port(
        self, mock_problem, *_
    ):
        check_network.CheckNetworkAction().run(config=None)
        mock_problem.assert_called_with(
            ANY,
            "Network connectivity check fails",
            "Cannot reach WhatsApp Server host1 on port 5222 or 443.\n"
            "Cannot reach WhatsApp Docker Repository host2 on port 5222 or 443.\n",
            ANY,
        )

    @patch.object(
        docker_utils, "get_running_wacore_containers", return_value=[MockContainer()]
    )
    @patch.object(
        check_network, "get_hosts_not_reachable_from_container", return_value=[]
    )
    @patch.object(results, "OK", autospec=True)
    def test_should_return_Ok_if_all_hosts_reachable(self, *_):
        check_network.CheckNetworkAction().run(config=None)

        results.OK.assert_called()

    @patch.object(
        check_network,
        "is_host_reachable_from_container",
        side_effect=[False, True, False],
    )
    def test_should_return_hosts_not_reachable(self, mock_call):
        mock_hosts = [
            ("host1", WA_SERVER_TYPE.WA_SERVER, "primary_port", "secondary_port"),
            ("host2", WA_SERVER_TYPE.WA_SERVER, "primary_port", "secondary_port"),
            ("host3", WA_SERVER_TYPE.WA_REPOSITORY, "primary_port", "secondary_port"),
        ]
        hosts_not_reachable = check_network.get_hosts_not_reachable_from_container(
            "container", mock_hosts
        )

        assert mock_call.call_count == len(mock_hosts)

        assert len(hosts_not_reachable) == 2
        assert ("host1", WA_SERVER_TYPE.WA_SERVER) in hosts_not_reachable
        assert ("host3", WA_SERVER_TYPE.WA_REPOSITORY) in hosts_not_reachable

    @patch.object(
        network_utils, "hostname_reachable_from_container", side_effect=[True, ANY]
    )
    def test_host_reachable_on_primary_port(self, mock_check):
        assert (
            check_network.is_host_reachable_from_container(
                "container", "host", "primary_port", "secondary_port"
            )
            is True
        )

        # only check primary port if reachable
        assert mock_check.call_count == 1

    @patch.object(
        network_utils, "hostname_reachable_from_container", side_effect=[False, True]
    )
    def test_host_reachable_on_secondary_port(self, mock_check):
        assert (
            check_network.is_host_reachable_from_container(
                "container", "host", "primary_port", "secondary_port"
            )
            is True
        )

        # check secondary port when not reachable on primary port
        assert mock_check.call_count == 2

    @patch.object(
        network_utils, "hostname_reachable_from_container", side_effect=[False, False]
    )
    def test_host_not_reachable_on_either_port(self, mock_check):
        assert (
            check_network.is_host_reachable_from_container(
                "container", "host", "primary_port", "secondary_port"
            )
            is False
        )

        # check secondary port when not reachable on primary port
        assert mock_check.call_count == 2
