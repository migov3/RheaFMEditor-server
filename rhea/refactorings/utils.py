from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, Constraint
from flamapy.core.models.ast import AST, ASTOperation, Node

from rhea.refactorings import FMRefactoring


def get_right_feature_name(instance: Constraint) -> str:
    if instance.ast.root.right.data is ASTOperation.NOT:
        not_operation = instance.ast.root.right
        right_feature_name_ctc = not_operation.left.data
    else:
        right_feature_name_ctc = instance.ast.root.right.data
    return right_feature_name_ctc


def get_left_feature_name(instance: Constraint) -> str:
    if instance.ast.root.left.data is ASTOperation.NOT:
        not_operation = instance.ast.root.left
        left_feature_name_ctc = not_operation.left.data
    else:
        left_feature_name_ctc = instance.ast.root.left.data
    return left_feature_name_ctc


def remove_abstract_leaf_without_reference(model: FeatureModel) -> FeatureModel:
    '''Removes all abstract LEAF which richt feature is not in tree (before joining subtrees)'''
    model_if_none = model
    if model is not None:
        for feat in model.get_features():
            ctc = next((c for c in model.get_constraints() if get_left_feature_name(c) == feat.name), None)
            if feat.is_leaf() and feat.is_abstract:
                if ctc is not None:
                   if model.get_feature_by_name(get_right_feature_name(ctc)) not in model.get_features():
                        model = eliminate_node_from_tree(model, feat)
    if model is None:
        model = model_if_none
    return model

# def remove_abstract_leaf_without_constraint(model: FeatureModel) -> FeatureModel:
#     '''Removes all abstract LEAF nodes without contraint (after joining subtrees)'''
#     model_if_none = model
#     if model is not None:
#         for feat in model.get_features():
#             if feat.is_leaf() and feat.is_abstract:
#                 for ctc in model.get_constraints():
#                     if feat in ctc.get_features():
#                         pass
#     if model is None:
#         model = model_if_none
#     return model


def get_new_feature_name(fm: FeatureModel, name: str) -> str:
    count = 1
    new_name = f'{name}'
    while fm.get_feature_by_name(new_name) is not None:
        new_name = f'{name}{count}'
        count += 1
    return new_name


def get_new_feature_complex_name(fm: FeatureModel, name: str) -> str:
    count = 1
    new_name = f'{name}'
    while fm.get_feature_by_name(new_name) is not None:
        new_name = f'{name}_{count}'
        count += 1
    return new_name


def get_new_ctc_name(ctcs_names: list[str], name: str) -> str:
    count = 1
    new_name = f'{name}'
    while new_name in ctcs_names:
        new_name = f'{name}{count}'
        count += 1
    return new_name


def get_new_attr_name(header: list, name: str) -> str:
    count = 1
    new_name = f'{name}'
    while new_name in header:
        new_name = f'{name}{count}'
        count += 1
    return new_name


def remove_abstract_child(fm: FeatureModel, feature: Feature) -> FeatureModel:
    feature_relations = feature.get_relations()
    feature_next_rel = next(r for r in feature_relations)
    feature_next_abstract = next(c for c in feature.get_children())
    if len(feature_relations)==1 and feature_next_rel.is_mandatory() and feature_next_abstract.is_abstract:
            feature.get_relations().remove(feature_next_rel)
            fm.root = feature_next_abstract
            fm = remove_abstract_child(fm, feature_next_abstract)
    return fm


def is_there_node(parent: Feature, child_node: Feature) -> Feature:
    result = ''
    for child in parent.get_children():
        if child==child_node:
            result = child
    return result


def convert_parent_to_mandatory(fm: FeatureModel, f: Feature) -> FeatureModel:
    parent = f.get_parent()
    if parent is not None:
        # print(f'PARENT: {parent.name}')
        # print(f'PARENT RELATIONS: {[str(r) for r in parent.get_relations()]}')
        rel_mand = next((r for r in parent.relations if f in r.children), None)
        if rel_mand is not None:
            rel_mand.card_min = 1
        fm = convert_parent_to_mandatory(fm, parent)
    return fm

def get_model_plus(model: FeatureModel, f_list: list[Feature]) -> FeatureModel:
    for f in f_list:
        if model is not None:
            model = add_node_to_tree(model, f)
    return model

def get_model_less(model: FeatureModel, f_list: list[Feature]) -> FeatureModel:
    #print(f'Feature to eliminate: {[f.name for f in f_list]}')
    for f_left_less in f_list:
        if model is not None:
            model = eliminate_node_from_tree(model, f_left_less)
            #print(f'Less ({f_left_less}): {model}')
    return model


def add_node_to_tree(model: FeatureModel, node: Feature) -> FeatureModel:
    if node not in model.get_features(): 
        #  If model does not contain F (node), the result is None
        return None
    elif model.root==node:
        # If F (node) is the root of model, the result is model. 
        return model
    else:
        parent = node.parent  # Let the parent feature of F (node) be P (parent).
        if (not parent.is_group()) and node.is_optional():  # parent.is_root() or parent.is_mandatory() or parent.is_optional()
            # If P is a MandOpt feature and F is an optional subfeature, make F a mandatory subfeature of P
            rel_mand = next((r for r in parent.get_relations() if node in r.children), None)
            rel_mand.card_min = 1
        elif parent.is_alternative_group() and (len(parent.get_children()) > 2 or (parent.get_children()[0].name != 
                                                parent.get_children()[1].name)):
            # If P is an Xor feature, make P a MandOpt feature which has F as single
            # mandatory subfeature and has no optional subfeatures. All other
            # subfeatures of P are removed from the tree.
            rel = next((r for r in parent.get_relations()), None)
            parent.get_relations().remove(rel)
            r_mand = Relation(parent, [node], 1, 1)  # mandatory
            parent.add_relation(r_mand)
        elif parent.is_or_group():
            # If P is an Or feature, make P a MandOpt feature which has F as single
            # mandatory subfeature, and has all other subfeatures of P as optional subfeatures. 
            relations = [r for r in parent.get_relations()]
            r_mand = Relation(parent, [node], 1, 1)  # mandatory
            parent.add_relation(r_mand)
            for child in parent.get_children():
                if child!=node:
                    r_opt = Relation(parent, [child], 0, 1)  # optional
                    parent.add_relation(r_opt)
            for rel in relations:
                parent.get_relations().remove(rel)

        # Convert P to mandatory.
        model = convert_parent_to_mandatory(model, parent)

    # GOTO step 2 with P instead of F.
    model = add_node_to_tree(model, parent)
    # print(f'NEW MODEL PLUS after: {model}')
    return model


def eliminate_node_from_tree(model: FeatureModel, node: Feature) -> FeatureModel:
    # print(f'my model {node.name}: {model}')
    # print(f'MODEL LESS PARA {node}: {model}')
    # print(f'{node} ES MANDATORY: {node.is_mandatory()}')

    if node not in model.get_features():
        # If model does not contain node, the result is model.
        return model
    elif model.root==node:
        # If F is the root of T, the result is NIL.
        print(f'model.root: {model.root}')
        return None
    else:
        parent = node.parent  # Let the parent feature of F be P.
        if node.is_mandatory() and not parent.is_group():  # parent.is_root() or parent.is_mandatory() or parent.is_optional()
            # If P is a MandOpt feature and F is a mandatory subfeature of P, GOTO
            # step 2 with P instead of F.
            print(f'node mandatory: {node.name}')
            model = eliminate_node_from_tree(model, parent)
        elif not parent.is_group() and node.is_optional():  # parent.is_root() or parent.is_mandatory() or parent.is_optional()
            # If P is a MandOpt feature and F is an optional subfeature of P, delete F.
            r_opt = next((r for r in parent.get_relations() if r.is_optional() 
                                                               and node in r.children), None)
            parent.get_relations().remove(r_opt)
            print(f'node optional: {node.name}')
        elif parent.is_alternative_group() and len(parent.get_children()) == 2 and parent.get_children()[0].name == parent.get_children()[1].name:
            print(f'node xor iguales: {node.name}')
            node1 = parent.get_children()[0]
            node2 = parent.get_children()[1]
            rel = next((r for r in parent.get_relations()), None)

            fm1 = FeatureModel(node1, None)
            fm = FeatureModel(node, None)

            node_to_maintain = None  # the other will be eliminated
            if fm1 == fm:
                node_to_maintain = node2
            else:
                node_to_maintain = node1
            rel.children = [node_to_maintain]
            rel.card_min = 1
            rel.card_max = 1
            print(f'Relation: {str(rel)}')
        elif parent.is_or_group() or parent.is_alternative_group():
            print(f'node group: {node.name}')
            # If P is an Xor feature or an Or feature, delete F; if P has only one
            # remaining subfeature, make P a MandOpt feature and
            # its subfeature a mandatory subfeature. 
            rel = next((r for r in parent.get_relations()), None)
            rel.children.remove(node)  # Be careful!! Dangerous because features can be duplicated and they are only compared by names. Solution is to compare the whole FM as in the previous case.
            if rel.card_max > 1:
                rel.card_max -= 1
            if len(rel.children) == 1:
                rel.card_min = 1
    return model


def to_unique_features(fm: FeatureModel) -> FeatureModel:
    """Replace duplicated features names."""
    if not hasattr(fm, 'dict_references'):
            fm.dict_references = {}
    unique_features_names = []
    for f in fm.get_features():
        if f.name not in unique_features_names:
            unique_features_names.append(f.name)
        else:
            new_name = get_new_feature_name(fm, f.name)
            fm.dict_references[new_name] = f.name
            f.name = new_name
            unique_features_names.append(f.name)
            
    return fm


def apply_refactoring(fm: FeatureModel, refactoring: FMRefactoring) -> FeatureModel:
    instances = refactoring.get_instances(fm)
    for i in instances:
        fm = refactoring.transform(fm, i)
    return fm