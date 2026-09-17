class LinearModel:


    def __init__(
        self,
        weight: float,
        bias: float,
    ):

        self.weight = weight

        self.bias = bias


    def predict(
        self,
        x: float,
    ):

        return (
            self.weight * x
            + self.bias
        )
