# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.analytics import Analytics, Events

import json


def send_results_to_fb(result, success_callback=None, failure_callback=None):
    try:
        event = Events.RUN_ACTIONS_AND_SEND_RESULTS
        data = json.dumps(result)

        run_id = Analytics.send_event(event, data)
        result['run_id'] = run_id

        if success_callback:
            success_callback(result)
    except Exception as e:
        if failure_callback:
            failure_callback(e)


def send_logs_to_fb(zipped_logs_file_handle, success_callback=None, failure_callback=None):
    try:
        run_id = Analytics.send_logs_to_fb(zipped_logs_file_handle)

        if success_callback:
            return success_callback(run_id)
    except Exception as e:
        if failure_callback:
            return failure_callback(e)
