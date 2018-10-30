# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools

import click

from wadebug import exceptions

"""Module to create re-usable CLI parameters for wadebug"""

# This works by creating two new decorators: wadebug_option and wadebug_argument

# They are used exactly like click.option or click. argument, with two differences:
# 1. They save the value os a parameter on dict ctx.obj as well.
# 2. They take a ReusableParam as argument

# Usage example:

# json_output = ReusableParam(
#     '--json',
#     'json',
#     help='Pass this flag to output results in json format. This enables '
#     'automation and integration with other applications if needed.',
#     is_flag=True,
#     default=False,
# )

# @click.option('--specific_param', 'specific_param', help='used only on my_new_command')
# @wadebug_option(json_output)
# def my_new_command(ctx, specific_param, **kwargs):
#     print('This is my_new_command')
#     print('param_specific_to_this_command is {}'.format(param_specific_to_this_command))
#     print('--json is {}'.format(ctx.obj['json']))


# By using the decorator above, we can make the two following commands to be equivalent
# wadebug --json my_new_command
# wadebug my_new_command --json

# if `json` appears before `ls`, `json=True` is set on dict `ctx.obj`
# on function `my_new_command`, value of `kwargs['json']` is False as it wasn't provided,
# but code will prioritize value from ctx.obj as it was set

class ReusableParam:
    """A click command-line parameter that can be used for multiple click commands."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class _WADebugParam(object):
    """Decorator to use click with ReusableParam. Values should always be accessed through ctx.obj and NEVER kwargs."""

    decorator_mapping = {
        'option': click.option,
        'argument': click.argument,
    }

    def __init__(self, reusable_param, param_type):
        self.reusable_param = reusable_param

        if param_type not in self.decorator_mapping.keys():
            raise exceptions.InvalidParamType(
                'param_type {} is invalid. options are {}'.format(
                    param_type,
                    self.self.decorator_mapping.keys()
                )
            )

        self.param_type = param_type

    def __call__(self, func):
        decorator_to_apply = self.decorator_mapping[self.param_type]

        @decorator_to_apply(
            *self.reusable_param.args,
            **self.reusable_param.kwargs
        )
        @functools.wraps(func)
        def wrapper(ctx, *args, **kwargs):
            if not ctx.obj:
                ctx.obj = {}
            for k, v in kwargs.items():
                if v:
                    ctx.obj[k] = v
            return func(ctx, *args, **kwargs)

        return wrapper


class wadebug_option(_WADebugParam):
    def __init__(self, reusable_param):
        super(wadebug_option, self).__init__(reusable_param, 'option')


class wadebug_argument(_WADebugParam):
    def __init__(self, reusable_param):
        super(wadebug_option, self).__init__(reusable_param, 'argument')
