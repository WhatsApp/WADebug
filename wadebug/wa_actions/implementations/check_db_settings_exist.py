# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from wadebug.wa_actions.base import WAAction
from wadebug import results
from wadebug.wa_actions import docker_utils
from collections import defaultdict

DB_SETTINGS_CONTAINER = ['WA_DB_ENGINE', 'WA_DB_HOSTNAME', 'WA_DB_PORT', 'WA_DB_USERNAME', 'WA_DB_PASSWORD']


class CheckDbSettingsExist(WAAction):
    user_facing_name = 'check_db_settings_exist'
    short_description = \
        'Test if required db settings are passed'

    @classmethod
    def _run(cls, config, *args, **kwargs):
        errors = defaultdict(list)
        containers = docker_utils.get_all_running_wa_containers_except_db()

        for container in containers:
            for item in DB_SETTINGS_CONTAINER:
                value = docker_utils.get_value_by_inspecting_container_environment(container, item)
                if not value:
                    errors[container.name].append(item)

        if errors:
            err_str = 'For container {}, missing the required database settings : {}'
            return results.Problem(
                cls,
                'Some required db settings are not passed',
                '\n'.join([err_str.format(key, value) for key, value in errors.items()]),
                'Pleaes make sure to pass required db configuration',)
        return results.OK(cls)
