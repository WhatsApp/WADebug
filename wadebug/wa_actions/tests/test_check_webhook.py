# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import patch
from wadebug import results
from wadebug.exceptions import WABizAccessError
from wadebug.wa_actions.curl_utils import CURLTestResult
from wadebug.wa_actions.implementations import check_webhook
from wadebug.wa_actions.implementations.check_webhook import curl_utils, docker_utils


MOCK_COMPLETE_CONFIG = {
    "webapp": {
        "baseUrl": "dummy_url",
        "user": "dummy_user",
        "password": "dummy_password",
    }
}

DUMMY_HTTP_WEBHOOK = "http://dummy_webhook_url.com"
DUMMY_HTTPS_WEBHOOK = "https://dummy_webhook_url.com"


class MockContainer:
    pass


class TestCheckWebhook(unittest.TestCase):
    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.__init__", return_value=None)
    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url", return_value="")
    @patch.object(results, "Warning", autospec=True)
    def test_should_return_warning_if_no_webhook_url(self, *_):
        check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
        results.Warning.assert_called()

    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.__init__", return_value=None)
    @patch(
        "wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url",
        return_value=DUMMY_HTTP_WEBHOOK,
    )
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_webhook_url_not_https(self, *_):
        check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
        results.Problem.assert_called()

    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.__init__", return_value=None)
    @patch(
        "wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url",
        side_effect=WABizAccessError,
    )
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_access_error(self, *_):
        check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
        results.Problem.assert_called()

    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.__init__", return_value=None)
    @patch(
        "wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url",
        return_value=DUMMY_HTTPS_WEBHOOK,
    )
    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_cert", return_value=None)
    @patch.object(
        docker_utils, "get_running_wacore_containers", return_value=[MockContainer()]
    )
    @patch.object(
        curl_utils,
        "https_post_request_from_container",
        return_value=(CURLTestResult.CONNECTION_TIMEOUT, None),
    )
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_read_timeout(self, *_):
        check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
        results.Problem.assert_called()

    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.__init__", return_value=None)
    @patch(
        "wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url",
        return_value=DUMMY_HTTPS_WEBHOOK,
    )
    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_cert", return_value=None)
    @patch.object(
        docker_utils, "get_running_wacore_containers", return_value=[MockContainer()]
    )
    @patch.object(
        curl_utils,
        "https_post_request_from_container",
        return_value=(CURLTestResult.CONNECTION_ERROR, None),
    )
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_connection_error(self, *_):

        check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
        results.Problem.assert_called()

    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.__init__", return_value=None)
    @patch(
        "wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url",
        return_value=DUMMY_HTTPS_WEBHOOK,
    )
    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_cert", return_value=None)
    @patch.object(
        docker_utils, "get_running_wacore_containers", return_value=[MockContainer()]
    )
    @patch.object(
        curl_utils,
        "https_post_request_from_container",
        return_value=(CURLTestResult.HTTP_STATUS_NOT_OK, None),
    )
    @patch.object(results, "Problem", autospec=True)
    def test_should_return_problem_if_non_200_status_code(self, *_):
        check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
        results.Problem.assert_called()

    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.__init__", return_value=None)
    @patch(
        "wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url",
        return_value=DUMMY_HTTPS_WEBHOOK,
    )
    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_cert", return_value=None)
    @patch.object(
        docker_utils, "get_running_wacore_containers", return_value=[MockContainer()]
    )
    @patch.object(
        curl_utils,
        "https_post_request_from_container",
        return_value=(CURLTestResult.OK, check_webhook.ACCEPTABLE_RESPONSE_TIME + 1),
    )
    @patch.object(results, "Warning", autospec=True)
    def test_should_return_problem_if_warning_if_webhook_response_slow(self, *_):
        check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
        results.Warning.assert_called()
