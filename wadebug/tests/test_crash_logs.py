# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import patch
from wadebug import results, wa_actions


class TestCrashLogs(unittest.TestCase):
    @patch(
        "wadebug.wa_actions.CheckContainersAreUp._run",
        side_effect=Exception("Uncaught exception on WAAction"),
    )
    def test_catch_unexpected_errors(self, mocked_call):
        """Make a WAAction crash and make sure wadebug can handle it gracefully."""
        try:
            result = wa_actions.CheckContainersAreUp.run({})
        except Exception as e:
            self.fail("WAAction.run() should never raise an exception:\n{}".format(e))

        assert mocked_call.call_count == 1
        assert isinstance(result, results.WADebugError)
