# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.exceptions import WABizAccessError
from wadebug import results
from wadebug.wa_actions.implementations import check_webhook
from wadebug.wa_actions.implementations.check_webhook import docker_utils, curl_utils
from wadebug.wa_actions.curl_utils import CURLTestResult

MOCK_COMPLETE_CONFIG = {
    'webapp': {
        'baseUrl': 'dummy_url',
        'user': 'dummy_user',
        'password': 'dummy_password',
    }
}

DUMMY_HTTP_WEBHOOK = 'http://dummy_webhook_url.com'
DUMMY_HTTPS_WEBHOOK = 'https://dummy_webhook_url.com'


def test_should_return_warning_if_no_webhook_url(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', return_value='')
    mocker.patch.object(results, 'Warning', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Warning.assert_called()


def test_should_return_problem_if_webhook_url_not_https(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', return_value=DUMMY_HTTP_WEBHOOK)
    mocker.patch.object(results, 'Problem', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Problem.assert_called()


def test_should_return_problem_if_access_error(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', side_effect=WABizAccessError)
    mocker.patch.object(results, 'Problem', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Problem.assert_called()


def test_should_return_problem_if_read_timeout(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', return_value=DUMMY_HTTPS_WEBHOOK)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_cert', return_value=None)
    mocker.patch.object(
        docker_utils,
        'get_running_wacore_containers',
        return_value=[MockContainer()]
    )
    mocker.patch.object(
        curl_utils,
        'https_post_request_from_container',
        return_value=(CURLTestResult.CONNECTION_TIMEOUT, None)
    )
    mocker.patch.object(results, 'Problem', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Problem.assert_called()


def test_should_return_problem_if_connection_error(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', return_value=DUMMY_HTTPS_WEBHOOK)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_cert', return_value=None)
    mocker.patch.object(
        docker_utils,
        'get_running_wacore_containers',
        return_value=[MockContainer()]
    )
    mocker.patch.object(
        curl_utils,
        'https_post_request_from_container',
        return_value=(CURLTestResult.CONNECTION_ERROR, None)
    )
    mocker.patch.object(results, 'Problem', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Problem.assert_called()


def test_should_return_problem_if_non_200_status_code(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', return_value=DUMMY_HTTPS_WEBHOOK)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_cert', return_value=None)
    mocker.patch.object(
        docker_utils,
        'get_running_wacore_containers',
        return_value=[MockContainer()]
    )
    mocker.patch.object(
        curl_utils,
        'https_post_request_from_container',
        return_value=(CURLTestResult.HTTP_STATUS_NOT_OK, None)
    )
    mocker.patch.object(results, 'Problem', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Problem.assert_called()


def test_should_return_problem_if_warning_if_webhook_response_slow(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', return_value=DUMMY_HTTPS_WEBHOOK)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_cert', return_value=None)
    mocker.patch.object(
        docker_utils,
        'get_running_wacore_containers',
        return_value=[MockContainer()]
    )
    mocker.patch.object(
        curl_utils,
        'https_post_request_from_container',
        return_value=(CURLTestResult.OK, check_webhook.ACCEPTABLE_RESPONSE_TIME + 1)
    )
    mocker.patch.object(results, 'Warning', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Warning.assert_called()


class MockContainer:
    pass
