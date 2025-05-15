from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring, OrMandatoryRefactoring


class LCOrGroupMandatoryFeature(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Or-group with mandatory feature'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[Feature]:
        return [f for f in fm.get_features() if is_or_group_with_mandatory(f)]

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return [OrMandatoryRefactoring]

def is_or_group_with_mandatory(feature: Feature) -> bool:
    or_group = next((r for r in feature.get_relations() if r.is_or()), None)
    return (or_group is not None and 
            any(r.children[0] in or_group.children for r in feature.get_relations() 
                if r.is_mandatory()))