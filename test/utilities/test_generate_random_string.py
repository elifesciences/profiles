import re

from profiles.utilities import generate_random_string


def test_it_generates_a_random_string():
    output = generate_random_string(8)

    pattern = re.compile('^[A-Za-z0-9]{8}$')
    assert pattern.match(output) is not None


def test_it_generates_a_random_string_of_a_set_length():
    output = generate_random_string(5)

    pattern = re.compile('^[A-Za-z0-9]{5}$')
    assert pattern.match(output) is not None


def test_it_generates_a_random_string_of_set_characters():
    output = generate_random_string(8, 'ABCabc')

    pattern = re.compile('^[A-Ca-c]{8}$')
    assert pattern.match(output) is not None
