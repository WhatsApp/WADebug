# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import patch
from wadebug import results
from wadebug.wa_actions.implementations import check_webapp_port
from wadebug.wa_actions.implementations.check_webapp_port import docker_utils


class MockContainer:
    pass


class TestCheckWebappPort(unittest.TestCase):
    @patch.object(docker_utils, "get_running_waweb_containers", return_value=[])
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_no_waweb_running(self, *_):
        check_webapp_port.CheckWebappPortAction().run(config=None)

        results.Problem.assert_called()

    @patch.object(
        docker_utils, "get_running_waweb_containers", return_value=[MockContainer()]
    )
    @patch.object(docker_utils, "get_container_port_bindings", return_value={})
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_no_port_binding_for_443(self, *_):
        check_webapp_port.CheckWebappPortAction().run(config=None)

        results.Problem.assert_called()

    @patch.object(
        docker_utils, "get_running_waweb_containers", return_value=[MockContainer()]
    )
    @patch.object(
        docker_utils,
        "get_container_port_bindings",
        return_value={"443/tcp": "a valid host binding"},
    )
    @patch.object(results, "OK", autospec=True)
    def test_should_return_OK_if_port_443_has_host_binding(self, *_):
        check_webapp_port.CheckWebappPortAction().run(config=None)

        results.OK.assert_called()
