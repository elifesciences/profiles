from profiles.utilities import remove_none_values


def test_it_removes_none_values():
    input = {'foo': 'bar', 'baz': None, 'test': None}

    output = remove_none_values(input)

    assert output == {'foo': 'bar'}
