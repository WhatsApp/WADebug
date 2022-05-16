#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from unittest.mock import patch

from wadebug import results
from wadebug.wa_actions import docker_utils
from wadebug.wa_actions.implementations import check_containers
from wadebug.wa_actions.tests.stubs.mock_wa_container import (
    MockStoppedWAContainer,
    MockWACoreappContainer,
    MockWAWebContainer,
)


class TestCheckContainers(unittest.TestCase):
    @patch.object(docker_utils, "get_wa_containers")
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_when_no_wa_containers_running(
        self, mock_problem, mock_get_running_wa_containers
    ):
        mock_get_running_wa_containers.return_value = [
            MockStoppedWAContainer(),
            MockStoppedWAContainer(),
            MockStoppedWAContainer(),
        ]
        check_containers.CheckContainersAreUp()._run(None)

        mock_problem.assert_called()

    @patch.object(docker_utils, "get_wa_containers")
    @patch.object(results, "Warning", autospec=True)
    def test_should_return_warning_when_not_all_wa_containers_running(
        self, mock_warning, mock_get_wa_containers
    ):
        mock_get_wa_containers.return_value = [
            MockWACoreappContainer(),
            MockWAWebContainer(),
            MockStoppedWAContainer(),
        ]
        check_containers.CheckContainersAreUp()._run(None)

        mock_warning.assert_called()
