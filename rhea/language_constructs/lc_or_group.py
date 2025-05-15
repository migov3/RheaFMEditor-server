from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring


class LCOrGroupFeature(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Or-group'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[Feature]:
        return [f for f in fm.get_features() if f.is_or_group()]

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return []