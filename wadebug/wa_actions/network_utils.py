# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def hostname_reachable_from_container(container, hostname, port, timeout):
    try:
        exec_result = container.exec_run(
            ['nc', '-zv', hostname,
             str(port), '-w',
             str(timeout)])
        exit_code = exec_result[0]
        return exit_code == 0
    except Exception:
        return False


def hostname_not_reachable_from_container(container, hostname, port, timeout):
    return not hostname_reachable_from_container(container, hostname, port,
                                                 timeout)
