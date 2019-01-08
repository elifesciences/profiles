from profiles.utilities import dict_contains_none_values


def test_dict_contains_none_values() -> None:
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

    assert dict_contains_none_values(dict_1) is False
    assert dict_contains_none_values(dict_2) is True
    assert dict_contains_none_values(dict_3) is False
    assert dict_contains_none_values(dict_4) is True
    assert dict_contains_none_values(dict_5) is True
