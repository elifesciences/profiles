from profiles.models import Name


def test_it_can_be_printed():
    name1 = Name('given names', 'family name')
    name2 = Name('given names')

    assert repr(name1) == "<Name 'given names' 'family name'>"
    assert repr(name2) == "<Name 'given names'>"


def test_it_casts_to_a_string():
    name1 = Name('given names', 'family name')
    name2 = Name('given names')

    assert str(name1) == 'given names family name'
    assert str(name2) == 'given names'


def test_it_has_given_names():
    name = Name('given names', 'family name')

    assert name.given_names == 'given names'


def test_it_may_have_a_family_name():
    has = Name('given names', 'family name')
    has_not = Name('given names')

    assert has.family_name == 'family name'
    assert has_not.family_name is None


def test_it_can_be_compared():
    name = Name('given names', 'family name')
    name1 = Name('given names', 'family name')
    name2 = Name('someone', 'else')
    name3 = Name('someone')
    name4 = Name('someone')

    assert name == name1
    assert name != name2
    assert name != name3
    assert name3 == name4
