# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import with_metaclass
from wadebug.wa_actions.common import common_results

import pydash
import traceback

'''
Register all WAActions classes available in a dict
using a metaclasses. If we decide to support only python3.6+
it can be simplified
'''
registry = {}
user_facing_registry = {}


class WAActionAlreadyRegisteredError(Exception):
    pass


def register_class(target_class):
    if target_class.user_facing_name in user_facing_registry:
        raise WAActionAlreadyRegisteredError(
            '{} already in use by class {}. '
            'Choose another user-facing name'.format(
                target_class.user_facing_name,
                user_facing_registry[target_class.user_facing_name].__name__),
        )
    registry[target_class.__name__] = target_class
    user_facing_registry[target_class.user_facing_name] = target_class


class MetaRegistry(type):
    """Metaclass to store WAActions when instantiating. """
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        if name != 'WAAction' and name not in registry:
            register_class(cls)
        return cls


class WAAction(with_metaclass(MetaRegistry)):
    # should be lowercase, no hypens, short and descriptive
    user_facing_name = ''

    # A one phrase description of your action
    short_description = ''

    # tuples of configuration dependencies of this action
    # e.g.: ('db.host', 'auth.token')
    config_dependencies = ()

    def __str__(self):
        return '{s.user_facing_name}: {s.short_description}'.format(s=self)

    @classmethod
    def run(cls, config, *args, **kwargs):
        invalid_dependencies = tuple(
            c for c in cls.config_dependencies
            if not pydash.objects.has(config, c)
        )

        if invalid_dependencies:
            return common_results.missing_config(cls, invalid_dependencies)

        try:
            return cls._run(config, *args, **kwargs)
        except Exception as e:
            return common_results.wadebug_error(cls, e, traceback.format_exc())

    @classmethod
    def _run(cls, config, *args, **kwargs):
        raise NotImplementedError('Action not implemented.')


def get_all_actions():
    from wadebug.wa_actions.implementations.dummy_action import (
        DummyOKAction,
        DummyProblemAction,
        DummyWADebugErrorAction,
    )

    blacklisted_actions = set([
        DummyOKAction,
        DummyProblemAction,
        DummyWADebugErrorAction,
    ])
    ret = [v for v in registry.values() if v not in blacklisted_actions]
    return ret


def get_action_by_classname(name):
    return registry[name]


def get_action_by_name(name):
    return user_facing_registry[name]
