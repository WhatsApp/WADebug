# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from requests.exceptions import RequestException
from wadebug import exceptions
from wadebug.wa_actions.wabiz_api import WABizAPI

import pytest


MOCK_COMPLETE_CONFIG = {
    'baseUrl': 'https://localhost:9090',
    'user': 'wadebug',
    'password': 'secretdebugger',
}

MOCK_INCOMPLETE_CONFIG = {
    'baseUrl': 'bad_url',
    'user': 'bad_user',
}


def mocked_requests_post_auth_error(*args, **kwargs):
    return MockResponse({'errors': [{'details': 'auth_error'}]}, 401)


def mocked_requests_post_auth_success(*args, **kwargs):
    return MockResponse({'users': [{'token': 'fake_token'}]}, 200)


def mocked_requests_get_support_error(*args, **kwargs):
    raise RequestException('Mock Error')


def mocked_requests_get_support_success(*args, **kwargs):
    return MockResponse({'support': 'fake_info'}, 200)


def mocked_requests_get_app_settings_error(*args, **kwargs):
    return MockResponse({'errors': [{'code': 1005}]}, 200)


def mocked_requests_get_app_settings_success(*args, **kwargs):
    return MockResponse({'settings': {'application': {'webhooks': {'url': 'fake_url'}}}}, 200)


def test_should_throw_valueerror_for_wrong_config_input(mocker):
    with pytest.raises(ValueError):
        WABizAPI(**MOCK_INCOMPLETE_CONFIG)


def test_should_throw_auth_error_if_user_pass_is_invalid(mocker):
    mocked_call = mocker.patch('requests.post', side_effect=mocked_requests_post_auth_error)
    with pytest.raises(exceptions.WABizAuthError):
        WABizAPI(**MOCK_COMPLETE_CONFIG)
    assert mocked_call.call_count == 1


def test_should_not_throw_auth_error_if_user_pass_is_valid(mocker):
    expected_header = {
        'AUTHORIZATION': 'Bearer fake_token',
        'CONTENT_TYPE': 'application/json',
    }
    mocked_call = mocker.patch('requests.post', side_effect=mocked_requests_post_auth_success)
    try:
        client = WABizAPI(**MOCK_COMPLETE_CONFIG)
        assert mocked_call.call_count == 1
        assert client.api_header == expected_header
    except Exception as e:
        pytest.fail(e)


def test_should_throw_network_error_if_host_not_reachable(mocker):
    mocker.patch('requests.post', side_effect=mocked_requests_post_auth_success)
    mocked_call = mocker.patch('requests.get', side_effect=mocked_requests_get_support_error)

    with pytest.raises(exceptions.WABizNetworkError):
        client = WABizAPI(**MOCK_COMPLETE_CONFIG)
        client.get_support_info()
        assert mocked_call.call_count == 1


def test_should_not_throw_network_error_if_host_reachable(mocker):
    mocker.patch('requests.post', side_effect=mocked_requests_post_auth_success)
    mocked_call = mocker.patch('requests.get', side_effect=mocked_requests_get_support_success)
    try:
        client = WABizAPI(**MOCK_COMPLETE_CONFIG)
        support_info = client.get_support_info()
        assert mocked_call.call_count == 1
        assert 'support' in support_info
    except Exception as e:
        pytest.fail(e)


def test_should_throw_access_error_if_insufficient_role_permissions(mocker):
    mocker.patch('requests.post', side_effect=mocked_requests_post_auth_success)
    mocked_call = mocker.patch('requests.get', side_effect=mocked_requests_get_app_settings_error)

    with pytest.raises(exceptions.WABizAccessError):
        client = WABizAPI(**MOCK_COMPLETE_CONFIG)
        client.get_webhook_url()
        assert mocked_call.call_count == 1


def test_should_return_webhook_url_if_no_error(mocker):
    expected_webhook_url = 'fake_url'
    mocker.patch('requests.post', side_effect=mocked_requests_post_auth_success)
    mocked_call = mocker.patch('requests.get', side_effect=mocked_requests_get_app_settings_success)

    try:
        client = WABizAPI(**MOCK_COMPLETE_CONFIG)
        webhook_url = client.get_webhook_url()
        assert mocked_call.call_count == 1
        assert webhook_url == expected_webhook_url
    except Exception as e:
        pytest.fail(e)


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data
