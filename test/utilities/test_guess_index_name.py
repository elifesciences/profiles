from profiles.utilities import guess_index_name


def test_it_turns_a_name_into_an_index_name():
    output1 = guess_index_name("foo bar")
    output2 = guess_index_name("foo")

    assert output1 == "bar, foo"
    assert output2 == "foo"


def test_it_assumes_multiple_words_are_part_of_the_family_name():
    output = guess_index_name("foo bar baz qux")

    assert output == "bar baz qux, foo"
