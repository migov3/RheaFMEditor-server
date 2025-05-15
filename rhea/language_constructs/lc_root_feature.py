from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring


class RootFeature(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Root feature'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[Feature]:
        return [fm.root]

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return []