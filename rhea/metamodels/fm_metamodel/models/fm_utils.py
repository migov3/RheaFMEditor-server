import copy
from typing import Any
import datetime

from flamapy.core.models import AST, ASTOperation, ast
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Constraint, Relation

from rhea.metamodels.fm_metamodel.models import Type


def parse_type_value(value: str) -> tuple[Type, Any]:
    """Given a value represented in a string, returns the associated type and its parsed value."""
    try:
        return (Type('Integer'), int(value))
    except:
        pass
    try:
        return (Type('Float'), float(value))
    except:
        pass
    try:
        return (Type('Date'), datetime.datetime.strptime(value, '%b %d %Y'))
    except:
        pass
    return (Type('String'), value)


def split_constraint(constraint: Constraint) -> list[Constraint]:
    """Given a constraint, split it in multiple constraints separated by the AND operator."""
    asts = split_formula(constraint.ast)
    asts_nnf = [ast.convert_into_nnf(ctc) for ctc in asts]
    asts = []
    for ctc in asts_nnf:
        asts.extend(split_formula(ctc))
    asts_cnf = [ast.convert_into_cnf(ctc) for ctc in asts]
    asts = []
    for ctc in asts_cnf:
        asts.extend(split_formula(ctc))
    return [Constraint(f'{constraint.name}{i}', ast) for i, ast in enumerate(asts)]


def split_formula(formula: AST) -> list[AST]:
    """Given a formula, returns a list of formulas separated by the AND operator."""
    res = []
    node = formula.root
    if node.data == ASTOperation.AND:
        res.extend(split_formula(AST(node.left)))
        res.extend(split_formula(AST(node.right)))
    else:
        res.append(formula)
    return res


def is_simple_constraint(constraint: Constraint) -> bool:
    return is_requires_constraint(constraint) or is_excludes_constraint(constraint)


def is_complex_constraint(constraint: Constraint) -> bool:
    return not is_simple_constraint(constraint)


def is_requires_constraint(constraint: Constraint) -> bool:
    root_op = constraint.ast.root
    if root_op.is_binary_op():
        if root_op.data in [ASTOperation.REQUIRES, ASTOperation.IMPLIES]:
            return root_op.left.is_term() and root_op.right.is_term()
        elif root_op.data == ASTOperation.OR:
            neg_left = root_op.left.data == ASTOperation.NOT and root_op.left.left.is_term()
            neg_right = root_op.right.data == ASTOperation.NOT and root_op.right.left.is_term()
            return neg_left and root_op.right.is_term() or neg_right and root_op.left.is_term()
    return False


def is_excludes_constraint(constraint: Constraint) -> bool:
    root_op = constraint.ast.root
    if root_op.is_binary_op():
        if root_op.data in [ASTOperation.EXCLUDES, ASTOperation.XOR]:
            return root_op.left.is_term() and root_op.right.is_term()
        elif root_op.data in [ASTOperation.REQUIRES, ASTOperation.IMPLIES]:
            neg_right = root_op.right.data == ASTOperation.NOT and root_op.right.left.is_term()
            return root_op.left.is_term() and neg_right
        elif root_op.data == ASTOperation.OR:
            neg_left = root_op.left.data == ASTOperation.NOT and root_op.left.left.is_term()
            neg_right = root_op.right.data == ASTOperation.NOT and root_op.right.left.is_term()
            return neg_left and neg_right
    return False


def filter_products(fm: FeatureModel, configurations: list[list[str]]) -> list[list[str]]:
    """Given a list of configurations return it with the configurations filtered.
    
    This method takes into account that the features in the FM can be not unique. 
    That is, features can have a 'reference' attribute indicating that the feature is non-unique
    and appears in other part of the FM. The 'reference' points to the original feature.

    The filters performed are the following:
      a) Remove abstract features.
      b) Substitute non-unique features with the original one.
      c) Remove duplicate features.
    """
    filtered_configs = set()
    for config in configurations:
        c = set()
        for f in config:
            feature = fm.get_feature_by_name(f)
            if not feature.is_abstract:
                while hasattr(feature, 'reference'):
                    feature = feature.reference
                c.add(feature.name)
        filtered_configs.add(frozenset(c))
    return filtered_configs


def filter_products_from_dict(fm: FeatureModel, configurations: list[list[str]]) -> list[list[str]]:
    """Given a list of configurations return it with the configurations filtered.
    
    This method takes into account that the features in the FM can be not unique. 
    That is, features can have its corresponding features in a dictionary
    indicating that the feature is non-unique and appears in other part of the FM.
    The corresponding value in the dictionary points to the original feature.

    The filters performed are the following:
      a) Remove abstract features.
      b) Substitute non-unique features with the original one.
      c) Remove duplicate features.
    """
    filtered_configs = set()
    for config in configurations:
        c = set()
        for f in config:
            feature_name = f
            if hasattr(fm, 'dict_references') and f in fm.dict_references:
                feature_name = fm.dict_references[f]
            feature = fm.get_feature_by_name(feature_name)
            if not feature.is_abstract:
                c.add(feature.name)
        filtered_configs.add(frozenset(c))
    return filtered_configs


def remove_references(fm: FeatureModel) -> FeatureModel:
    """Given a feature model with a references dictionary, 
    substitute each reference with the original feature 
    giving as result a feature model with non-unique features."""
    if hasattr(fm, 'dict_references'):    
        for feature in fm.get_features():
            if feature.name in fm.dict_references.keys():
                feature = fm.dict_references[feature.name]
                print(f'FEATURE remove reference: {feature.name}')
    return fm


def update_feature(fm: FeatureModel, 
                   feature_old_name: str, 
                   feature_new_name: str, 
                   feature_type: str, 
                   group_card_min: int, 
                   group_card_max: int, 
                   feature_attributes: list[dict[str, str]]) -> FeatureModel:
    
    return fm


def commitment_feature(fm: FeatureModel, feature_name: str) -> FeatureModel:
    """Given a feature model T and a feature F, this algorithm computes the feature model
    T(+F) whose products are precisely those products of T with contain F.
    
    The algorithm transforms T into T(+F).

    The algorithm is an adaptation from:
        [Broek2008 @ SPLC: Elimination of constraints from feature trees].
    """
    features_to_commit = [f for f in fm.get_features() if f.name == feature_name]
    if not features_to_commit:  # If T does not contain F, the result is NIL.
        return None
    for feature in features_to_commit:
        feature_to_commit = feature
        while feature_to_commit != fm.root:  # If F is the root of T, the result is T.
            parent = feature_to_commit.get_parent()  # Let the parent feature of F be P.
            if not parent.is_group() and feature_to_commit.is_optional():  # If P is a MandOpt feature and F is an optional subfeature, make F a mandatory subfeature of P.
                rel = next((r for r in parent.get_relations() if feature_to_commit in r.children), None)
                rel.card_min = 1
            elif parent.is_alternative_group():  #If P is an Xor feature, make P a MandOpt feature which has F as single mandatory subfeature and has no optional subfeatures. All other subfeatures of P are removed from the tree.
                parent.get_relations()[0].children = [feature_to_commit]
            elif parent.is_or_group():  # If P is an Or feature, make P a MandOpt feature which has F as single mandatory subfeature, and has all other subfeatures of P as optional subfeatures.
                parent_relations = parent.get_relations()
                or_relation = parent_relations[0]
                or_relation.children.remove(feature_to_commit)
                parent_relations.remove(or_relation)
                new_mandatory_rel = Relation(parent, [feature_to_commit], 1, 1)
                parent_relations.append(new_mandatory_rel)
                for child in or_relation.children:
                    new_optional_rel = Relation(parent, [child], 0, 1)
                    parent_relations.append(new_optional_rel)
            # GOTO step 2 with P instead of F.
            feature_to_commit = parent
    return fm


def deletion_feature(fm: FeatureModel, feature_name: str) -> FeatureModel:
    """Given a feature model T and a feature F, this algorithm computes the feature model
    T(-F) whose products are precisely those products of T with do not contain F.
    
    The algorithm transforms T into T(-F).

    The algorithm is an adaptation from:
        [Broek2008 @ SPLC: Elimination of constraints from feature trees].
    """
    features_to_delete = [f for f in fm.get_features() if f.name == feature_name]
    if not features_to_delete:  # If T does not contain F, the result is T.
        return fm
    for feature in features_to_delete:
        feature_to_delete = feature
        parent = feature_to_delete.get_parent()  # Let the parent feature of F be P.
        # If P is a MandOpt feature and F is a mandatory subfeature of P, GOTO step 2 with P instead of F.
        while feature_to_delete != fm.root and not parent.is_group() and feature_to_delete.is_mandatory():
            feature_to_delete = parent
            parent = feature_to_delete.get_parent()
        if feature_to_delete == fm.root:  # If F is the root of T, the result is NIL.
            return None
        # If P is a MandOpt feature and F is an optional subfeature of P, delete F.
        if not parent.is_group() and feature_to_delete.is_optional():
            rel = next((r for r in parent.get_relations() if feature_to_delete in r.children), None)
            parent.get_relations().remove(rel)
        # If P is an Xor feature or an Or feature, delete F; if P has only one remaining subfeature, make P a MandOpt feature and its subfeature a mandatory subfeature.
        if parent.is_alternative_group() or parent.is_or_group():
            rel = parent.get_relations()[0]
            rel.children.remove(feature_to_delete)
            if len(rel.children) == 1:
                rel.card_max = 1
    return fm


def eliminate_requires(fm: FeatureModel, requires_ctc: Constraint) -> FeatureModel:
    """Algorithm to eliminate a constraint 'A requires B' from the feature model.
    
    The algorithm construct a feature model T whose products are those products of T 
    which contain B when they contain A.
    This set of products is the union of the products sets of T(+B) and T(-A-B).
    The product sets of T(+B) and T(-A-B) are disjoint. So the required feature model can be
    obtained by taking a new Xor feature as root which has T(+B) and T(-A-B) as subfeatures.
    """
    fm.get_constraints().remove(requires_ctc)
    feature_name_a, feature_name_b = features_names_from_simple_constraint(requires_ctc)
    fm_plus_b = copy.deepcopy(fm)
    fm_less_ab = copy.deepcopy(fm)
    # Construct T(+B) and T(-A-B)
    fm_plus_b = commitment_feature(fm_plus_b, feature_name_b)
    fm_less_ab = deletion_feature(fm_less_ab, feature_name_a)
    fm_less_ab = deletion_feature(fm_less_ab, feature_name_b)
    # If both trees are not equal to NIL, 
    # then the result consists of a new root, which is an Xor feature,
    # with subfeatures T(+B) and T(-A-B).
    if fm_plus_b is not None and fm_less_ab is not None:
        new_root = Feature(get_new_feature_name(fm, 'root'), is_abstract=True)
        fm_plus_b.root.parent = new_root
        fm_less_ab.root.parent = new_root
        xor_rel = Relation(new_root, [fm_plus_b.root, fm_less_ab.root], 1, 1)
        new_root.add_relation(xor_rel)
        fm.root = new_root
        return fm
    if fm_less_ab is None:  # If T(-A-B) is equal to NIL, then the result is T(+B).
        fm = fm_plus_b
    if fm_plus_b is None:  # If T(+B) is equal to NIL, then the result is T(-A-B).
        fm = fm_less_ab
    return fm


def features_names_from_simple_constraint(simple_ctc: Constraint) -> tuple[str, str]:
    """Return the names of the features involved in a simple constraint.
    
    A simple constraint can be a requires constraint or an excludes constraint.
    A requires constraint can be represented in the AST of the constraint with one of the following structures:
        A requires B
        A => B
        !A v B
    An excludes constraint can be represented in the AST of the constraint with one of the following structures:
        A excludes B
        A => !B
        !A v !B
    """
    root_op = simple_ctc.ast.root
    left = root_op.left.data
    right = root_op.right.data
    if left == ASTOperation.NOT:
        left = root_op.left.left.data
    if right == ASTOperation.NOT:
        right == root_op.right.left.data
    return (left, right)


def get_new_feature_name(fm: FeatureModel, prefix_name: str) -> str:
    """Return a new name for a feature based on the provided prefix."""
    count = 1
    new_name = f'{prefix_name}'
    while fm.get_feature_by_name(new_name) is not None:
        new_name = f'{prefix_name}{count}'
        count += 1
    return new_name
