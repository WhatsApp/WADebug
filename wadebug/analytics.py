# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from wadebug import exceptions
from wadebug.wa_actions import log_utils

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
    def send_report_to_fb(event, data, with_logs=False, phonenumber=None):
        postData = {
            'access_token': Analytics.CLIENT_TOKEN,
            'event_type': event,
            'event_data': data,
            'phone_number': phonenumber,
            'version': Analytics.VERSION,
        }

        try:
            if with_logs:
                filesParam = {
                    'logs_archive': (
                        'wadebug_logs.zip',
                        log_utils.prepare_logs(),
                        'application/zip'
                    )
                }
            else:
                filesParam = None

            res = requests.post(
                url=Analytics.API_ENDPOINT,
                data=postData,
                timeout=Analytics.TIMEOUT,
                files=filesParam
            ).json()
        except ValueError:
            raise ValueError('Invalid JSON response')
        except requests.exceptions.RequestException:
            raise exceptions.FBNetworkError('Network Error. Please ensure you can connect to www.facebook.com')

        if (res.get('error')):
            raise ValueError(pprint.pformat(res))

        return res.get('run_id')

    @staticmethod
    def send_logs_to_fb(phonenumber=None):
        return Analytics.send_report_to_fb(Events.SEND_LOGS, 'none', True, phonenumber)
