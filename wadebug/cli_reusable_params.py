# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

from wadebug.cli_param import ReusableParam


opt_out = ReusableParam(
    "--do-not-send-usage",
    "opt_out",
    help="Pass this flag to opt out from sending usage to WhatsApp. Sending "
    "usage to WhatsApp could accelerate Direct Support ticket resolve time.",
    is_flag=True,
    default=False,
)

json_output = ReusableParam(
    "--json",
    "json",
    help="Pass this flag to output results in json format. This enables "
    "automation and integration with other applications if needed.",
    is_flag=True,
    default=False,
)

send_logs = ReusableParam(
    "--send",
    "send",
    help="Opt to send logs to Facebook for help on Direct Support.",
    is_flag=True,
    default=False,
)

logs_since = ReusableParam(
    "--since",
    "since",
    help="Pass this flag to get logs since a datetime in GMT timezone. "
    "Use the datetime format yyyy-MM-dd HH:mm:ss enclosed in quotes "
    "(e.g.: '2018-09-19 14:55:02')",
)
