# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pymysql.cursors


class MySQLUtil:
    def __init__(self, host='', port=0, user='', password=''):
        if host and port and user and password:
            self.db_host = host
            self.db_port = int(port)
            self.db_user = user
            self.db_password = password
        else:
            raise ValueError('Wrong input parameters')

    def create_connection(self):
        connection = pymysql.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            cursorclass=pymysql.cursors.DictCursor)
        return connection

    def try_connect(self):
        connection = self.create_connection()
        connection.close()

    def get_mysql_version(self):
        connection = self.create_connection()
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT version()")
            result = cursor.fetchone()
            return result['version()']
