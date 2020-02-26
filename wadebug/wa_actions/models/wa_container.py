#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


WA_WEB_CONTAINER_TAG = "whatsapp.biz/web"
WA_COREAPP_CONTAINER_TAG = "whatsapp.biz/coreapp"
MYSQL_CONTAINER_TAG = "mysql"


class WAContainer:
    def __init__(self, docker_container):
        self.container = docker_container

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self.container, attr)

    def is_coreapp(self):
        return (
            len(
                [
                    repo_tag
                    for repo_tag in self.image.attrs["RepoTags"]
                    if WA_COREAPP_CONTAINER_TAG in repo_tag
                ]
            )
            > 0
        )

    def is_webapp(self):
        return (
            len(
                [
                    repo_tag
                    for repo_tag in self.image.attrs["RepoTags"]
                    if WA_WEB_CONTAINER_TAG in repo_tag
                ]
            )
            > 0
        )

    def is_db(self):
        return (
            len(
                [
                    repo_tag
                    for repo_tag in self.image.attrs["RepoTags"]
                    if MYSQL_CONTAINER_TAG in repo_tag
                ]
            )
            > 0
        )

    def is_running(self):
        return self.status == "running"

    def get_container_type(self):
        if self.is_coreapp():
            return WA_COREAPP_CONTAINER_TAG
        elif self.is_webapp():
            return WA_WEB_CONTAINER_TAG
        else:
            return MYSQL_CONTAINER_TAG
