# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

from wadebug import results
from wadebug.wa_actions.base import WAAction
from wadebug.wa_actions.mysql_utils import MySQLUtil


PRIVILEGES = [
    "Select_priv",
    "Insert_priv",
    "Update_priv",
    "Delete_priv",
    "Create_priv",
    "Alter_priv",
    "Index_priv",
    "Drop_priv",
]
SUCCESS = "Y"


class CheckMySQLPermissions(WAAction):
    user_facing_name = "check_mysql_permissions"
    short_description = (
        "Test if the database have permissions to create database or tables"
    )
    config_dependencies = ("db.host", "db.port", "db.user", "db.password")

    @classmethod
    def _run(cls, config, *args, **kwargs):
        db_config = config.get("db")
        cur_user = db_config.get("user")

        errors = []
        remediation = """
Run MySQL command:
    GRANT ALL PRIVILEGES ON *.* TO \'{}\'@\'{}\'
to grant all privileges to the db user `{}` and rerun the checks.
        """.format(
            cur_user, db_config.get("host"), cur_user
        )

        try:
            mysql_utils = MySQLUtil(**db_config)
            result = mysql_utils.user_has_privileges(cur_user, PRIVILEGES)

            if not result:
                return results.Problem(
                    cls,
                    "Checking permissions returns empty result",
                    "User {} doesn't exist".format(cur_user),
                    "Make sure the correct db user is set in the config file",
                )

            for col in PRIVILEGES:
                if result[col] != SUCCESS:
                    errors.append(col)
        except Exception as e:
            return results.Problem(
                cls, "Unable to connect to db to check permisions", e, remediation
            )

        if errors:
            return results.Problem(
                cls,
                "Some required db permisions are missing",
                "Missing Permissions : {}".format(" , ".join(errors)),
                remediation,
            )

        return results.OK(cls)
