# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from wadebug.wa_actions import docker_utils


class TestGetWAContainerType:
    def test_should_return_type_if_is_wa_container(mocker):
        container_type = docker_utils.get_wa_container_type(
            MockContainer([docker_utils.WA_COREAPP_CONTAINER_TAG]))

        assert container_type == docker_utils.WA_COREAPP_CONTAINER_TAG

    def test_should_return_None_if_not_wa_container(mocker):
        container_type = docker_utils.get_wa_container_type(
            MockContainer(["a random image"]))

        assert not container_type


class TestGetWAContainers:
    def test_should_only_return_wa_containers(self, mocker):
        mock_containers = [
            MockContainer([docker_utils.WA_COREAPP_CONTAINER_TAG]),
            MockContainer([docker_utils.WA_WEBAPP_CONTAINER_TAG]),
            MockContainer(["a random image"])
        ]

        mocker.patch.object(
            docker_utils, 'get_all_containers', return_value=mock_containers)

        wa_containers = docker_utils.get_wa_containers()

        assert len(
            wa_containers) == 2, 'Expected to get exactly 2 WA containers'
        assert not mock_containers[2] in wa_containers, 'Non-WA containers should not be returned'


class TestGetRunningWAContainers:
    def test_should_only_return_running_containers(self, mocker):
        mock_containers = [
            docker_utils.WAContainer(
                MockContainer([], 'running'), 'container_type'),
            docker_utils.WAContainer(
                MockContainer([], 'stopped'), 'container_type'),
            docker_utils.WAContainer(
                MockContainer([], 'running'), 'container_type')
        ]
        mocker.patch.object(
            docker_utils, 'get_wa_containers', return_value=mock_containers)

        running_wa_containers = docker_utils.get_running_wa_containers()

        assert len(running_wa_containers
                   ) == 2, 'Expected exactly 2 containers to be running'
        assert not mock_containers[1] in running_wa_containers, 'Non-running containers should not be returned'


class TestGetRunningWAContainersByType:
    def test_should_only_return_containers_of_certain_type(self, mocker):
        mock_containers = [
            docker_utils.WAContainer(
                MockContainer([], 'running'), 'container_type_1'),
            docker_utils.WAContainer(
                MockContainer([], 'running'), 'container_type_2')
        ]
        mocker.patch.object(
            docker_utils,
            'get_running_wa_containers',
            return_value=mock_containers)

        filtered_wa_containers = docker_utils.get_running_wa_containers_by_type(
            'container_type_1')

        assert len(filtered_wa_containers
                   ) == 1, 'Expected exactly 1 container to match the type'
        assert mock_containers[0].container in filtered_wa_containers


class MockContainer:
    def __init__(self, repo_tags, status='running'):
        self.image = MockContainerImage(repo_tags)
        self.status = status


class MockContainerImage:
    def __init__(self, repo_tags):
        self.attrs = {'RepoTags': repo_tags}
