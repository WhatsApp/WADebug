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

INVALID_CHARACTERS = "?{}&~!()^="


class CheckMySQLPassword(WAAction):
    user_facing_name = 'check_mysql_password'
    short_description = \
        'Test if database password has any invalid characters'
    config_dependencies = ('db.password', )

    @classmethod
    def _run(cls, config, *args, **kwargs):
        errors = []
        wa_containers = docker_utils.get_running_wa_containers()
        if wa_containers:
            password = docker_utils.get_mysql_password(wa_containers[0])
        else:
            # if containers not giving password then get password from db config file
            password = config.get('db').get('password')

        if set(INVALID_CHARACTERS) & set(password):
            errors.append('Please make sure mysql password do not have any special characters from {}'
                          .format(INVALID_CHARACTERS))

        if errors:
            return results.Problem(
                cls,
                'Your mysql password contains some invalid characters',
                '\n'.join(errors),
                '',)
        return results.OK(cls)
