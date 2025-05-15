from flamapy.metamodels.fm_metamodel.models import FeatureModel, Constraint

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring, SplitConstraint


class LCPseudoComplexConstraint(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Pseudo-complex constraint'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[Constraint]:
        return SplitConstraint.get_instances(fm)

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return [SplitConstraint]