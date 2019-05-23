# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import traceback
import unittest

import pytest
from mock import patch
from wadebug import cli


class TestCli(unittest.TestCase):
    @patch("wadebug.cli.main", side_effect=Exception("something goes wrong!"))
    def test_cli_should_not_throw_by_default(self, mock_main):
        try:
            cli.safe_main()
        except Exception:
            pytest.fail(
                "cli.safe_main should not throw by default\n{}".format(
                    traceback.format_exc()
                )
            )

    @patch("wadebug.cli.main", side_effect=Exception("something goes wrong!"))
    @patch.dict(os.environ, {"WADEBUG_DEV_MODE": "True"})
    def test_cli_should_throw_in_dev_mode(self, mock_main):
        try:
            cli.safe_main()
            pytest.fail(
                "cli.safe_main should not throw by default\n{}".format(
                    traceback.format_exc()
                )
            )
        except Exception:
            pass
