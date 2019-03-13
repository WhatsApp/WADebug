# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from wadebug import exceptions

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import base64
import warnings
import requests


class WABizAPI:
    LOGIN_USER_ENDPOINT = '/v1/users/login'
    SUPPORT_INFO_ENDPOINT = '/v1/support'

    def __init__(self, **kwargs):
        baseUrl = kwargs.get('baseUrl')
        user = kwargs.get('user')
        password = kwargs.get('password')

        if baseUrl and user and password:
            self.api_baseUrl = baseUrl
            self.api_user = user
            self.api_password = password

            # suppress unverified https request warnings
            warnings.simplefilter('ignore', InsecureRequestWarning)
            self.api_header = self.__gen_req_header()
        else:
            raise ValueError('One or more required params (baseUrl, user, password) are missing.')

    def __gen_req_header(self):
        # encode(): string -> byte, to use in b64encode()
        # decode(): byte -> string, to use in header
        encoded = base64.b64encode('{}:{}'.format(self.api_user, self.api_password).encode()).decode()
        try:
            res = requests.post(
                url=urljoin(self.api_baseUrl, self.LOGIN_USER_ENDPOINT),
                headers={'AUTHORIZATION': 'Basic {}'.format(encoded)},
                verify=False,  # disable ssl verification
            )
            if res.status_code == 401:
                raise exceptions.WABizAuthError(
                    'API authentication error.  Please check your configuration file (wadebug.conf.yml '
                    'in current directory).'
                )

            res = res.json()
        except requests.exceptions.RequestException as e:
            raise exceptions.WABizNetworkError(
                'Network request error. Please check your configuration. (wadebug.conf.yml in current directory)'
                '\nDetails:{}'.format(e)
            )

        token = res['users'][0]['token']
        return {
            'AUTHORIZATION': 'Bearer {}'.format(token),
            'CONTENT_TYPE': 'application/json',
        }

    def get_support_info(self):
        try:
            res = requests.get(
                url=urljoin(self.api_baseUrl, self.SUPPORT_INFO_ENDPOINT),
                headers=self.api_header,
                verify=False,  # disable ssl verification
            )

            if res.status_code == 401:
                raise exceptions.WABizAuthError(
                    'API authentication error.  Please check your configuration.'
                )

            return res.json()
        except requests.exceptions.RequestException as e:
            raise exceptions.WABizNetworkError(
                'Network request error. Please check your configuration. \nDetails:{}'.format(e)
            )

    def get_phone_number(self):
        res = self.get_support_info()
        phone_number = res['support']['debug_info']
        if phone_number == 'unregistered':
            return None
        return phone_number
