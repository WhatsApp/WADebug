# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import patch
from wadebug.wa_actions.network_utils import hostname_reachable_from_container


class MockContainer:
    def exec_run(self):
        pass


class TestNetworkUtils(unittest.TestCase):
    def test_should_return_true_if_exit_code_is_0(self):
        def mockreturn(command):
            return (0, "a valid output")

        mock_container = MockContainer()
        with patch.object(mock_container, "exec_run", mockreturn):
            is_reachable = hostname_reachable_from_container(
                mock_container, "hostname", "port", "timeout"
            )
            assert is_reachable

    def test_should_return_false_if_exit_code_is_not_0(self):
        def mockreturn(command):
            return (1, "an invalid output")

        mock_container = MockContainer()
        with patch.object(mock_container, "exec_run", mockreturn):
            is_reachable = hostname_reachable_from_container(
                mock_container, "hostname", "port", "timeout"
            )
            assert not is_reachable

    def test_should_return_false_if_exec_throws(self):
        def mockreturn(command):
            raise

        mock_container = MockContainer()
        with patch.object(mock_container, "exec_run", mockreturn):
            is_reachable = hostname_reachable_from_container(
                mock_container, "hostname", "port", "timeout"
            )
            assert not is_reachable
