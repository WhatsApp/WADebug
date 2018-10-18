# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import pytest

from wadebug import wa_actions
from wadebug import results


def test_catch_unexpected_errors(mocker):
    """Make a WAAction crash and make sure wadebug can handle it gracefully."""
    mocked_call = mocker.patch(
        'wadebug.wa_actions.CheckContainersAreUp._run',
        side_effect=Exception('Uncaught exception on WAAction'),
    )

    try:
        result = wa_actions.CheckContainersAreUp.run({})
    except Exception as e:
        pytest.fail('WAAction.run() should never raise an exception:\n{}'.format(e))

    assert mocked_call.call_count == 1
    assert isinstance(result, results.WADebugError)
