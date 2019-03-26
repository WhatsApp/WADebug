# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.analytics import Analytics, Events
from wadebug.config import Config
from wadebug.wa_actions.wabiz_api import WABizAPI

import json


def send_results_to_fb(result, success_callback=None, failure_callback=None):
    phone_number = None
    try:
        config = Config().values
        if config:
            api = WABizAPI(**config.get('webapp'))
            phone_number = api.get_phone_number()
    except Exception:
        pass

    try:
        event = Events.RUN_ACTIONS_AND_SEND_RESULTS
        data = json.dumps(result)

        run_id = Analytics.send_event(event, data, phone_number)
        result['run_id'] = run_id

        if success_callback:
            success_callback(result)
    except Exception as e:
        if failure_callback:
            failure_callback(e)


def send_logs_to_fb(zipped_logs_file_handle, success_callback=None, failure_callback=None):
    phone_number = None
    try:
        config = Config().values
        if config:
            api = WABizAPI(**config.get('webapp'))
            phone_number = api.get_phone_number()
    except Exception:
        pass

    try:
        run_id = Analytics.send_logs_to_fb(zipped_logs_file_handle, phone_number)

        if success_callback:
            return success_callback(run_id)
    except Exception as e:
        if failure_callback:
            return failure_callback(e)
