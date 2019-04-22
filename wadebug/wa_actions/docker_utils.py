# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from datetime import datetime
from datetime import timedelta
from enum import Enum
from six import BytesIO

import tempfile
import tarfile
import docker
import os

WA_WEBAPP_CONTAINER_TAG = 'whatsapp.biz/web'
WA_COREAPP_CONTAINER_TAG = 'whatsapp.biz/coreapp'
MYSQL_CONTAINER_TAG = 'mysql'
CONTAINER_RUNNING = 'running'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
EXPIRED_DATE_FORMAT = '%Y-%m-%d'
LIFETIME_OF_BETA_BUILD_IN_DAYS = 45
LIFETIME_OF_BUILD_IN_DAYS = 180
MAX_LINE_OF_LOGS = 10000
TEMP_TAR_FILENAME = 'temp.tar'


def get_all_containers():
    client = docker.from_env()
    return client.containers.list(all=True)


def get_container_logs(container):
    return container.logs(tail=MAX_LINE_OF_LOGS)


def get_inspect_result(container):
    client = docker.from_env()
    res = client.api.inspect_container(container.short_id)
    # hide password
    for index, value in enumerate(res['Config']['Env']):
        if value.lower().find("password") != -1:
            arr = value.split('=')
            res['Config']['Env'][index] = arr[0] + '*******'
    return res


def get_core_dump_logs(container):
    client = docker.from_env()
    files_changed = client.api.diff(container.short_id)
    coredump_logs = []
    for file_change in files_changed:
        file_change_type = file_change['Kind']
        full_path = file_change['Path']
        # the crash files should have names like:
        # /usr/local/waent/logs/wa-service-bffb11a7-crash.log
        if (
            '-crash.log' in full_path
            and file_change_type != DockerDiffFileChange.DELETED
        ):
            folder_path, file_name = full_path.rsplit('/', 1)
            coredump = get_archive_from_container(container, folder_path, file_name)
            coredump_logs.append(coredump)
    result = '\n'.join(coredump_logs)
    return result


def get_archive_from_container(container, path, file_name):
    with tempfile.NamedTemporaryFile() as destination:
        stream, stat = container.get_archive(os.path.join(path, file_name))
        for data in stream:
            destination.write(data)
        destination.seek(0)
        retrieved_data = untar_file(destination, file_name)
        retrieved_data = retrieved_data.decode('utf-8')
        return retrieved_data


# https://docker-py.readthedocs.io/en/1.5.0/api/#get_archive
# 'docker sdk' for get-archive returns tuple. In which, first element is a raw tar data stream.
# We should untar this file to read content.
# The reason it gives tar file is path to get_archive() can be a folder instead of just a file
def untar_file(tardata, file_name):
    with tarfile.open(mode='r', fileobj=tardata) as t:
        f = t.extractfile(file_name)
        result = f.read()
        f.close()
    return result


def put_archive_to_container(container, src, dest):
    with tempfile.NamedTemporaryFile() as temptar:  # tempfile backed tarfile
        file_data = open(src, 'rb').read()
        tar_file = tarfile.open(fileobj=temptar, mode='w')
        tarinfo = tarfile.TarInfo(name=os.path.basename(src))
        tarinfo.size = os.stat(src).st_size
        tar_file.addfile(tarinfo, BytesIO(file_data))
        tar_file.close()
        temptar.flush()
        temptar.seek(0)
        container.put_archive(dest, temptar.read())


def write_to_file_in_binary(path, content):
    with open(path, 'wb') as file:
        file.write(content)
        file.close()


def write_to_file(path, content):
    with open(path, 'w') as file:
        file.write(content)
        file.close()


def get_wa_version_from_container(container):
    return get_version(container.image.attrs['RepoTags'][0].split(':')[1])


def get_running_wacore_containers():
    return get_running_wa_containers_by_type(WA_COREAPP_CONTAINER_TAG)


def get_running_waweb_containers():
    return get_running_wa_containers_by_type(WA_WEBAPP_CONTAINER_TAG)


def get_running_wa_containers_by_type(type_to_match):
    return [
        c.container for c in get_running_wa_containers()
        if c.container_type == type_to_match
    ]


def get_running_wa_containers():
    return [
        c for c in get_wa_containers() if is_container_running(c.container)
    ]


def get_wa_containers():
    """Return all probably relevant containers, including MySQL, if exists."""
    return [
        WAContainer(c, get_wa_container_type(c)) for c in get_all_containers()
        if get_wa_container_type(c)
    ]


def get_wa_container_type(container):
    for repo_tag in container.image.attrs['RepoTags']:
        if repo_tag.find(WA_WEBAPP_CONTAINER_TAG) > -1:
            return WA_WEBAPP_CONTAINER_TAG
        if repo_tag.find(WA_COREAPP_CONTAINER_TAG) > -1:
            return WA_COREAPP_CONTAINER_TAG
        if repo_tag.find(MYSQL_CONTAINER_TAG) > -1:
            return MYSQL_CONTAINER_TAG
    return None


def is_container_running(container):
    return container.status == CONTAINER_RUNNING


def get_all_running_wa_containers_except_db():
    return [
        c.container for c in get_running_wa_containers()
        if c.container_type != MYSQL_CONTAINER_TAG
    ]


def get_mysql_password(wa_container):
    client = docker.from_env()
    res = client.api.inspect_container(wa_container.container.short_id)
    for _, value in enumerate(res['Config']['Env']):
        if value.find("MYSQL_ROOT_PASSWORD") != -1:
            arr = value.split('=')
            return arr[1]
    return ""


def get_value_by_inspecting_container_environment(container, key_in_config):
    client = docker.from_env()
    res = client.api.inspect_container(container.short_id)
    for _, value in enumerate(res['Config']['Env']):
        if value.find(key_in_config) != -1:
            arr = value.split('=')
            return arr[1]
    return ""


def get_container_port_bindings(container):
    return container.attrs['HostConfig']['PortBindings']


def is_beta_build(version_number):
    return int(version_number) % 2 == 0


def get_version(version):
    '''
    It returns the version in format of v2.{major version}.{minor version}.

    All beta builds are marked 2.{even_number}.*. Expiry date for these is image create date + 45 days
    All external builds are 2.{odd_number}.*. Expiry date for all 2.{odd_number}.* is same.
    Although 2.19.* is for external users, expiry date for these builds are image_create_date + 180 days
    So, this function returns
      if version >= v2.21.1 or if it's not a internal build
          (v2.{major version}, v2.{major version}.{minor version})
         Ex : i.e for 2.21.1 it returns (v2.21,v2.21.1)
      otherwise
          (v2.{major version}.{minor version}, v2.{major version}.{minor version})
          Ex : i.e for 2.20.2 it returns (v2.20.2,v2.20.2)
    '''
    arr = version.split('.')
    if is_beta_build(arr[1]) or int(arr[1]) <= 19:
        return (version, version)
    return (arr[0] + '.' + arr[1], version)


def get_expiration_map():

    def is_wa_image(image):
        if not image['RepoDigests']:
            return False
        for repo_tag in image['RepoDigests']:
            return repo_tag.find(WA_WEBAPP_CONTAINER_TAG) > -1 or repo_tag.find(WA_COREAPP_CONTAINER_TAG) > -1

    client = docker.from_env()
    images = client.api.images()
    expiration_map = dict()
    for image in images:
        if is_wa_image(image):
            ver = get_version(image['RepoTags'][0].split(':')[1])
            if ver[0] not in expiration_map:
                if 'Labels' in image and 'EXPIRES_ON' in image['Labels']:
                    dt_ts = datetime.strptime(image['Labels']['EXPIRES_ON'], EXPIRED_DATE_FORMAT)
                    expiration_map[ver[0]] = str(dt_ts)
                    continue
                ts = get_expiry_date(ver[0], image['Created'])
                expiration_map[ver[0]] = ts
    return expiration_map


def get_expiry_date(version, ts):
    arr = version.split('.')
    str_ts = datetime.utcfromtimestamp(ts).strftime(DATE_FORMAT)
    dt_ts = datetime.strptime(str_ts, DATE_FORMAT)
    expiry_date = ''
    if is_beta_build(arr[1]):
        expiry_date = dt_ts + timedelta(LIFETIME_OF_BETA_BUILD_IN_DAYS)
    else:
        expiry_date = dt_ts + timedelta(LIFETIME_OF_BUILD_IN_DAYS)
    return str(expiry_date)


class DockerDiffFileChange(Enum):
    CREATED = 0
    MODIFIED = 1
    DELETED = 2


class WAContainer:
    def __init__(self, container, container_type):
        self.container = container
        self.container_type = container_type

    @property
    def status(self):
        return self.container.status
