# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import re
import unittest

from wadebug import wa_actions


class TestActions(unittest.TestCase):
    def test_user_facing_descriptions(self):
        actions = wa_actions.get_all_actions()
        for action in actions:
            result = re.search(r"[^\w_]", action.user_facing_name)
            assert not result, (
                "Action {} user_facing_name is invalid.\n"
                "Use only letters and underscores.\nName found: {}".format(
                    action.__name__, action.user_facing_name
                )
            )
        pass
