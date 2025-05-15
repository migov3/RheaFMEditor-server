from typing import Any
from abc import ABC, abstractmethod

from flamapy.metamodels.fm_metamodel.models import FeatureModel

from rhea.refactorings import FMRefactoring


class LanguageConstruct(ABC):

    @staticmethod
    @abstractmethod
    def name() -> str:
        """Name of the language construct."""
        pass

    @staticmethod
    @abstractmethod
    def get_instances(fm: FeatureModel) -> list[Any]:
        """Return the instances of this language construct in the given feature model."""
        pass

    @staticmethod
    @abstractmethod
    def get_refactorings() -> list[FMRefactoring]:
        """Return the available refactorings to this language construct."""
        pass