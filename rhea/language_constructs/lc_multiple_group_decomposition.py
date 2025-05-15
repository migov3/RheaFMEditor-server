from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation

from rhea.language_constructs import LanguageConstruct 
from rhea.refactorings import FMRefactoring, MultipleGroupDecompositionRefactoring


class LCMultipleGroupDecomposition(LanguageConstruct):

    @staticmethod
    def name() -> str:
        return 'Multiple group decomposition'

    @staticmethod
    def get_instances(fm: FeatureModel) -> list[Feature]:
        return [f for f in fm.get_features() if is_multiple_group_decomposition(f)]

    @staticmethod
    def get_refactorings() -> list[FMRefactoring]:
        return [MultipleGroupDecompositionRefactoring]


def is_multiple_group_decomposition(feature: Feature) -> bool:
    children_of_groups = []
    groups_relations = []
    ands_relations = []
    children_of_ands = []
    for relation in feature.get_relations():
        if relation.is_group():
            groups_relations.append(relation)
            children_of_groups.extend(relation.children)
        else:
            ands_relations.append(relation)
            children_of_ands.extend(relation.children)
    return (len(groups_relations) > 1 or
            (len(groups_relations) > 0 and len(ands_relations) > 0 and 
             not any(c in children_of_groups for c in children_of_ands))
           )
