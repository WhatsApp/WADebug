# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
from os import path

import pytest
from mock import patch
from wadebug import exceptions
from wadebug.wa_actions import docker_utils, log_utils


class MockContainer:
    def __init__(self):
        self.name = "MockContainer"


class TestLogUtils(unittest.TestCase):
    @patch("os.access", return_value=True)
    @patch("os.makedirs", return_value=True)
    def test_should_makedir_if_have_access(self, mocked_makedirs_call, mock_access):
        log_utils.check_access()

        assert mocked_makedirs_call.call_count == 1

    def test_should_return_filepath_string_if_get_container_logs_has_no_exceptions(
        self
    ):
        mock_container = docker_utils.WAContainer(MockContainer(), "container_type")
        expected_container_logs_filepath = "filepath"

        with patch.object(
            docker_utils, "get_container_logs", return_value="This is a container log"
        ), patch.object(
            docker_utils, "write_to_file_in_binary", return_value=None
        ), patch.object(
            path, "join", return_value=expected_container_logs_filepath
        ):
            try:
                log_filepath = log_utils.get_container_logs(mock_container)
            except Exception as e:
                pytest.fail(
                    "Unexpected Exception from log_utils.get_container_logs: \n {}".format(
                        e
                    )
                )
            assert log_filepath == expected_container_logs_filepath

    def test_should_return_filepath_string_if_get_container_inspect_logs_has_no_exceptions(
        self
    ):
        mock_container = docker_utils.WAContainer(MockContainer(), "container_type")
        mock_inspect_result = {"result": "this is a mock result"}
        expected_inspect_log_filepath = "filepath"

        with patch.object(
            docker_utils, "get_inspect_result", return_value=mock_inspect_result
        ), patch.object(docker_utils, "write_to_file", return_value=None), patch.object(
            path, "join", return_value=expected_inspect_log_filepath
        ):
            try:
                inspect_log_filepath = log_utils.get_container_inspect_logs(
                    mock_container
                )
            except Exception as e:
                pytest.fail(
                    "Unexpected Exception from log_utils."
                    "get_container_inspect_logs: \n {}".format(e)
                )
            assert inspect_log_filepath == expected_inspect_log_filepath

    def test_should_return_filepath_string_if_get_corecontainer_coredumps_logs_has_no_exceptions(
        self
    ):
        mock_container = docker_utils.WAContainer(
            MockContainer(), docker_utils.WA_COREAPP_CONTAINER_TAG
        )
        expected_coredump_log_filepath = "file_path"

        with patch.object(
            docker_utils, "get_core_dump_logs", return_value="Mock Coredump Result"
        ), patch.object(docker_utils, "write_to_file", return_value=None), patch.object(
            path, "join", return_value=expected_coredump_log_filepath
        ):
            try:
                coredump_log_filepath = log_utils.get_corecontainer_coredumps_logs(
                    mock_container
                )
            except Exception as e:
                pytest.fail(
                    "Unexpected Exception from log_utils."
                    "get_corecontainer_coredumps_logs: \n {}".format(e)
                )
            assert coredump_log_filepath == expected_coredump_log_filepath

    def test_should_return_none_if_get_corecontainer_coredumps_logs_on_not_core_container(
        self,
    ):
        mocker_container = docker_utils.WAContainer(
            MockContainer(), "not core container type"
        )
        try:
            result = log_utils.get_corecontainer_coredumps_logs(mocker_container)
        # there should be no exception, since get_corecontainer_coredumps
        # should not run any code to pull logs if the container is not the core container
        except Exception as e:
            pytest.fail(
                "Unexpected Exception from log_utils."
                "get_corecontainer_coredumps_logs: \n {}".format(e)
            )
        assert result is None

    def test_should_return_filepath_string_if_get_webcontainer_logs_has_no_exceptions(
        self
    ):
        mock_container = docker_utils.WAContainer(
            MockContainer(), docker_utils.WA_WEBAPP_CONTAINER_TAG
        )
        expected_log_filepath = "/logs"

        with patch.object(
            log_utils,
            "copy_additional_logs_for_webcontainer",
            return_value=expected_log_filepath,
        ):
            try:
                webapp_log_filepath, webapp_error_log_filepath = log_utils.get_webcontainer_logs(
                    mock_container
                )
            except Exception as e:
                pytest.fail(
                    "Unexpected Exception from log_utils.get_webcontainer_logs:\n{}".format(
                        e
                    )
                )
            assert (
                webapp_log_filepath == expected_log_filepath
                and webapp_error_log_filepath == expected_log_filepath
            )

    def test_should_return_none_if_get_webcontainer_logs_on_not_web_container(self):
        mocker_container = docker_utils.WAContainer(
            MockContainer(), "not web container type"
        )
        try:
            log_result, error_result = log_utils.get_webcontainer_logs(mocker_container)
        # there should be no exception, since get_webcontainer_logs
        # should not run any code to pull logs if the container is not the web container
        except Exception as e:
            pytest.fail(
                "Unexpected Exception from log_utils.get_webcontainer_logs:\n{}".format(
                    e
                )
            )
        assert log_result is None and error_result is None

    @patch.object(
        docker_utils,
        "get_wa_containers",
        return_value=[docker_utils.WAContainer(MockContainer(), "container_type")],
    )
    @patch.object(log_utils, "get_container_logs", return_value="/container/logs")
    @patch.object(log_utils, "get_container_inspect_logs", return_value="/inspect/logs")
    @patch.object(
        log_utils, "get_corecontainer_coredumps_logs", return_value="/core_dump/logs"
    )
    @patch.object(
        log_utils,
        "get_webcontainer_logs",
        return_value=("/webcontainer/logs", "/webcontainer/errors"),
    )
    def test_should_return_list_of_filepaths_for_logs_if_get_logs_has_no_exceptions(
        self, *_
    ):
        expected_logs_files = [
            "/container/logs",
            "/inspect/logs",
            "/core_dump/logs",
            "/webcontainer/logs",
            "/webcontainer/errors",
        ]
        try:
            results = log_utils.get_logs()
        except exceptions.LogsNotCompleteError:
            pytest.fail("Access error:  Cannot write logs to current directory")
        assert results == expected_logs_files

    @patch.object(docker_utils, "get_archive_from_container", return_value="Mock logs")
    @patch.object(docker_utils, "write_to_file", return_value=None)
    def test_should_write_webcontainer_log_to_file(
        self, mocked_write_call, mock_get_archive_from_container
    ):
        mock_container = MockContainer()

        log_utils.copy_additional_logs_for_webcontainer(
            mock_container, "mock path", "mock file name"
        )
        assert mocked_write_call.call_count == 1

    @patch("wadebug.wa_actions.wabiz_api.WABizAPI.__init__", return_value=None)
    @patch(
        "wadebug.wa_actions.wabiz_api.WABizAPI.get_support_info",
        return_value="mock_json_string",
    )
    @patch("wadebug.config.Config.values", return_value={"webapp": {}})
    @patch.object(docker_utils, "write_to_file", return_value=None)
    def test_get_support_info_should_return_file_path_if_no_exceptions(
        self,
        mocked_write_call,
        mock_config_values,
        mock_get_support_info,
        mock_wabizapi,
    ):
        support_info_file_path = log_utils.get_support_info()

        assert mocked_write_call.call_count == 1
        assert support_info_file_path == "wadebug_logs/support-info.log"

    @patch("wadebug.config.Config.values", return_value={"webapp": {}})
    @patch(
        "wadebug.wa_actions.wabiz_api.WABizAPI.__init__",
        side_exception=Exception("mock exception"),
    )
    def test_get_support_info_should_return_none_if_exception(
        self, mocked_config_call, mock_config_values
    ):
        support_info_file_path = log_utils.get_support_info()

        assert mocked_config_call.call_count == 1
        assert support_info_file_path is None
