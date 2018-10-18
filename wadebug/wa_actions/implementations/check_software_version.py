# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
from wadebug.wa_actions.base import WAAction
from wadebug import results
from wadebug.wa_actions import docker_utils

from datetime import datetime


class CheckSoftwareVersion(WAAction):
    user_facing_name = 'check_software_version'
    short_description = \
        'Action to test whether software version is up-to-date'

    @classmethod
    def _run(cls, config, *args, **kwargs):
        errors = []
        warnings = []
        expiration_date_map = docker_utils.get_expiration_map()

        def get_all_running_wa_containers():
            wa_containers = docker_utils.get_wa_containers()
            versions_to_wa_containers_dict = defaultdict(lambda: defaultdict(list))
            for wa_container in wa_containers:
                container = wa_container.container
                container_type = wa_container.container_type
                if(docker_utils.is_container_running(container)):
                    if (docker_utils.WA_WEBAPP_CONTAINER_TAG == container_type or
                            docker_utils.WA_COREAPP_CONTAINER_TAG == container_type):
                        version = docker_utils.get_wa_version_from_container(container)
                        versions_to_wa_containers_dict[version][container_type].append(container)
            return versions_to_wa_containers_dict

        def is_valid_version(version, wa_containers_dict):
            containers = []
            for container in wa_containers_dict.values():
                containers.extend(container)
            valid_version = True
            cur = datetime.utcnow().strftime(docker_utils.DATE_FORMAT)
            try:
                days_delta = days_between(cur, expiration_date_map[version[0]])
                if days_delta < 0:
                    valid_version = False
                    error_str = '{}: Current version of your container {} has expired on {} UTC'
                    for container in containers:
                        errors.append(error_str.format(container.name, version[1], expiration_date_map[version[0]]))
                elif days_delta < 7:
                    warnings_str = '{}: Current version of your software ({}) is expiring on {} UTC, '
                    'please consider upgrading soon'
                    for container in containers:
                        warnings.append(warnings_str.format(container.name, version[1],
                                                            expiration_date_map[version[0]]))
            except KeyError:
                valid_version = False
                error_str = '{}: Current version of your container ({}) is not supported anymore or '
                'wadebug tool is not up-to-date'
                for container in containers:
                    errors.append(error_str.format(container.name, version[1]))
            return valid_version

        running_wa_containers = get_all_running_wa_containers()

        valid_versions = []
        for key, value in running_wa_containers.items():
            if(len(value[docker_utils.WA_COREAPP_CONTAINER_TAG]) != len(value[docker_utils.WA_WEBAPP_CONTAINER_TAG])):
                errors.append('Number of coreapp containers for version {} is not same as '
                              'number of webapp containers'.format(key))
            elif is_valid_version(key, value):
                valid_versions.append(key[1])

        if(len(valid_versions) > 1):
            warnings.append('More than one set of valid software versions({}) are running. '
                            'It may be fine, but worth noticing.'.format(valid_versions))

        if errors:
            error_str = 'Error Message: {}\n'
            warning_str = 'Warning Message: {}\n'

            return results.Problem(
                cls,
                'Some of your WhatsApp container versions are expired or there is mismatch between versions'
                ' of coreapp and webapp',
                '{}\n{}'.format('\n'.join([error_str.format(e) for e in errors]),
                                '\n'.join([warning_str.format(w) for w in warnings])),
                'Please find the following link to find latest version: '
                'https://developers.facebook.com/docs/whatsapp/changelog\n'
                'and please find upgrade instructions here:'
                'https://developers.facebook.com/docs/whatsapp/guides/installation\n',)

        if warnings:
            warning_str = 'Warning Message: {}\n'
            return results.Warning(
                cls,
                'Some of your WhatsApp conatiners are nearing expiration or '
                'more than one valid version is running',
                '\n'.join([warning_str.format(w) for w in warnings]),
                'Please find the following link to find latest version: '
                'https://developers.facebook.com/docs/whatsapp/changelog\n'
                'and please find upgrade instructions here:'
                'https://developers.facebook.com/docs/whatsapp/guides/installation\n',)

        return results.OK(cls)


def days_between(d1, d2):
    d1 = datetime.strptime(d1, docker_utils.DATE_FORMAT)
    d2 = datetime.strptime(d2, docker_utils.DATE_FORMAT)
    return (d2 - d1).days
