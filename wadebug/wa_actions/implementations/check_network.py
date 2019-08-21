# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

from enum import Enum

from wadebug import results
from wadebug.wa_actions import docker_utils, network_utils
from wadebug.wa_actions.base import WAAction


class WA_SERVER_TYPE(Enum):
    WA_SERVER = "WhatsApp Server"
    WA_REPOSITORY = "WhatsApp Docker Repository"


DEFAULT_PORT = 5222
HTTPS_PORT = 443

WHATSAPP_SERVERS = [
    ("g.whatsapp.net", WA_SERVER_TYPE.WA_SERVER, DEFAULT_PORT, HTTPS_PORT),
    ("v.whatsapp.net", WA_SERVER_TYPE.WA_SERVER, HTTPS_PORT, DEFAULT_PORT),
    ("mmg.whatsapp.net", WA_SERVER_TYPE.WA_SERVER, HTTPS_PORT, DEFAULT_PORT),
    ("graph.facebook.com", WA_SERVER_TYPE.WA_SERVER, HTTPS_PORT, DEFAULT_PORT),
    ("docker.whatsapp.biz", WA_SERVER_TYPE.WA_REPOSITORY, HTTPS_PORT, DEFAULT_PORT),
    ("dt.bintray.com", WA_SERVER_TYPE.WA_REPOSITORY, HTTPS_PORT, DEFAULT_PORT),
    ("akamai.bintray.com", WA_SERVER_TYPE.WA_REPOSITORY, HTTPS_PORT, DEFAULT_PORT),
]

CONNECTION_TIMEOUT = 1


class CheckNetworkAction(WAAction):
    user_facing_name = "check_network"
    short_description = (
        "Test if required hosts can be reached on specific port "
        "from coreapp container."
    )

    @classmethod
    def _run(cls, config, *args, **kwargs):
        wacore_containers = docker_utils.get_running_wacore_containers()

        short_error_message = "Network connectivity check fails"

        if not wacore_containers:
            return results.Problem(
                cls,
                short_error_message,
                "There is no wacore container running",
                "Please check results from other actions to diagnose",
            )

        container = wacore_containers[0]

        hosts_not_reachable = get_hosts_not_reachable_from_container(
            container, WHATSAPP_SERVERS
        )

        TROUBLESHOOTING_URL = (
            "https://developers.facebook.com/docs/whatsapp/network-debugging"
        )

        if hosts_not_reachable:
            error_message = format_error_message(hosts_not_reachable)
            return results.Problem(
                cls,
                "Network connectivity check fails",
                error_message,
                "Please refer to {} for network requirements details.".format(
                    TROUBLESHOOTING_URL
                ),
            )

        return results.OK(cls)


def get_hosts_not_reachable_from_container(container, hosts):
    hosts_not_reachable = []

    for host in hosts:
        hostname, server_type, primary_port, secondary_port = host
        if not is_host_reachable_from_container(
            container, hostname, primary_port, secondary_port
        ):
            hosts_not_reachable.append((hostname, server_type))

    return hosts_not_reachable


def is_host_reachable_from_container(container, hostname, primary_port, secondary_port):
    return network_utils.hostname_reachable_from_container(
        container, hostname, primary_port, CONNECTION_TIMEOUT
    ) or network_utils.hostname_reachable_from_container(
        container, hostname, secondary_port, CONNECTION_TIMEOUT
    )


def format_error_message(hosts):
    message = ""
    for hostname, server_type in hosts:
        # error message to users doesn't need to differentiate primary/secondary
        # ports for different hosts
        message += "Cannot reach {} {} on port {} or {}.\n".format(
            server_type.value, hostname, DEFAULT_PORT, HTTPS_PORT
        )
    return message
