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


class CheckContainersAreUp(WAAction):
    user_facing_name = 'containers_status'
    short_description = \
        'Action to test whether containers are running'

    @classmethod
    def _run(cls, config, *args, **kwargs):

        stopped_containers = []
        stopped_sql_containers = []

        def get_all_running_wa_containers():
            containers = docker_utils.get_wa_containers()
            versions_to_wa_containers_dict = defaultdict(lambda: defaultdict(list))
            for wa_container in containers:
                container = wa_container.container
                container_type = wa_container.container_type
                if(docker_utils.is_container_running(container)):
                    if (docker_utils.WA_WEBAPP_CONTAINER_TAG == container_type or
                            docker_utils.WA_COREAPP_CONTAINER_TAG == container_type):
                        version = docker_utils.get_wa_version_from_container(container)
                        versions_to_wa_containers_dict[version[1]][container_type].append(container)
                else:
                    if docker_utils.MYSQL_CONTAINER_TAG == container_type:
                        stopped_sql_containers.append(container)
                    else:
                        stopped_containers.append(container)
            return versions_to_wa_containers_dict

        errors = []
        warnings = []

        running_wa_containers = get_all_running_wa_containers()
        if not running_wa_containers:
            errors.append("Either core container or web container is missing")
        no_of_working_versions = 0
        for key, value in running_wa_containers.items():
            if(len(value) != 2):
                errors.append("Either web container or core container missing for version {}".format(key))
            elif(len(value[docker_utils.WA_COREAPP_CONTAINER_TAG]) != len(value[docker_utils.WA_WEBAPP_CONTAINER_TAG])):
                errors.append('The number of running coreapp containers, for version {}, is not'
                              'same as number of running web containers'.format(key))
            else:
                no_of_working_versions = no_of_working_versions + 1
                if(no_of_working_versions > 1):
                    warnings.append('More than one set of Web app and Core app are running. '
                                    'It may be fine, but worth noticing.')

        if errors or stopped_sql_containers:
            err_str = 'Message: {}\n'
            container_details = "Container - ID: {}, Name: {}, Status: {}"
            stopped_containers.extend(stopped_sql_containers)
            return results.Problem(
                cls,
                'Some of your WhatsApp containers are missing or not running.',
                '{}\n{}'.format('\n'.join([err_str.format(e) for e in errors]),
                                '\n'.join([container_details.format
                                           (c.short_id, c.name, c.status) for c in stopped_containers])),
                'Use the following commands to learn more:\n'
                '\tdocker ps -a\n'
                '\tdocker inspect <CONTAINER_ID>',)

        if warnings:
            warning_str = 'Message: {}\n'
            return results.Warning(
                cls,
                'More than one set(coreapp,webapp) of containers are running',
                '\n'.join([warning_str.format(w) for w in warnings]),
                'Use the following commands to learn more:\n'
                '\tdocker ps -a\n')

        return results.OK(cls)
