# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug import exceptions
from wadebug.wa_actions import docker_utils

import docker
import errno
import json
import shutil
import os


OUTPUT_FOLDER = 'wadebug_logs'
WEB_LOG_PATH = '/var/log/whatsapp'
WEB_LOG_FILE = 'web.log'
WEB_ERROR_LOG_PATH = '/var/log/lighttpd'
WEB_ERROR_LOG_FILE = 'error.log'


def prepare_logs():
    check_access()
    get_logs()
    path = os.path.join(os.getcwd(), 'wadebug_logs/')
    shutil.make_archive('wadebug_logs', 'zip', path)
    return open(os.path.join(os.getcwd(), 'wadebug_logs.zip'), 'rb')


def check_access():
    try:
        if(os.access(os.getcwd(), os.R_OK)):
            os.makedirs(os.path.join(os.getcwd(), OUTPUT_FOLDER))
        else:
            raise exceptions.FileAccessError('Access error:  Cannot read from current directory')

    except OSError as e:
        if e.errno != errno.EEXIST:
            raise exceptions.FileAccessError('Access error:  Cannot write logs to current directory')


def get_logs():
    wa_containers = docker_utils.get_wa_containers()
    errors = []
    for wa_container in wa_containers:
        container = wa_container.container
        container_type = wa_container.container_type
        try:
            container_logs = docker_utils.get_container_logs(container)
            docker_utils.write_to_file_in_binary(
                os.path.join(OUTPUT_FOLDER, '{}-container.log'.format(container.name)), container_logs)
            inspect_result = docker_utils.get_inspect_result(container)
            docker_utils.write_to_file(
                os.path.join(OUTPUT_FOLDER, '{}-inspect.log'.format(container.name)),
                json.dumps(inspect_result, indent=1),
            )
            if docker_utils.WA_WEBAPP_CONTAINER_TAG == container_type:
                copy_additional_logs_for_webcontainer(container, WEB_LOG_PATH, WEB_LOG_FILE)
                copy_additional_logs_for_webcontainer(container, WEB_ERROR_LOG_PATH, WEB_ERROR_LOG_PATH)
        except Exception as e:
            print(e)
            errors.append((container, e))

    if errors:
        err_str = 'Container: {}\nException: {}'
        exception_msg = 'Some logs could not be obtained:\n{}'.format(
            '\n'.join([err_str.format(err[0].name, err) for err in errors])
        )
        raise exceptions.LogsNotCompleteError(exception_msg)


def copy_additional_logs_for_webcontainer(container, path, file_name):
    try:
        logs = docker_utils.get_archive_from_container(container, path, file_name)
        path = os.path.join(OUTPUT_FOLDER, '{}-{}'.format(container.name, file_name))
        docker_utils.write_to_file(path, logs)
    except (KeyError, docker.errors.NotFound):
        pass
