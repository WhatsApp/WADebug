# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from enum import Enum

from wadebug.wa_actions.base import WAAction
from wadebug import results

from wadebug.wa_actions import docker_utils
from wadebug.wa_actions import network_utils


class WA_SERVER_TYPE(Enum):
    WA_SERVER = 'WhatsApp Server'
    WA_REPOSITORY = 'WhatsApp Docker Repository'


DEFAULT_PORT = 5222
HTTPS_PORT = 443

HOSTS_USING_DEFAULT_PORT = [
    ('g.whatsapp.net', WA_SERVER_TYPE.WA_SERVER)
]

HOSTS_USING_HTTPS_PORT = [
    ('v.whatsapp.net', WA_SERVER_TYPE.WA_SERVER),
    ('mmg.whatsapp.net', WA_SERVER_TYPE.WA_SERVER),
    ('graph.facebook.com', WA_SERVER_TYPE.WA_SERVER),
    ('docker.whatsapp.biz', WA_SERVER_TYPE.WA_REPOSITORY),
    ('dt.bintray.com', WA_SERVER_TYPE.WA_REPOSITORY),
    ('akamai.bintray.com', WA_SERVER_TYPE.WA_REPOSITORY)
]

CONNECTION_TIMEOUT = 1


class CheckNetworkAction(WAAction):
    user_facing_name = 'check_network'
    short_description = \
        'Test if required hosts can be reached on specific port '\
        'from coreapp container.'

    @classmethod
    def _run(cls, config, *args, **kwargs):
        wacore_containers = docker_utils.get_running_wacore_containers()

        short_error_message = 'Network connectivity check fails'

        if not wacore_containers:
            return results.Problem(
                cls, short_error_message,
                'There is no wacore container running',
                'Please check results from other actions to diagnose'
            )

        container = wacore_containers[0]

        hosts_in_warning_state = []
        hosts_in_error_state = []

        for host in HOSTS_USING_DEFAULT_PORT:
            hostname = host[0]
            if is_server_in_warning_state(container, hostname):
                hosts_in_warning_state.append(host)
            elif is_server_in_error_state(container, hostname):
                hosts_in_error_state.append(host)

        for host in HOSTS_USING_HTTPS_PORT:
            hostname = host[0]
            if is_server_in_error_state(container, hostname):
                hosts_in_error_state.append(host)

        TROUBLESHOOTING_URL = \
            'https://developers.facebook.com/docs/whatsapp/network-debugging'

        if hosts_in_error_state:
            error_message = format_error_message(hosts_in_error_state) + \
                format_warning_message(hosts_in_warning_state)
            return results.Problem(
                cls, 'Network connectivity check fails', error_message,
                'Please refer to {} for network requirements details.'.format(
                    TROUBLESHOOTING_URL))

        if hosts_in_warning_state:
            warning_message = format_warning_message(hosts_in_warning_state)
            return results.Warning(
                cls, 'Network connectivity check fails', warning_message,
                'Please refer to {} for network requirements details.'.format(
                    TROUBLESHOOTING_URL))

        return results.OK(cls)


def is_server_in_warning_state(container, hostname):
    not_reachable_on_default_port = \
        network_utils.hostname_not_reachable_from_container(
            container, hostname, DEFAULT_PORT, CONNECTION_TIMEOUT)

    reachable_on_https_port = \
        network_utils.hostname_reachable_from_container(
            container, hostname, HTTPS_PORT, CONNECTION_TIMEOUT)

    return not_reachable_on_default_port and reachable_on_https_port


def is_server_in_error_state(container, hostname):
    not_reachable_on_https_port = \
        network_utils.hostname_not_reachable_from_container(
            container, hostname, HTTPS_PORT, CONNECTION_TIMEOUT)
    return not_reachable_on_https_port


def format_warning_message(hosts_in_warning_state):
    message = ''
    for hostname, server_type in hosts_in_warning_state:
        message += 'Warning: Cannot reach {} {} on port {}, using port {}.\n'\
            .format(server_type.value, hostname, DEFAULT_PORT, HTTPS_PORT)
    return message


def format_error_message(hosts_in_error_state):
    message = ''
    for hostname, server_type in hosts_in_error_state:
        message += 'Cannot reach {} {} on port {}.\n'\
            .format(server_type.value, hostname, DEFAULT_PORT, HTTPS_PORT)
    return message
