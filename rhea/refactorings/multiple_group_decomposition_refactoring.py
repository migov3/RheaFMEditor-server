from typing import Any

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation

from rhea.refactorings import FMRefactoring
from rhea.refactorings import utils


class MultipleGroupDecompositionRefactoring(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Multiple decomposition types refactoring'
    
    @staticmethod
    def get_description() -> str:
        return ("It substitutes each group in the feature by a mandatory abstract feature which "
                "becomes a new group below the original feature.")

    @staticmethod
    def get_language_construct_name() -> str:
        return 'Multiple decomposition types'
    
    @staticmethod
    def get_instances(model: FeatureModel) -> list[Any]:
        return [f for f in model.get_features() if is_multiple_group_decomposition(f)]

    @staticmethod
    def is_applicable(model: FeatureModel) -> bool:
        return True

    @staticmethod
    def transform(model: FeatureModel, instance: Feature) -> FeatureModel:
        if instance is None:
            raise Exception(f'There is not feature with name "{instance.name}".')
        if not is_multiple_group_decomposition(instance):
            raise Exception(f'Feature {instance.name} is not a multiple group decomposition.')

        for relation in instance.get_relations():
            if relation.is_group():
                model = new_decomposition(model, instance, relation)
        return model


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


def new_decomposition(fm: FeatureModel, feature: Feature, r_group: Relation) -> FeatureModel:
    new_name = utils.get_new_feature_name(fm, feature.name)
    f_p = Feature(name=new_name, parent=feature, is_abstract=True)
    r_mand = Relation(feature, [f_p], 1, 1)  # mandatory
    feature.add_relation(r_mand)
    r_group.parent = f_p
    for child in r_group.children:
        child.parent = f_p
    # Add relations to features
    f_p.add_relation(r_group)
    feature.get_relations().remove(r_group)
    return fm
