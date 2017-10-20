import pytest

from profiles.exceptions import SchemaNotFound
from profiles.utilities import validate_json


def test_it_can_validate_against_schema():
    data = {
        'name': {'preferred': 'some_user'}
    }
    schema_dir = 'test/schema'

    assert validate_json(data, schema_name='dummy_schema', schema_dir=schema_dir) is True


def test_it_will_fail_to_validate_with_invalid_data():
    data = {'somevalue': 'invalid'}
    schema_dir = 'test/schema'

    assert validate_json(data, schema_name='dummy_schema', schema_dir=schema_dir) is False


def test_it_will_handle_schema_not_found_error():
    data = {
        'name': {'preferred': 'some_user'}
    }

    with pytest.raises(SchemaNotFound):
        validate_json(data, schema_name='invalid_schema_path')
