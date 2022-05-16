# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from unittest.mock import patch

from wadebug.wa_actions import docker_utils
from wadebug.wa_actions.tests.stubs.mock_wa_container import (
    MockDockerContainer,
    MockStoppedWAContainer,
    MockWACoreappContainer,
    MockWAWebContainer,
)


class TestIsWAContainer(unittest.TestCase):
    def test_should_return_true_if_is_wa_container(self):
        assert docker_utils.is_wa_container(MockWACoreappContainer()) is True

    def test_should_return_false_if_is_not_wa_container(self):
        assert docker_utils.is_wa_container(MockDockerContainer()) is False


class TestGetWAContainers(unittest.TestCase):
    def test_should_only_return_wa_containers(self):
        mock_containers = [
            MockWACoreappContainer(),
            MockWAWebContainer(),
            MockDockerContainer(),
        ]

        with patch.object(
            docker_utils, "get_all_containers", return_value=mock_containers
        ):
            wa_containers = docker_utils.get_wa_containers()

            assert len(wa_containers) == 2, "Expected to get exactly 2 WA containers"
            assert (
                not mock_containers[2] in wa_containers
            ), "Non-WA containers should not be returned"


class TestGetRunningWAContainers:
    def test_should_only_return_running_containers(self):
        mock_containers = [
            MockWACoreappContainer(),
            MockStoppedWAContainer(),
            MockWAWebContainer(),
        ]

        with patch.object(
            docker_utils, "get_wa_containers", return_value=mock_containers
        ):
            running_wa_containers = docker_utils.get_running_wa_containers()

            assert (
                len(running_wa_containers) == 2
            ), "Expected exactly 2 containers to be running"
            assert (
                not mock_containers[1] in running_wa_containers
            ), "Non-running containers should not be returned"
