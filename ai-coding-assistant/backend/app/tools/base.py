from abc import ABC, abstractmethod


class Tool(ABC):

    name: str = "tool"


    @abstractmethod
    def run(
        self,
        **kwargs,
    ):

        raise NotImplementedError
