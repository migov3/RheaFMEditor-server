from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring


class LCNonUniqueFeature(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Non-unique feature'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[str]:
        features = fm.get_features()
        unique_features = set(features)
        for feature in unique_features:
            features.remove(feature)
        non_unique_features = {f.name for f in features}
        return non_unique_features

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return []