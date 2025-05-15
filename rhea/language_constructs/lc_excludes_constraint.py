from flamapy.metamodels.fm_metamodel.models import FeatureModel, Constraint

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring, EliminationSimpleConstraintsExcludes


class LCExcludesConstraint(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Excludes constraint'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[Constraint]:
        return EliminationSimpleConstraintsExcludes.get_instances(fm)

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return [EliminationSimpleConstraintsExcludes]