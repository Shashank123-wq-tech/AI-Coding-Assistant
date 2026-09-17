def clean_numbers(values):

    return [
        value
        for value in values
        if value is not None
    ]


def calculate_mean(values):

    if not values:

        return 0

    return sum(values) / len(values)
