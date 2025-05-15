from asyncio import constants
from statistics import mode
from turtle import left
from typing import Any, Dict

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, Constraint
from flamapy.metamodels.fm_metamodel.transformations import UVLWriter

from flamapy.core.models.ast import AST, ASTOperation, Node
from rhea.refactorings.split_constraint import SplitConstraint
from rhea.refactorings.elimination_complex_constraints import EliminationComplexConstraints
from rhea.refactorings.elimination_simple_ctcs_requires import EliminationSimpleConstraintsRequires
from rhea.refactorings.elimination_simple_ctcs_excludes import EliminationSimpleConstraintsExcludes

from rhea.metamodels.fm_metamodel.models import FM, ConstraintHelper
from rhea.refactorings import FMRefactoring
from rhea.refactorings import utils
from rhea.metamodels.fm_metamodel.models import fm_utils


REFACTORING_COMPLEX = EliminationComplexConstraints
REFACTORING_REQUIRES = EliminationSimpleConstraintsRequires
REFACTORING_EXCLUDES = EliminationSimpleConstraintsExcludes


class EliminationAnyConstraints(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Elimination of Any Constraint from Feature Trees'

    @staticmethod
    def get_description() -> str:
        return ("It eliminates any requested constraint by calling al the other methods"
                    "of elimination of Constraints.")

    @staticmethod
    def get_language_construct_name() -> str:
        return 'Constraint'

    @staticmethod
    def get_instances(model: FeatureModel) -> list[Constraint]:
        return [ctc for ctc in model.get_constraints()]

    @staticmethod
    def is_applicable(model: FeatureModel) -> bool:
        return True

    @staticmethod
    def transform(model: FeatureModel, instance: Constraint) -> FeatureModel:
        if instance is None:
            raise Exception(f'Constraint {instance} is None.')

        if not hasattr(model, 'dict_references'):
            model.dict_references = {}
        
        print(f'MODEL DICT - before: {[(name, value.name) for name, value in model.dict_references.items()]}')
        
        if fm_utils.is_complex_constraint(instance):
            # split
            ctc_list = fm_utils.split_constraint(instance)
            model.get_constraints().remove(instance)
            original_ctcs = set(model.get_constraints())
            model.get_constraints().extend(ctc_list)
            
            for ctc in ctc_list:
                if fm_utils.is_complex_constraint(ctc):
                    # aplicas el refactoring del complex
                    model = REFACTORING_COMPLEX.transform(model, ctc)

            new_ctcs = set(model.get_constraints()) - original_ctcs

            for ctc in new_ctcs:
                if fm_utils.is_requires_constraint(ctc):
                    #print(f'Applying the refactoring {REFACTORING_REQUIRES.get_name()}...')
                    model = REFACTORING_REQUIRES.transform(model, ctc)
                    # UVLWriter(model, f"salida{ctc}.uvl").transform()
                elif fm_utils.is_excludes_constraint(ctc):
                    #print(f'Applying the refactoring {REFACTORING_EXCLUDES.get_name()}...')
                    model = REFACTORING_EXCLUDES.transform(model, ctc)
                    # UVLWriter(model, f"salida{ctc}.uvl").transform()
                else:
                    raise Exception(f'Invalid simple constraint: {ctc}')
        else:
            if fm_utils.is_requires_constraint(instance):
                #print(f'Applying the refactoring {REFACTORING_REQUIRES.get_name()}...')
                model = REFACTORING_REQUIRES.transform(model, instance)
                # UVLWriter(model, f"salida{instance}.uvl").transform()
            elif fm_utils.is_excludes_constraint(instance):
                #print(f'Applying the refactoring {REFACTORING_EXCLUDES.get_name()}...')
                model = REFACTORING_EXCLUDES.transform(model, instance)
                # UVLWriter(model, f"salida{instance}.uvl").transform()
            else:
                raise Exception(f'Invalid simple constraint: {instance}')

        print(f'MODEL DICT - after: {[(name, value.name) for name, value in model.dict_references.items()]}')

        return model