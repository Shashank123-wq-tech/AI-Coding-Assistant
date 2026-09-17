from model import LinearModel


def test_prediction():

    model = LinearModel(
        weight=2.0,
        bias=1.0,
    )

    assert model.predict(
        3.0
    ) == 7.0
