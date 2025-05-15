from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, Constraint

from rhea.refactorings import FMRefactoring
from rhea.metamodels.fm_metamodel.models import fm_utils


class SplitConstraint(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Split constraint'

    @staticmethod
    def get_description() -> str:
        return ("It splits a constraint in multiple constraints dividing it by the AND operator "
                "when possible.")

    @staticmethod
    def get_language_construct_name() -> str:
        return 'Constraint'

    @staticmethod
    def get_instances(model: FeatureModel) -> list[Constraint]:
        return [ctc for ctc in model.get_constraints() if len(fm_utils.split_constraint(ctc)) > 1]

    @staticmethod
    def is_applicable(model: FeatureModel) -> bool:
        return True

    @staticmethod
    def transform(model: FeatureModel, instance: Constraint) -> FeatureModel:
        if instance is None:
            raise Exception(f'Constraint {instance} is None.')

        model.ctcs.remove(instance)
        for ctc in fm_utils.split_constraint(instance):
            model.ctcs.append(ctc)
        return model
