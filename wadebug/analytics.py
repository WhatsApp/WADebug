# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from wadebug import exceptions

import pkg_resources
import pprint
import requests


class Events:
    RUN_ACTIONS = 'run_actions'
    RUN_ACTIONS_AND_SEND_RESULTS = 'run_actions_and_send_results'
    SEND_LOGS = 'send_logs'


class Analytics:
    API_ENDPOINT = 'https://graph.facebook.com/v3.1/wa_debug_logs'
    CLIENT_TOKEN = '260133211267543|a2471a9f36e4eaf6b9b79bb60b7887ee'
    TIMEOUT = 30
    VERSION = pkg_resources.get_distribution('wadebug').version

    @staticmethod
    def send_event(event, data, phone_number=None, files_param=None):
        postData = {
            'access_token': Analytics.CLIENT_TOKEN,
            'event_type': event,
            'event_data': data,
            'phone_number': phone_number,
            'version': Analytics.VERSION,
        }

        try:
            res = requests.post(
                url=Analytics.API_ENDPOINT,
                data=postData,
                timeout=Analytics.TIMEOUT,
                files=files_param,
            ).json()
        except ValueError:
            raise ValueError('Invalid JSON response')
        except requests.exceptions.RequestException:
            raise exceptions.FBNetworkError('Network Error. Please ensure you can connect to www.facebook.com')

        if res.get('error'):
            raise ValueError(pprint.pformat(res))

        return res.get('run_id')

    @staticmethod
    def send_logs_to_fb(zipped_logs_file_handle, phone_number=None):
        files_param = {
            'logs_archive': (
                'wadebug_logs.zip',
                zipped_logs_file_handle,
                'application/zip'
            )
        }
        return Analytics.send_event(
            Events.SEND_LOGS,
            data='none',
            files_param=files_param,
            phone_number=phone_number,
        )
