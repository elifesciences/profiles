from abc import ABC, abstractmethod


class CanBeCleared(ABC):
    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError
