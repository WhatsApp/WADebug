#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug import results
from wadebug.wa_actions import docker_utils
from wadebug.wa_actions.base import WAAction


class CheckContainersAreUp(WAAction):
    user_facing_name = "containers_status"
    short_description = "Check if WA containers are running"

    @classmethod
    def _run(cls, config, *args, **kwargs):
        all_wa_containers = docker_utils.get_wa_containers()
        stopped_wa_container_ids = [
            wa_container.short_id
            for wa_container in all_wa_containers
            if not wa_container.is_running()
        ]

        remediation_msg = (
            "List all containers on the current host with `docker ps -a` and "
            "run `docker start #container_id` to start a container. "
            "If a container stops due to errors, "
            "refer to messages from other checks to diagnose or contact support "
            "https://developers.facebook.com/docs/whatsapp/contact-support"
        )

        if len(all_wa_containers) == len(stopped_wa_container_ids):
            return results.Problem(
                cls,
                "No WA container is running",
                "All WA containers are stopped.",
                remediation_msg,
            )

        if len(stopped_wa_container_ids) > 0:
            return results.Warning(
                cls,
                "Not all WA containers are running.",
                f"WA containers with id {', '.join(stopped_wa_container_ids)}"
                " not running.",
                f"If this is expected, please ignore. {remediation_msg}",
            )

        return results.OK(cls)
