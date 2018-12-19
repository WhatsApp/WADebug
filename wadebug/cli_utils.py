# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.analytics import Analytics, Events

import json
import pkg_resources
import yaml

CONFIG_FILE = 'wadebug.conf.yml'


def get_config_from_file(config_file):
    with open(config_file, 'r') as f:
        config = yaml.load(f)
    return config


def create_default_config_file(sample_config_file_path):
    config_file_stream = pkg_resources.resource_string(__name__,
                                                       sample_config_file_path)

    with open(CONFIG_FILE, 'wb') as f:
        f.write(config_file_stream)


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
