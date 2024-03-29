# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
from datetime import datetime, timezone
from os import path
from unittest.mock import patch

import pytest
from wadebug import exceptions
from wadebug.wa_actions import docker_utils, log_utils
from wadebug.wa_actions.tests.stubs.mock_wa_container import (
    MockWACoreappContainer,
    MockWAWebContainer,
)


class TestLogUtils(unittest.TestCase):
    @patch("os.access", return_value=True)
    @patch("os.makedirs", return_value=True)
    def test_should_makedir_if_have_access(self, mocked_makedirs_call, mock_access):
        log_utils.check_access()

        assert mocked_makedirs_call.call_count == 1

    @patch("wadebug.wa_actions.log_utils.datetime")
    def test_get_container_logs_start_end_datetimes_with_no_start_dt(
        self, mock_datetime
    ):
        mock_now = datetime(2019, 12, 19, 8, 22, 1)
        mock_datetime.now.return_value = mock_now
        mock_tz = timezone.utc
        mock_duration_hours = 2

        start_dt, end_dt = log_utils.get_container_logs_start_end_datetimes(
            "", "date_format", mock_tz, mock_duration_hours
        )

        assert start_dt == datetime(
            2019, 12, 19, mock_now.hour - mock_duration_hours, 22, 1
        )
        assert end_dt == mock_now

    def test_get_container_logs_start_end_datetimes_with_start_dt_str(self):
        mock_start_dt_str = "2019-12-19 08:22:01"
        mock_tz = timezone.utc
        mock_duration_hours = 4

        start_dt, end_dt = log_utils.get_container_logs_start_end_datetimes(
            mock_start_dt_str, "%Y-%m-%d %H:%M:%S", mock_tz, mock_duration_hours
        )

        assert start_dt == datetime(2019, 12, 19, 8, 22, 1, tzinfo=mock_tz)
        assert end_dt == datetime(
            2019, 12, 19, 8 + mock_duration_hours, 22, 1, tzinfo=mock_tz
        )

    def test_should_return_filepath_string_if_get_container_logs_has_no_exceptions(
        self,
    ):
        mock_container = MockWACoreappContainer()
        expected_container_logs_filepath = "filepath"

        with patch.object(
            docker_utils, "get_container_logs", return_value="This is a container log"
        ), patch.object(
            docker_utils, "write_to_file_in_binary", return_value=None
        ), patch.object(
            path, "join", return_value=expected_container_logs_filepath
        ):
            try:
                log_filepath = log_utils.get_container_logs(
                    mock_container, datetime.now(), datetime.now()
                )
            except Exception as e:
                pytest.fail(
                    "Unexpected Exception from log_utils.get_container_logs: \n {}".format(
                        e
                    )
                )
            assert log_filepath == expected_container_logs_filepath

    def test_should_return_filepath_string_if_get_container_inspect_logs_has_no_exceptions(
        self,
    ):
        mock_container = MockWAWebContainer()
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
        self,
    ):
        mock_container = MockWACoreappContainer()
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
        mocker_container = MockWAWebContainer()
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
        self,
    ):
        mock_container = MockWAWebContainer()
        expected_log_filepath = "/logs"

        with patch.object(
            log_utils,
            "copy_additional_logs_for_webcontainer",
            return_value=expected_log_filepath,
        ):
            try:
                (
                    webapp_log_filepath,
                    webapp_error_log_filepath,
                ) = log_utils.get_webcontainer_logs(mock_container)
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
        mocker_container = MockWACoreappContainer()
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
        docker_utils, "get_wa_containers", return_value=[MockWAWebContainer()]
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
            results = log_utils.get_logs(datetime.now(), datetime.now())
        except exceptions.LogsNotCompleteError:
            pytest.fail("Access error:  Cannot write logs to current directory")
        assert results == expected_logs_files

    @patch.object(docker_utils, "get_archive_from_container", return_value="Mock logs")
    @patch.object(docker_utils, "write_to_file", return_value=None)
    def test_should_write_webcontainer_log_to_file(
        self, mocked_write_call, mock_get_archive_from_container
    ):
        mock_container = MockWAWebContainer()

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
