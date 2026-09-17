from main import home


def test_home():

    result = home()

    assert result["message"] == "Hello World"
