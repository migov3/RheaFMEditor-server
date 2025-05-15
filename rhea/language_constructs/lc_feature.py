from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring


class LCFeature(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Feature'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[Feature]:
        return fm.get_features()

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return []