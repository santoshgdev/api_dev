import pytest

from utils.cloud_utils import create_resource_path


@pytest.mark.parametrize(
    "project_id, service, name, expected_output",
    [("project1", "secrets", "test", "projects/project1/secrets/test/versions/latest")],
)
def test_create_resource_path(project_id, service, name, expected_output):
    assert expected_output == create_resource_path(project_id, service, name)
