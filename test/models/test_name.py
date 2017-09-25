from profiles.models import Name


def test_it_can_be_printed():
    name = Name('Foo Bar')

    assert repr(name) == "<Name 'Foo Bar'>"


def test_it_casts_to_a_string():
    name = Name('Foo Bar')

    assert str(name) == 'Foo Bar'


def test_it_has_a_preferred_name():
    name = Name('Foo Bar')

    assert name.preferred == 'Foo Bar'


def test_it_has_an_index_name():
    name = Name('Foo Bar', 'Bar, Foo')

    assert name.index == 'Bar, Foo'


def test_it_guesses_the_index_name():
    name = Name('Foo Bar')

    assert name.index == 'Bar, Foo'


def test_it_can_be_compared():
    name = Name('Foo Bar')
    name1 = Name('Foo Bar', 'Bar, Foo')
    name2 = Name('Foo Bar', 'Bar, Foo')
    name3 = Name('Bar Foo')

    assert name == name1
    assert name == name2
    assert name != name3
