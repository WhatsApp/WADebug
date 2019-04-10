# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from wadebug.exceptions import WABizAccessError, WABizAuthError, WABizGeneralError, WABizNetworkError
from wadebug.wa_actions.base import WAAction
from wadebug.wa_actions.wabiz_api import WABizAPI
from wadebug import results

import requests

REQ_TIMEOUT = 5
ACCEPTABLE_RESPONSE_TIME = 3


class CheckWebhookAction(WAAction):
    user_facing_name = 'check_webhook'
    short_description = \
        'Test if the webhook is accessible and responsive'
    config_dependencies = ('webapp.baseUrl', 'webapp.user', 'webapp.password')

    @classmethod
    def _run(cls, config, *args, **kwargs):
        api = WABizAPI(**config.get('webapp'))
        try:
            webhook_url = api.get_webhook_url()
            if not webhook_url:
                return _result_webhook_not_set(cls)
        except (WABizAccessError, WABizAuthError, WABizNetworkError, ValueError) as e:
            return _result_get_webhook_error(cls, e)
        # explicitly catching a possible exception
        except WABizGeneralError as e:
            # rethrowing as WABizGeneralError is likely not a user error, should be handled by app-wide catch
            raise e
        else:
            try:
                status_code, response_time = test_webhook_health(webhook_url)
            except requests.exceptions.ReadTimeout:
                return _result_webhook_did_not_respond(cls)
            except requests.exceptions.ConnectionError:
                return _result_webhook_could_not_connect(cls)
            else:
                if status_code != 200:
                    return _result_webhook_did_not_return_ok(cls, status_code)
                elif (response_time > ACCEPTABLE_RESPONSE_TIME):
                    return _result_webhook_slow_response(cls, response_time)
                return results.OK(cls)


def test_webhook_health(webhook_url):
    res = requests.post(webhook_url, timeout=REQ_TIMEOUT, verify=False)
    return res.status_code, res.elapsed.total_seconds()


def _result_webhook_not_set(cls):
    return results.Warning(
        cls, 'Unable to check webhook', 'Webhook has not been set',
        'Set up webhook via App Settings https://developers.facebook.com/docs/whatsapp/api/settings/app', ''
    )


def _result_get_webhook_error(cls, exception):
    results.Problem(cls, 'Unable to check webhook', str(exception), '')


def _result_webhook_did_not_respond(cls):
    return results.Problem(
        cls, 'Webhook unresponsive', 'Webhook did not respond within {} seconds'.format(REQ_TIMEOUT),
        'Please ensure you are returning 200 OK from your webhook handler as soon as possible.  '
        'If processing is needed, we recommend returning 200 OK and doing processing later.'
    )


def _result_webhook_could_not_connect(cls):
    return results.Problem(
        cls, 'Webhook unresponsive', 'Could not establish a connection to the webhook'.format(REQ_TIMEOUT),
        'Please check to make sure your webhook endpoint is up, or '
        'have configured the webhook setting correctly'
    )


def _result_webhook_did_not_return_ok(cls, status_code):
    return results.Problem(
        cls, 'Webhook did not return 200 OK', 'Webhook returned status code of {}'.format(status_code),
        'Please ensure your webhook handler returns 200 OK'
    )


def _result_webhook_slow_response(cls, response_time):
    return results.Warning(
        cls, 'Slow webhook response', 'Webhook responded in {} seconds'.format(response_time),
        'Please ensure you are returning 200 OK from your webhook handler as soon as possible'
    )
