from flamapy.metamodels.fm_metamodel.models import FeatureModel, Constraint

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring, EliminationComplexConstraints


class LCStrictComplexConstraint(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Strict-complex constraint'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[Constraint]:
        return EliminationComplexConstraints.get_instances(fm)

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return [EliminationComplexConstraints]