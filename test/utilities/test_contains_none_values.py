import pytest

from profiles.utilities import contains_none_values

EMPTY_DICT = {}
DICT_WITH_NONE_VALUE = {'test': None}
DICT_WITH_NESTED_DICTS_WITHOUT_NONE_VALUE = {'test': {'test': {'test': 1}}}
DICT_WITH_NESTED_DICTS_WITH_NONE_VALUE = {'test': {'test': {'test': 1},
                                                   'this': {'test': None}}
                                          }
DICT_WITH_NESTED_DICTS_WITH_NONE_VALUE_AND_FOLLOWING_VALUES = {
    'test': {'test': {'test': 1},
             'this': {'test': {'test': 'this'}},
             'and': {'test': {'test': None}},
             'that': {'test': 2}}
}
DICT_WITH_NESTED_DICT_AND_LIST_WITH_NONE_VALUE = {
    'test': {'test': [1, None, 3]}}

LIST_WITH_NONE_VALUE = [1, '2', None, 4]
LIST_WITHOUT_NONE_VALUE = [1, '2', '3', 4]
LIST_WITH_NESTED_LISTS_WITH_NONE_VALUE_AND_FOLLOWING_VALUES = [
    1,
    [1, 2, 3],
    [1, 2, [1,
            2,
            None]
     ],
    [1, 2, 3],
    4]


@pytest.mark.parametrize('input, expected_result', [
    (EMPTY_DICT, False),
    (DICT_WITH_NONE_VALUE, True),
    (DICT_WITH_NESTED_DICTS_WITHOUT_NONE_VALUE, False),
    (DICT_WITH_NESTED_DICTS_WITH_NONE_VALUE, True),
    (DICT_WITH_NESTED_DICTS_WITH_NONE_VALUE_AND_FOLLOWING_VALUES, True),
    (DICT_WITH_NESTED_DICT_AND_LIST_WITH_NONE_VALUE, True),
    (LIST_WITH_NONE_VALUE, True),
    (LIST_WITHOUT_NONE_VALUE, False),
    (LIST_WITH_NESTED_LISTS_WITH_NONE_VALUE_AND_FOLLOWING_VALUES, True)
])
def test_contains_none_values(input, expected_result) -> None:
    assert contains_none_values(input) is expected_result
