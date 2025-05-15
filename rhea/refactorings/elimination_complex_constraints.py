from flamapy.core.models.ast import AST, ASTOperation, Node
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, Constraint

from rhea.metamodels.fm_metamodel.models import fm_utils
from rhea.refactorings import FMRefactoring
from rhea.refactorings import utils


class EliminationComplexConstraints(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Strict-complex constraint refactoring'

    @staticmethod
    def get_description() -> str:
        return ("It transforms a strict-complex constraint by adding additional abstract features "
                "and simple constraints without adding or removing products.")

    @staticmethod
    def get_language_construct_name() -> str:
        return 'Strict-complex constraint'

    @staticmethod
    def get_instances(model: FeatureModel) -> list[Constraint]:
        return [ctc for ctc in model.get_constraints() if fm_utils.is_complex_constraint(ctc)]

    @staticmethod
    def is_applicable(model: FeatureModel) -> bool:
        return True

    @staticmethod
    def transform(model: FeatureModel, instance: Constraint) -> FeatureModel:
        if instance is None:
            raise Exception(f'Constraint {instance} is None.')
        if not fm_utils.is_complex_constraint(instance):
            raise Exception(f'Constraint {instance} is not complex.')

        model.ctcs.remove(instance)
        ctcs_names = [ctc.name for ctc in model.get_constraints()]
        new_or = Feature(utils.get_new_feature_name(model, 'OR'), is_abstract=True)
        features = []
        dict_constraint = get_features_clauses(instance)  # NOT before negatives (dict)
        for f in dict_constraint.keys():
            new_feature = Feature(utils.get_new_feature_complex_name(model, f), 
                                  parent=new_or, is_abstract=True)
            features.append(new_feature)
            ast_operation = ASTOperation.REQUIRES if dict_constraint[f] else ASTOperation.EXCLUDES
            ctc = Constraint(utils.get_new_ctc_name(ctcs_names, 'CTC'), 
                             AST.create_binary_operation(ast_operation, 
                             Node(new_feature.name), Node(f)))
            ctcs_names.append(ctc.name)
            model.ctcs.append(ctc)

        # New branch with OR as root
        rel_or = Relation(new_or, features, 1, len(features))  # OR
        new_or.add_relation(rel_or)
        
        # New root (only needed if the root feature is a group)
        if model.root.is_group():
            new_root = Feature(utils.get_new_feature_name(model, 'root'), is_abstract=True)
            rel_1 = Relation(new_root, [model.root], 1, 1)  # mandatory
            new_root.add_relation(rel_1)
            model.root.parent = new_root
        else:
            new_root = model.root
        rel_2 = Relation(new_root, [new_or], 1, 1)  # mandatory
        new_root.add_relation(rel_2)
        new_or.parent = new_root
        model.root = new_root

        return model


def get_features_clauses(instance: Constraint) -> dict:
    """Returns a dictionary of 'Features -> bool',
    that sets 'bool' to FALSE if the feature has a negation"""
    features = {}
    clauses = instance.ast.to_cnf()
    stack = [clauses.root]
    while stack:
        node = stack.pop()
        if node.is_unique_term():
            features[node.data] = True
        elif node.is_unary_op():
            features[node.left.data] = False
        elif node.is_binary_op():
            stack.append(node.right)
            stack.append(node.left)
    return features
