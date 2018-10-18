# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.wa_actions.base import WAAction
from wadebug import results
from wadebug.wa_actions import docker_utils

WEBAPP_PRIVATE_PORT = 443
WEBAPP_PRIVATE_PORT_PROTOCOL = 'tcp'


class CheckWebappPortAction(WAAction):
    user_facing_name = 'check_webapp_port'
    short_description = 'Check if webapp maps container port {} to host'.format(
        WEBAPP_PRIVATE_PORT)

    @classmethod
    def _run(cls, config, *args, **kwargs):
        running_waweb_containers = docker_utils.get_running_waweb_containers()

        short_error_message = 'Check webapp port failed'

        if not running_waweb_containers:
            return results.Problem(
                cls, short_error_message,
                'There is no waweb container running',
                'Please check results from other actions to diagnose')

        waweb_container = running_waweb_containers[0]
        port_bindings = docker_utils.get_container_port_bindings(
            waweb_container)

        for key in port_bindings:
            if key == '{}/{}'.format(WEBAPP_PRIVATE_PORT,
                                     WEBAPP_PRIVATE_PORT_PROTOCOL):
                return results.OK(cls)

        return results.Problem(
            cls, short_error_message,
            'Port {} inside the webapp container needs to be mapped to host'.
            format(WEBAPP_PRIVATE_PORT),
            'Please start the waweb container with port binding: \nports:\n\t- [Public Port]:{}"'.
            format(WEBAPP_PRIVATE_PORT))
