# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from wadebug import results


def missing_config(cls, missing_configs):
    return results.Skipped(
        cls,
        'This check is skipped',
        'Unable to read required config values:\n{}'.format(
            '\n'.join(missing_configs)),
        'Please check these configurations are properly defined in wadebug.conf.yml'
    )


def wadebug_error(cls, exception, trace):
    return results.WADebugError(
        cls,
        'An unexpected error occurred on this check',
        exception,
        'Please report this via Direct Support (https://business.facebook.com/direct-support)',
        traceback=trace,
    )
