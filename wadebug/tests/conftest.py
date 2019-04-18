# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import pytest
from wadebug.config import Singleton


@pytest.fixture(autouse=True)
def reset_singletons():
    Singleton._instances = {}
