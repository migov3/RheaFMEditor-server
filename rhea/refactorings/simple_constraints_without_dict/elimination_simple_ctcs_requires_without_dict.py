import copy
from ctypes import util
from hashlib import new
from logging import root
from msilib.schema import FeatureComponents
from numbers import Real
from pyexpat import model
from typing import Any, List

from flamapy.core.models.ast import AST, ASTOperation, Node
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, Constraint

from rhea.metamodels.fm_metamodel.models import FM, ConstraintHelper
from rhea.refactorings import FMRefactoring
from rhea.refactorings import utils


class EliminationSimpleConstraintsRequiresWithoutDict(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Elimination of Constraints from Feature Trees WITHOUT DICT - Requires'

    @staticmethod
    def get_instances(model: FeatureModel) -> list[Constraint]:
        return [ctc for ctc in model.get_constraints() if ConstraintHelper(ctc).is_requires_constraint()]

    @staticmethod
    def transform(model: FeatureModel, instance: Constraint) -> FeatureModel:
        if instance is None:
            raise Exception(f'There is not constraint with name "{str(instance)}".')
        if not ConstraintHelper(instance).is_requires_constraint():
            raise Exception(f'Operator {str(instance)} is not requires.')

        model_plus = copy.deepcopy(model)  # copy.deepcopy(model)
        model_less = copy.deepcopy(model)

        right_feature_name_ctc = instance.ast.root.right.data
        right_feature_ctc_plus = model_plus.get_feature_by_name(right_feature_name_ctc)
        if right_feature_ctc_plus is None:
            for f in model_plus.get_features():
                while hasattr(f, 'reference'):
                    f = f.reference
                if f.name==right_feature_name_ctc:
                    right_feature_ctc_plus = f
                    break
        xor_plus = Feature(utils.get_new_feature_name(model_plus, 'XOR'), is_abstract=True)
        list_right_feature_ctc_plus = get_features_reference(model_plus, right_feature_ctc_plus)

        right_feature_ctc_less = model_less.get_feature_by_name(right_feature_name_ctc)
        if right_feature_ctc_less is None:
            for f in model_less.get_features():
                while hasattr(f, 'reference'):
                    f = f.reference
                if f.name==right_feature_name_ctc:
                    right_feature_ctc_less = f
                    break
        list_right_feature_ctc_less = get_features_reference(model_less, right_feature_ctc_less)

        if instance.ast.root.data in [ASTOperation.REQUIRES, ASTOperation.IMPLIES]:
            left_feature_name_ctc = instance.ast.root.left.data
        elif instance.ast.root.data is ASTOperation.OR:
            not_operation = instance.ast.root.left
            left_feature_name_ctc = not_operation.left.data
        left_feature_ctc_less = model_less.get_feature_by_name(left_feature_name_ctc)
        if left_feature_ctc_less is None:
            for f in model_less.get_features():
                while hasattr(f, 'reference'):
                    f = f.reference
                if f.name==left_feature_name_ctc:
                    left_feature_ctc_less = f
                    break
        list_left_feature_ctc_less = get_features_reference(model_less, left_feature_ctc_less)

        plus_roots = []
        for f_plus in list_right_feature_ctc_plus:
            new_model_plus = copy.deepcopy(model)
            if hasattr(f_plus, 'reference') and new_model_plus is not None:
                new_f_plus = new_model_plus.get_feature_by_name(f_plus.name)
                model_plus = utils.add_node_to_tree(new_model_plus, new_f_plus)
            elif model_plus is not None:
                model_plus = utils.add_node_to_tree(model_plus, f_plus)
            if model_plus is not None:
                old_root = model_plus.root
                model_plus = remove_abstract_child(model_plus, old_root)
                if old_root != model_plus.root:
                    new_rel = Relation(old_root, [model_plus.root], 1, 1)  # mandatory
                    old_root.add_relation(new_rel)
                    model_plus.root.parent = old_root
                plus_roots.append(model_plus.root)
        
        # Joining all trees with XOR
        if len(list_right_feature_ctc_plus)>1:
            r_xor_plus = Relation(xor_plus, plus_roots, 1, 1)  # XOR
            xor_plus.add_relation(r_xor_plus)
            model_plus.root = xor_plus
            for child in plus_roots:
                child.parent = xor_plus
            count = 1
            for r in xor_plus.get_children():
                r.name = f'{utils.get_new_feature_name(model, r.name)}{count}'
                count += 1

        for f_left_less in list_left_feature_ctc_less:
            if model_less is not None:
                model_less = utils.eliminate_node_from_tree(model_less, f_left_less)

        for f_right_less in list_right_feature_ctc_less:
            if model_less is not None:
                model_less = utils.eliminate_node_from_tree(model_less, f_right_less)


        # Construct T(+B) and T(-A-B).
        if model_plus is not None and model_less is not None:
            # If both trees are not equal to NIL, then the result consists of a new root, which
            # is an Xor feature, with subfeatures T(+B) and T(-A-B).
            new_root = Feature(utils.get_new_feature_name(model, 'root'), is_abstract=True)
            rel = Relation(new_root, [model_plus.root, model_less.root], 1, 1)  #XOR
            new_root.add_relation(rel)
            model.root = new_root
            model_plus.root.parent = new_root
            model_less.root.parent = new_root
        elif model_less is None:
            # If T(-A-B) is equal to NIL, then the result is T(+B).
            model = model_plus
        elif model_plus is None:
            # If T(+B) is equal to NIL, then the result is T(-A-B). 
            model = model_less

        model.ctcs.remove(instance)

        # Changing names to avoid duplicates
        # CUIDADO!!! (puede que haya que modificarlo)
        if model_less is not None and model_plus is not None:
            for feature in model_less.get_features():
                if feature in model_plus.get_features():
                    feature_reference = model.get_feature_by_name(feature.name)
                    feature.name = utils.get_new_feature_name(model, feature.name)
                    if feature != feature_reference:
                        feature.reference = feature_reference

        #if hasattr(model, 'dict_references'):
        #    feature_original = model.dict_references['A1']
        return model



def get_features_reference(fm: FeatureModel, feature: Feature) -> list[Feature]:
    features = [feature]
    for new_feature in fm.get_features():
        feature_with_attr = new_feature
        while hasattr(feature_with_attr, 'reference'):
            feature_with_attr = feature_with_attr.reference
        if hasattr(new_feature, 'reference') and feature_with_attr == feature:
            features.append(new_feature)
    return features

def remove_abstract_child(fm: FeatureModel, feature: Feature) -> FeatureModel:
    feature_relations = feature.get_relations()
    feature_next_rel = next(r for r in feature_relations)
    feature_next_abstract = next(c for c in feature.get_children())
    if len(feature_relations)==1 and feature_next_rel.is_mandatory() and feature_next_abstract.is_abstract:
            feature.get_relations().remove(feature_next_rel)
            fm.root = feature_next_abstract
            fm = remove_abstract_child(fm, feature_next_abstract)
    return fm