from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring


class LCOptionalFeature(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Optional feature'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[Feature]:
        return [f for f in fm.get_features() if f.is_optional()]

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return []