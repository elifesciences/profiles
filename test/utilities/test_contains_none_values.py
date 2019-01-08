from profiles.utilities import contains_none_values


def test_contains_none_values() -> None:
    dict_1 = {}
    dict_2 = {'test': None}
    dict_3 = {'test': {'test': {'test': 1}}}
    dict_4 = {'test': {'test': {'test': 1},
                       'this': {'test': None}}
              }
    dict_5 = {'test': {'test': {'test': 1},
                       'this': {'test': {'test': 'this'}},
                       'and': {'test': {'test': None}},
                       'that': {'test': 2}
                       }
              }
    list_1 = [1, '2', None, 4]
    list_2 = [1, '2', '3', 4]
    list_3 = [1,
              [1, 2, 3],
              [1, 2, [
                  1, 2, None
              ]],
              [1, 2, 3],
              4]

    assert contains_none_values(dict_1) is False
    assert contains_none_values(dict_2) is True
    assert contains_none_values(dict_3) is False
    assert contains_none_values(dict_4) is True
    assert contains_none_values(dict_5) is True
    assert contains_none_values(list_1) is True
    assert contains_none_values(list_2) is False
    assert contains_none_values(list_3) is True
