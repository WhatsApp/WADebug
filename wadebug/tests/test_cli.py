# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug import cli

import traceback

import pytest


def test_should_not_be_in_dev_mode(mocker):
    assert cli.DEVELOPMENT_MODE is False, 'cli.DEVELOPMENT_MODE should be False before commiting code'


def test_cli_should_not_throw(mocker, monkeypatch):
    mock_exception = Exception('something goes wrong!')
    mocker.patch.object(cli, 'main', side_effect=mock_exception)
    monkeypatch.setattr(cli, 'DEVELOPMENT_MODE', False)

    try:
        cli.safe_main()
    except Exception:
        pytest.fail(
            'cli.safe_main should never throw if cli.DEVELOPMENT_MODE == False\n{}'.format(traceback.format_exc()))


def test_cli_should_throw_in_dev_mode(mocker, monkeypatch):
    mock_exception = Exception('something goes wrong!')
    mocker.patch.object(cli, 'main', side_effect=mock_exception)
    monkeypatch.setattr(cli, 'DEVELOPMENT_MODE', True)

    with pytest.raises(Exception):
        cli.safe_main()
