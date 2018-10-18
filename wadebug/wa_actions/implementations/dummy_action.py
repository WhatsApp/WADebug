# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from wadebug.wa_actions.base import WAAction
from wadebug import results


class DummyOKAction(WAAction):
    user_facing_name = 'dummy_ok_action'
    short_description = \
        'Action to test that things work. Always returns OK.'

    @classmethod
    def _run(cls, *args, **kwargs):
        return results.OK(cls)


class DummyProblemAction(WAAction):
    user_facing_name = 'dummy_problem_action'
    short_description = \
        'Action to test that things work. Always returns Problem.'

    @classmethod
    def _run(cls, config, *args, **kwargs):
        return results.Problem(
            cls,
            'This action always returns a problem.',
            'It\'s used for test purposes.',
            'There is nothing you can do about it.',
        )


class DummyWADebugErrorAction(WAAction):
    user_facing_name = 'dummy_wadebug_error_action'
    short_description = \
        'Action to test that things work. Always throws an Exception.'

    @classmethod
    def _run(cls, config, *args, **kwargs):
        raise Exception('This action always throws')
