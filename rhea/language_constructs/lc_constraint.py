from flamapy.metamodels.fm_metamodel.models import FeatureModel, Constraint

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring


class LCConstraint(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Cross-tree constraint'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[Constraint]:
        return fm.get_constraints()

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return []