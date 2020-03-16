#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mock import Mock
from wadebug.wa_actions.models.wa_container import (
    WA_COREAPP_CONTAINER_TAG,
    WA_WEB_CONTAINER_TAG,
    WAContainer,
)


class MockDockerImage:
    def __init__(self, repo_tags):
        self.attrs = {"RepoTags": repo_tags}


class MockDockerContainer:
    def __init__(self, name="MockContainer", repo_tags=None, status="running"):
        self.name = name
        self.image = MockDockerImage(repo_tags if repo_tags else [])
        self.status = status

    def __getattr__(self, attr):
        if attr in ["short_id"]:
            return ""
        return Mock()


class MockWACoreappContainer(WAContainer):
    def __init__(self):
        WAContainer.__init__(self, MockDockerContainer("", [WA_COREAPP_CONTAINER_TAG]))


class MockWAWebContainer(WAContainer):
    def __init__(self):
        WAContainer.__init__(self, MockDockerContainer("", [WA_WEB_CONTAINER_TAG]))


class MockStoppedWAContainer(WAContainer):
    def __init__(self):
        WAContainer.__init__(
            self, MockDockerContainer("", [WA_WEB_CONTAINER_TAG], "stopped")
        )
