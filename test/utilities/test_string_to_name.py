from profiles.models import Name
from profiles.utilities import string_to_name


def test_it_turns_a_string_into_a_name():
    output1 = string_to_name('foo bar')
    output2 = string_to_name('foo')

    assert output1 == Name('foo')
    assert output2 == Name('foo', 'bar')


def test_it_assumes_multiple_words_are_part_of_the_family_name():
    output = string_to_name('foo bar baz qux')

    assert output == Name('foo', 'bar baz qux')
