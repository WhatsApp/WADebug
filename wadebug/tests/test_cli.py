# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug import cli

import traceback
import pytest


def test_cli_should_not_throw_by_default(mocker):
    mock_exception = Exception('something goes wrong!')
    mocker.patch.object(cli, 'main', side_effect=mock_exception)

    try:
        cli.safe_main()
    except Exception:
        pytest.fail(
            'cli.safe_main should not throw by default\n{}'.format(traceback.format_exc()))


def test_cli_should_throw_in_dev_mode(mocker):
    mock_exception = Exception('something goes wrong!')
    mocker.patch.object(cli, 'main', side_effect=mock_exception)
    mocker.patch.dict('os.environ', {'WADEBUG_DEV_MODE': 'True'})

    with pytest.raises(Exception):
        cli.safe_main()
