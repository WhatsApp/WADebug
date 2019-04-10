# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from requests.exceptions import ReadTimeout, ConnectionError
from wadebug.exceptions import WABizAccessError
from wadebug import results
from wadebug.wa_actions.implementations import check_webhook

MOCK_COMPLETE_CONFIG = {
    'webapp': {
        'baseUrl': 'dummy_url',
        'user': 'dummy_user',
        'password': 'dummy_password',
    }
}


def test_should_return_warning_if_no_webhook_url(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', return_value='')
    mocker.patch.object(results, 'Warning', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Warning.assert_called()


def test_should_return_problem_if_access_error(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', side_effect=WABizAccessError)
    mocker.patch.object(results, 'Problem', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Problem.assert_called()


def test_should_return_problem_if_read_timeout(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', return_value='dummy_webhook_url')
    mocker.patch.object(check_webhook, 'test_webhook_health', side_effect=ReadTimeout)
    mocker.patch.object(results, 'Problem', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Problem.assert_called()


def test_should_return_problem_if_connection_error(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', return_value='dummy_webhook_url')
    mocker.patch.object(check_webhook, 'test_webhook_health', side_effect=ConnectionError)
    mocker.patch.object(results, 'Problem', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Problem.assert_called()


def test_should_return_problem_if_non_200_status_code(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', return_value='dummy_webhook_url')
    mocker.patch.object(check_webhook, 'test_webhook_health', return_value=(300, 5))
    mocker.patch.object(results, 'Problem', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Problem.assert_called()


def test_should_return_problem_if_warning_if_webhook_response_slow(mocker):
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.__init__', return_value=None)
    mocker.patch('wadebug.wa_actions.wabiz_api.WABizAPI.get_webhook_url', return_value='dummy_webhook_url')
    mocker.patch.object(
        check_webhook, 'test_webhook_health',
        return_value=(200, check_webhook.ACCEPTABLE_RESPONSE_TIME + 1)
    )
    mocker.patch.object(results, 'Warning', autospec=True)

    check_webhook.CheckWebhookAction().run(config=MOCK_COMPLETE_CONFIG)
    results.Warning.assert_called()
