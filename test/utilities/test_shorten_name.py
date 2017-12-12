import pytest

from profiles.utilities import shorten_name

name_fixtures = (
    {'given': 'Francisco', 'family': 'Baños', 'short': 'F. Baños'},
    {'given': 'Verónica', 'family': 'López López', 'short': 'V. López López'},
    {'given': 'Татьяна', 'family': 'Яковлева', 'short': 'Т. Яковлева'},
    {'given': '璞玉', 'family': '田', 'short': '璞. 田'},
    {'given': 'jian', 'family': 'yilang', 'short': 'j. yilang'},
    # {'given': 'السيد محمد', 'family': 'وردة أحمد', 'short': 'وردة أحمد .د'},
    {
        'given': 'Francisco Javier',
        'family': 'Cuevas-de-la-Rosa',
        'short': 'F. Cuevas-de-la-Rosa'
    },
    {
        'given': 'MARIA ISABEL',
        'family': 'GONZALEZ SANCHEZ',
        'short': 'M. GONZALEZ SANCHEZ'
    },
    {
        'given': 'Patrícia Andreia Pimenta de Castro',
        'family': 'Martins',
        'short': 'P. Martins'
    },
    {
        'given': 'Luis J',
        'family': 'Fernández-Clemente Martín-Orozco',
        'short': 'L. Fernández-Clemente Martín-Orozco'
    },
    {
        'given': 'Alexandra',
        'family': 'Imaculada de Oliveira e Medeiros',
        'short': 'A. Imaculada de Oliveira e Medeiros'
    },
)


@pytest.mark.parametrize('name', name_fixtures)
def test_it_can_shorten_name(name):
    short_name = shorten_name(name['given'], name['family'])
    assert short_name == name['short']
