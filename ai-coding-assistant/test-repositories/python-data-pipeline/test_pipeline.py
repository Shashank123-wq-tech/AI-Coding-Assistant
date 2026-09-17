from pipeline import (
    clean_numbers,
    calculate_mean,
)


def test_clean_numbers():

    values = [
        1,
        None,
        2,
        None,
        3,
    ]

    assert clean_numbers(
        values
    ) == [
        1,
        2,
        3,
    ]


def test_mean():

    assert calculate_mean(
        [1, 2, 3]
    ) == 2
