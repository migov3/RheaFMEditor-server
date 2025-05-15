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


class NewNamesEliminationSimpleConstraintsRequires(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Elimination of Constraints from Feature Trees - Requires (changing names)'

    @staticmethod
    def get_instances(model: FeatureModel) -> list[Feature]:
        return [ctc for ctc in model.get_constraints() if ConstraintHelper(ctc).is_requires_constraint()]

    @staticmethod
    def transform(model: FeatureModel, instance: Constraint) -> FeatureModel:
        if instance is None:
            raise Exception(f'There is not constraint with name "{str(instance)}".')
        if not ConstraintHelper(instance).is_requires_constraint():
            raise Exception(f'Operator {str(instance)} is not requires.')

        print(f'MODELO: {model}')
        model_plus = copy.deepcopy(model)
        model_less = copy.deepcopy(model)

        right_feature_name_ctc = instance.ast.root.right.data
        right_feature_ctc_plus = model_plus.get_feature_by_name(right_feature_name_ctc)
        xor_plus = Feature(utils.get_new_feature_name(model_plus, 'XOR'), is_abstract=True)
        [f for f in model.get_features() if f.name == ]
        list_right_feature_ctc_plus = get_features_reference(model_plus, right_feature_ctc_plus)
        print(f'RIGHT FEATURES PLUS: {[str(f) for f in list_right_feature_ctc_plus]}')
        right_feature_ctc_less = model_less.get_feature_by_name(right_feature_name_ctc)
        # xor_right_less = Feature(utils.get_new_feature_name(model_plus, 'XOR'), is_abstract=True)
        list_right_feature_ctc_less = get_features_reference(model_less, right_feature_ctc_less)
        print(f'RIGHT FEATURES LESS: {[str(f) for f in list_right_feature_ctc_less]}')

        left_feature_name_ctc = instance.ast.root.left.data
        left_feature_ctc_less = model_less.get_feature_by_name(left_feature_name_ctc)
        if left_feature_ctc_less is None:
            left_feature_ctc_less = next(f for f in model_less.get_features() if hasattr(f, 'reference') and f.reference.name==left_feature_name_ctc)
            while hasattr(left_feature_ctc_less, 'reference'):
                left_feature_ctc_less = left_feature_ctc_less.reference
            print(f'FEATURE REFERENCE FOR MODEL LESS: {left_feature_ctc_less.name}')
        # xor_left_less = Feature(utils.get_new_feature_name(model_plus, 'XOR'), is_abstract=True)
        list_left_feature_ctc_less = get_features_reference(model_less, left_feature_ctc_less)
        print(f'LEFT FEATURES LESS: {[str(f) for f in list_left_feature_ctc_less]}')


        # if model_plus is not None:
        #     for feature_plus in model_plus.get_features():
        #         if hasattr(feature_plus, 'reference'):
        #             print(f'ATRIBUTO DE {feature_plus} en model plus: {getattr(feature_plus, "reference")}')
        #             feature_plus.name = feature_plus.reference.name
        plus_roots = []
        for f_plus in list_right_feature_ctc_plus:
            new_model_plus = copy.deepcopy(model)
            if hasattr(f_plus, 'reference') and new_model_plus is not None:
                new_f_plus = new_model_plus.get_feature_by_name(f_plus.name)
                # print(f'NEW MODEL PLUS: {new_model_plus}')
                model_plus = utils.add_node_to_tree(new_model_plus, new_f_plus)
            elif model_plus is not None:
                model_plus = utils.add_node_to_tree(model_plus, f_plus)
            if model_plus is not None:
                # if model_plus.root in plus_roots:
                #     print(f'MODEL PLUS ROOT NAME: {model_plus.root.name}')
                #     model_plus.root.name = utils.get_new_feature_name(model, model_plus.root.name)
                #     print(f'MODEL PLUS ROOT NAME: {model_plus.root.name}')
                old_root = model_plus.root
                model_plus = remove_abstract_child(model_plus, old_root)
                if old_root != model_plus.root:
                    new_rel = Relation(old_root, [model_plus.root], 1, 1)  # mandatory
                    old_root.add_relation(new_rel)
                plus_roots.append(model_plus.root)
            print(f'T(+{f_plus}): {model_plus}')



        if len(list_right_feature_ctc_plus)>1:
            r_xor_plus = Relation(xor_plus, plus_roots, 1, 1)  # XOR
            xor_plus.add_relation(r_xor_plus)
            model_plus.root = xor_plus
            count = 1
            for r in xor_plus.get_children():
                r.name = f'{r.name}{count}'
                count += 1
            print(f'T(+{[str(f) for f in list_right_feature_ctc_plus]}): {model_plus}')





        # print('----my relations PLUS-----')
        # for r in model_plus.get_relations():
        #     print(f'Relation (plus): ({str(r)})')
        

        # print(f'FEATURES DE MODEL LESS 1: {[str(f) for f in model_less.get_features()]}')
        # if model_less is not None:
        #     for feature_less in model_less.get_features():
        #         if hasattr(feature_less, 'reference'):
        #             print(f'ATRIBUTO DE {feature_less} en model less 1: {getattr(feature_less, "reference")}')
        #             feature_less.name = feature_less.reference.name
        less_left_roots = []
        for f_left_less in list_left_feature_ctc_less:
            # new_model_less = copy.deepcopy(model)
            # if hasattr(f_left_less, 'reference') and new_model_less is not None:
            #     new_f_left_less = new_model_less.get_feature_by_name(f_left_less.name)
            #     print(f'NEW MODEL LESS 1: {new_model_less}')
            #     model_less = utils.eliminate_node_from_tree(new_model_less, new_f_left_less)
            if model_less is not None:
                model_less = utils.eliminate_node_from_tree(model_less, f_left_less)
            if model_less is not None:
                less_left_roots.append(model_less.root)
            print(f'T(-{f_left_less}): {model_less}')
        # if len(list_left_feature_ctc_less)>1:
        #     r_xor_left_less = Relation(xor_left_less, less_left_roots, 1, 1)  #XOR
        #     xor_left_less.add_relation(r_xor_left_less)
        #     model_less.root = xor_left_less
        # print(f'T(-{[str(f) for f in list_left_feature_ctc_less]}): {model_less}')
        # print('----my relations LESS 1-----')
        # for r in model_less.get_relations():
        #     print(f'Relation (less): ({r.parent}, {[f.name for f in r.children]}, {r.card_min}, {r.card_max})')
        
        

        # print(f'FEATURES DE MODEL LESS 2: {[str(f) for f in model_less.get_features()]}')
        # if model_less is not None:
        #     for feature_less in model_less.get_features():
        #         if hasattr(feature_less, 'reference'):
        #             print(f'ATRIBUTO DE {feature_less} en model less 2: {getattr(feature_less, "reference")}')
        #             feature_less.name = feature_less.reference.name
        less_right_roots = []
        for f_right_less in list_right_feature_ctc_less:
            if model_less is not None:
                model_less = utils.eliminate_node_from_tree(model_less, f_right_less)
            if model_less is not None:
                less_right_roots.append(model_less.root)
            print(f'T(-{f_right_less}): {model_less}')
        # if len(list_right_feature_ctc_less)>1:
        #     r_xor_right_less = Relation(xor_right_less, less_right_roots, 1, 1)  #XOR
        #     xor_right_less.add_relation(r_xor_right_less)
        #     model_less.root = xor_right_less
        # print(f'T(-{[str(f) for f in list_right_feature_ctc_less]}): {model_less}')
        # print('----my relations LESS 2-----')
        # for r in model_less.get_relations():
        #     print(f'Relation (less): ({r.parent}, {[f.name for f in r.children]}, {r.card_min}, {r.card_max})')
        
        
        # for feature in list_right_feature_ctc_plus:
        #     if model_plus is not None:
        #         model_plus = utils.add_node_to_tree(model_plus, feature)
        # for feature in list

        # if model_plus is not None:
        #     model_plus = utils.add_node_to_tree(model_plus, right_feature_ctc_plus)
        # print(f'T(+{right_feature_ctc_plus}): {model_plus}')
        # if model_less is not None:
        #     model_less = utils.eliminate_node_from_tree(model_less, left_feature_ctc_less)
        # print(f'T(-{left_feature_ctc_less}): {model_less}')
        # if model_less is not None:
        #     model_less = utils.eliminate_node_from_tree(model_less, right_feature_ctc_less)
        # print(f'T(-{right_feature_ctc_less}): {model_less}')


        # Construct T(+B) and T(-A-B).
        if model_plus is not None and model_less is not None:
            # If both trees are not equal to NIL, then the result consists of a new root, which
            # is an Xor feature, with subfeatures T(+B) and T(-A-B).
            new_root = Feature(utils.get_new_feature_name(model, 'root'), is_abstract=True)
            rel = Relation(new_root, [model_plus.root, model_less.root], 1, 1)  #XOR
            new_root.add_relation(rel)
            model.root = new_root
        elif model_less is None:
            # If T(-A-B) is equal to NIL, then the result is T(+B).
            model = model_plus
        elif model_plus is None:
            # If T(+B) is equal to NIL, then the result is T(-A-B). 
            model = model_less

        # print('----my relations MODEL FINAL-----')
        # for r in model.get_relations():
        #     print(f'Relation (less): ({r.parent}, {[f.name for f in r.children]}, {r.card_min}, {r.card_max})')

        model.ctcs.remove(instance)







        # Changing names to avoid duplicates
        # CUIDADO!!! (puede que haya que modificarlo)
        

        # Changing names to avoid duplicates
        # for feature in model.get_features():
        #     model = changing_names(model, feature)

        
        if model_less is not None and model_plus is not None:
            for feature in model_less.get_features():
                if feature in model_plus.get_features():
                    feature_reference = model.get_feature_by_name(feature.name)
                    feature.name = utils.get_new_feature_name(model, feature.name)
                    if feature != feature_reference:
                        feature.reference = feature_reference





        # for feature in model.get_features():
        #     feature_reference = model.get_feature_by_name(feature.name)
        #     feature.name = utils.get_new_feature_name(model, feature.name)
        #     feature.reference = feature_reference

        # print('----my relations MODEL FINAL (new names-----')
        # for r in model.get_relations():
        #     print(f'Relation (less): ({r.parent}, {[f.name for f in r.children]}, {r.card_min}, {r.card_max})')

        return model



def get_features_reference(fm: FeatureModel, feature: Feature) -> list[Feature]:
    features = [feature]
    for new_feature in fm.get_features():
        feature_with_attr = new_feature
        while hasattr(feature_with_attr, 'reference'):
            feature_with_attr = feature_with_attr.reference
        if hasattr(new_feature, 'reference') and feature_with_attr == feature:
            features.append(new_feature)

        # print(f'TIPO DE {new_feature} (new_feature): {type(new_feature)}')
        # print(f'TIPO DE {feature} (feature): {type(feature)}')
        # feature_with_attr = new_feature
        # if hasattr(feature_with_attr, 'reference'):
        #     print(f'FEATURE: {feature_with_attr}, REFERENCE: {feature_with_attr.reference}')
        #     if getattr(new_feature, "reference") == feature:
        #         features.append(new_feature)
        #     feature_with_attr = feature_with_attr.reference
    return features

def remove_abstract_child(fm: FeatureModel, feature: Feature) -> FeatureModel:
    # print(f'FEATURE IN REMOVE ABSTRACT CHILD: {feature.name}')
    feature_relations = feature.get_relations()
    # print(f'RELATIONS IN REMOVE ABSTRACT CHILD: {[str(f) for f in feature_relations]}')
    feature_next_rel = next(r for r in feature_relations)
    # print(f'NEXT RELATION IN REMOVE ABSTRACT CHILD: {str(feature_next_rel)}')
    feature_next_abstract = next(c for c in feature.get_children())
    # print(f'NEXT ABSTRACT IN REMOVE ABSTRACT CHILD: {feature_next_abstract}')
    # print(f'NEXT ABSTRACT IS ABSTRACT: {feature_next_abstract.is_abstract}')
    if len(feature_relations)==1 and feature_next_rel.is_mandatory() and feature_next_abstract.is_abstract:
            feature.get_relations().remove(feature_next_rel)
            fm.root = feature_next_abstract
            fm = remove_abstract_child(fm, feature_next_abstract)
    return fm


# def changing_names(model: FeatureModel, feature: Feature) -> FeatureModel:
#     features_list = []
#     for f in model.get_features():
#         if f == feature:
#             features_list.append(f)
#     if len(features_list)>1:
#         print(f'FEATURES LIST changing names before: {[f.name for f in features_list]}')
#         for feat in features_list:
#             feature_reference = model.get_feature_by_name(feat.name)
#             feat.name = utils.get_new_feature_name(model, feat.name)
#             if feat != feature_reference:
#                 feat.reference = feature_reference
#         print(f'FEATURES LIST changing names after: {[f.name for f in features_list]}')
#     return model