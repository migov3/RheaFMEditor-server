import copy
from typing import Any

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, Constraint
from flamapy.metamodels.fm_metamodel.transformations import UVLWriter

from flamapy.core.models.ast import AST, ASTOperation, Node

from rhea.metamodels.fm_metamodel.models import FM, ConstraintHelper
from rhea.refactorings import FMRefactoring
from rhea.refactorings import utils


class EliminationSimpleConstraintsExcludes(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Elimination of Constraints from Feature Trees - Excludes'
    
    @staticmethod
    def get_description() -> str:
        return ("It eliminates de simple constraint with Excludes")

    @staticmethod
    def get_language_construct_name() -> str:
        return 'Constraint'

    @staticmethod
    def get_instances(model: FeatureModel) -> list[Constraint]:
        return [ctc for ctc in model.get_constraints() if ConstraintHelper(ctc).is_excludes_constraint()]

    @staticmethod
    def is_applicable(model: FeatureModel) -> bool:
        return True

    @staticmethod
    def transform(model: FeatureModel, instance: Constraint) -> FeatureModel:
        if instance is None:
            raise Exception(f'There is not constraint with name "{str(instance)}".')
        if not ConstraintHelper(instance).is_excludes_constraint():
            raise Exception(f'Operator {str(instance)} is not excludes.')

        model_less = copy.deepcopy(model)
        model_less_plus = copy.deepcopy(model)

        right_feature_name_ctc = utils.get_right_feature_name(instance)
        list_right_features_less_ctc = [f for f in model_less.get_features()
                                        if f.name == right_feature_name_ctc]
        list_right_features_less_plus_ctc = [f for f in model_less_plus.get_features()
                                        if f.name == right_feature_name_ctc]

        left_feature_name_ctc = utils.get_left_feature_name(instance)
        list_left_features_less_plus_ctc = [f for f in model_less_plus.get_features() 
                                       if f.name == left_feature_name_ctc]

        
        model_less = utils.get_model_less(model_less, list_right_features_less_ctc)
        model_less_plus = utils.get_model_less(model_less_plus, list_left_features_less_plus_ctc)
        model_less_plus = utils.get_model_plus(model_less_plus, list_right_features_less_plus_ctc)


        # Construct T(-B) and T(-A+B).
        if model_less is not None and model_less_plus is not None:
            # If both trees are not equal to NIL, then the result consists of a new root, which
            # is an Xor feature with subtrees T(-B) and T(-A+B). 
            new_root = Feature(utils.get_new_feature_name(model, 'root'), is_abstract=True)
            rel = Relation(new_root, [model_less.root, model_less_plus.root], 1, 1)  #XOR
            new_root.add_relation(rel)
            model_less.root.parent = new_root
            model_less_plus.root.parent = new_root
            model.root = new_root
        elif model_less is None:
            # If T(-B) is equal to NIL, then the result is T(-A+B). 
            model = model_less_plus
        elif model_less_plus is None:
            # If T(-A+B) is equal to NIL, then the result is T(-B). 
            model = model_less
        
        model.ctcs.remove(instance)

        model_copy = copy.deepcopy(model)
        model_copy = utils.to_unique_features(model_copy)

        return model