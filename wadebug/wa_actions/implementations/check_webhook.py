# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from wadebug.exceptions import WABizAccessError, WABizAuthError, WABizGeneralError, WABizNetworkError
from wadebug.wa_actions import docker_utils
from wadebug.wa_actions import curl_utils
from wadebug.wa_actions.curl_utils import CURLTestResult
from wadebug.wa_actions.base import WAAction
from wadebug.wa_actions.wabiz_api import WABizAPI
from wadebug import results

import tempfile
import os

REQ_TIMEOUT = 5
ACCEPTABLE_RESPONSE_TIME = 3

TEST_POST_DATA_STRING = '{"wadebug_webhook_test":"test"}'
DEST_PATH = '/usr/local/waent'


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
            if not webhook_url.startswith('https'):
                return _result_webhook_not_https(cls)
        except (WABizAccessError, WABizAuthError, WABizNetworkError, ValueError) as e:
            return _result_get_webhook_error(cls, e)
        # explicitly catching a possible exception
        except WABizGeneralError as e:
            # rethrowing as WABizGeneralError is likely not a user error, should be handled by app-wide catch
            raise e

        wacore_containers = docker_utils.get_running_wacore_containers()

        if not wacore_containers:
            return results.Problem(
                cls, 'Webhook check failed',
                'There is no wacore container running',
                'Please check results from other actions to diagnose'
            )

        container = wacore_containers[0]
        cert_str = api.get_webhook_cert()
        dest_cert = None
        if cert_str:
            with tempfile.NamedTemporaryFile() as cert_file:
                cert_file.write(cert_str)
                cert_file.seek(0)
                docker_utils.put_archive_to_container(container, cert_file.name, DEST_PATH)
                dest_cert = os.path.join(DEST_PATH, os.path.basename(cert_file.name))

        result, response_time = curl_utils.https_post_request_from_container(
            container, webhook_url, TEST_POST_DATA_STRING, REQ_TIMEOUT, dest_cert,
        )

        if result == CURLTestResult.CONNECTION_ERROR:
            return _result_webhook_could_not_connect(cls)
        elif result == CURLTestResult.SSL_CERT_UNKNOWN:
            return _result_webhook_no_cert_uploaded(cls)
        elif result == CURLTestResult.CONNECTION_TIMEOUT:
            return _result_webhook_did_not_respond(cls)
        elif result == CURLTestResult.HTTP_STATUS_NOT_OK:
            return _result_webhook_did_not_return_ok(cls)
        elif response_time > ACCEPTABLE_RESPONSE_TIME:
            return _result_webhook_slow_response(cls, response_time)

        return results.OK(cls)


def _result_webhook_not_set(cls):
    return results.Warning(
        cls, 'Unable to check webhook', 'Webhook has not been set',
        'Set up webhook via App Settings https://developers.facebook.com/docs/whatsapp/api/settings/app', ''
    )


def _result_webhook_not_https(cls):
    return results.Problem(
        cls, 'Webhook not secure', 'Webhook is not using https',
        'Please set a webhook endpoint that is https enabled', ''
    )


def _result_webhook_no_cert_uploaded(cls):
    return results.Problem(
        cls, 'SSL verification error', 'Unable to connect securely to the webhook',
        'Please upload self signed cert (and restart coreapp) or use a publicly known cert', ''
    )


def _result_get_webhook_error(cls, exception):
    results.Problem(cls, 'Unable to check webhook', str(exception), '')


def _result_webhook_could_not_connect(cls):
    return results.Problem(
        cls, 'Webhook unresponsive', 'Could not establish a connection to the webhook'.format(REQ_TIMEOUT),
        'Please check to make sure your webhook endpoint is up, or '
        'have configured the webhook setting correctly'
    )


def _result_webhook_did_not_respond(cls):
    return results.Problem(
        cls, 'Webhook unresponsive', 'Webhook did not respond within {} seconds'.format(REQ_TIMEOUT),
        'Please ensure you are returning 200 OK from your webhook handler as soon as possible.  '
        'If processing is needed, we recommend returning 200 OK and doing processing later.'
    )


def _result_webhook_did_not_return_ok(cls):
    return results.Problem(
        cls, 'Unexpected webhook response', 'Webhook did not return 200 OK',
        'Please ensure your webhook handler returns 200 OK'
    )


def _result_webhook_slow_response(cls, response_time):
    return results.Warning(
        cls, 'Slow webhook response', 'Webhook responded in {} seconds'.format(response_time),
        'Please ensure you are returning 200 OK from your webhook handler as soon as possible'
    )
