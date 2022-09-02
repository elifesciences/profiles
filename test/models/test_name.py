from hypothesis import given
from hypothesis.strategies import text

from profiles.models import Name


@given(text())
def test_it_can_be_printed(name_text):
    name = Name(name_text)

    assert repr(name) == "<Name {!r}>".format(name_text)


@given(text())
def test_it_casts_to_a_string(name_text):
    name = Name(name_text)

    assert str(name) == name_text


@given(text())
def test_it_has_a_preferred_name(name_text):
    name = Name(name_text)

    assert name.preferred == name_text


@given(text(), text())
def test_it_has_an_index_name(name_text, name_text2):
    name = Name(name_text, name_text2)

    assert name.index == name_text2


def test_it_guesses_the_index_name():
    name = Name("Foo Bar")

    assert name.index == "Bar, Foo"


def test_it_can_be_compared():
    name = Name("Foo Bar")
    name1 = Name("Foo Bar", "Bar, Foo")
    name2 = Name("Foo Bar", "Bar, Foo")
    name3 = Name("Bar Foo")

    assert name == name1
    assert name == name2
    assert name != name3
