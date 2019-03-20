# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug import cli

import traceback

import pytest


def test_cli_should_not_throw(mocker):
    mock_exception = Exception('something goes wrong!')
    mocker.patch.object(cli, 'main', side_effect=mock_exception)
    mocker.patch('wadebug.config.Config._development_mode', False)

    try:
        cli.safe_main()
    except Exception:
        pytest.fail(
            'cli.safe_main should never throw if Config().development_mode == False\n{}'.format(traceback.format_exc()))


def test_cli_should_throw_in_dev_mode(mocker):
    mock_exception = Exception('something goes wrong!')
    mocker.patch.object(cli, 'main', side_effect=mock_exception)
    mocker.patch('wadebug.config.Config._development_mode', True)

    with pytest.raises(Exception):
        cli.safe_main()
