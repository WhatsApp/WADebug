# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import re

import pytest
from click.testing import CliRunner

from wadebug import wa_actions


@pytest.fixture
def runner():
    return CliRunner()


def test_user_facing_descriptions():
    actions = wa_actions.get_all_actions()
    for action in actions:
        result = re.search(r'[^\w_]', action.user_facing_name)
        assert not result, 'Action {} user_facing_name is invalid.\n' \
            'Use only letters and underscores.\nName found: {}'.format(
                action.__name__,
                action.user_facing_name
            )
    pass
