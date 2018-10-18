# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class Result:
    def to_dict(self):
        return {
            'class': self.action.__name__,
            'user_facing_name': self.action.user_facing_name,
            'result': self.result,
            'short_description': self.action.short_description,
            'message': self.message,
            'details': self.details,
            'remediation': self.remediation,
        }

    @property
    def result(self):
        """String value of the result."""
        return self.__class__.__name__.lower()


class OK(Result):
    def to_dict(self):
        return {
            'class': self.action.__name__,
            'user_facing_name': self.action.user_facing_name,
            'result': self.__class__.__name__,
        }

    def __init__(self, action):
        self.action = action


class _NotOK(Result):
    """Intermediate class to create cases where something is wrong."""

    def __str__(self):
        return 'Name: {}\n\nDescription: {}\n\nDetails: {}\n\n{}\n\n{}'.format(
            self.action.__name__,
            self.action.short_description,
            self.message,
            self.details,
            self.remediation
        )

    def __init__(self, action, message, details, remediation):
        self.action = action
        self.message = message
        if isinstance(details, Exception):
            self.details = str(details)
        else:
            self.details = details
        self.remediation = remediation


class Warning(_NotOK):
    pass


class Skipped(_NotOK):
    pass


class Problem(_NotOK):
    pass


class WADebugError(_NotOK):
    @property
    def result(self):
        return 'wadebug_error'
