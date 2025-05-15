from flamapy.metamodels.fm_metamodel.models import FeatureModel, Constraint

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring, EliminationSimpleConstraintsRequires


class LCRequiresConstraint(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Requires constraint'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[Constraint]:
        return EliminationSimpleConstraintsRequires.get_instances(fm)

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return [EliminationSimpleConstraintsRequires]