# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from wadebug.wa_actions.base import WAAction
from wadebug import results
from wadebug.wa_actions.mysql_utils import MySQLUtil


class CheckMySQLConnection(WAAction):
    user_facing_name = 'check_mysql_connection'
    short_description = \
        'Test if MySQL database can be connected'
    config_dependencies = ('db.host', 'db.port', 'db.user', 'db.password')

    @classmethod
    def _run(cls, config, *args, **kwargs):
        try:
            mysql_utils = MySQLUtil(**config.get('db'))
            mysql_utils.try_connect()
            return results.OK(cls)
        except Exception as e:
            return results.Problem(cls, 'Unable to connect to db.', e, '')
