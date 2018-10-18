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
from distutils.version import LooseVersion

MIN_MYSQL_VERSION = LooseVersion('5.7')
MAX_MYSQL_VERSION = LooseVersion('8')


class CheckMySQLVersion(WAAction):
    user_facing_name = 'check_mysql_version'
    short_description = \
        'Check MySQL version'
    config_dependencies = ('db.host', 'db.port', 'db.user', 'db.password')

    @classmethod
    def _run(cls, config, *args, **kwargs):
        try:
            mysql_utils = MySQLUtil(**config.get('db'))
            mysql_version = mysql_utils.get_mysql_version()
            if is_version_valid(mysql_version):
                return results.OK(cls)
            else:
                error_message = 'Please make sure MySQL version is higher than 5.7.xx but NOT version 8. '
                'Refer to https://developers.facebook.com/docs/whatsapp/guides/installation for more details'
                return results.Problem(
                    cls,
                    'You are using an unsupported version of MySQL',
                    error_message, '')
        except Exception as e:
            return results.Problem(cls, 'Unable to connect to db', e, '')


def is_version_valid(version):
    semver = LooseVersion(version)
    return (semver >= MIN_MYSQL_VERSION and semver < MAX_MYSQL_VERSION)
