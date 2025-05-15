import copy
import itertools
from unicodedata import is_normalized
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature



# def get_configurations3(fm: FeatureModel) -> list[set[str]]:
#     #configurations = [{fm.root}]
#     #return _get_configurations(fm.root, configurations)
#     return get_configurations_rec(fm.root)

def add_feature_to_configurations(feature: Feature, configurations: list[set[Feature]]) -> list[set[Feature]]:
    for config in configurations:
        config.add(feature)
    return configurations


def add_features_to_configurations(features: list[Feature], configurations: list[set[Feature]]) -> list[set[Feature]]:
    for config in configurations:
        config.update(features)
    return configurations


# def get_configurations_rec(feature: Feature) -> list[set[Feature]]:
#     if feature.is_leaf():
#         return [{feature}]
#     configurations = {}  # child -> configs
#     return_configurations = []
#     for relation in feature.get_relations():
#         if relation.is_mandatory():
#             configurations[child] = get_configurations_rec(child)
#             # meter el padre
#             configurations = add_feature_to_configurations(feature, configurations[child])
#         elif relation.is_optional():
#             configurations[child] = get_configurations_rec(child)
#             # meter el padre y no meterlo
#             return_configurations = add_feature_to_configurations(feature, configurations[child])
#             return_configurations.extend(set())
#         elif relation.is_alternative():
#             for child in relation.children:
#                 configurations[child] = get_configurations_rec(child)
#                 # meter el padre
#                 configurations[child] = add_feature_to_configurations(feature, configurations[child])

#         elif relation.is_or():
#             for child in relation.children:
#                 configurations[child] = get_configurations_rec(child)
#                 # meter el padre

#     for relation in feature.get_relations():
#         if relation.is_mandatory():
#             counts.append(count_configurations_rec(relation.children[0]))
#         elif relation.is_optional():
#             counts.append(count_configurations_rec(relation.children[0]) + 1)
#         elif relation.is_alternative():
#             for child in relation.children:
#                 configurations.extend(get_configurations_rec(child))
#         elif relation.is_or():
#             children_counts = [count_configurations_rec(f) + 1 for f in relation.children]
#             counts.append(math.prod(children_counts) - 1)
#     return math.prod(counts)


def get_configurations2(fm: FeatureModel) -> list[set[str]]:
    configurations = [{fm.root}]
    return _get_configurations(fm.root, configurations)


def _get_configurations(feature: Feature, configurations: list[set[Feature]]) -> list[set[Feature]]:
    children = feature.get_children()
    configurations_with_feature = configurations  # configuration with the current feature selected.
    print('----------')
    for i, p in enumerate(configurations_with_feature):
        print(f'P{i}: {[str(f) for f in p]}')
    print('----------')
    if feature.is_mandatory():
        for config in configurations:
            config.add(feature)
    elif feature.is_optional():
        configurations_with_feature = copy.deepcopy(configurations)
        for config in configurations_with_feature:
            config.add(feature)
        configurations.extend(configurations_with_feature)
    if feature.is_or_group():
        _configurations = []
        for size in range(1, len(children) + 1):
            combinations = itertools.combinations(children, size)
            for combi in combinations:
                _configurations.append(set(combi))
        # cartesian product
        new_configurations = []
        config_products = itertools.product(configurations_with_feature, _configurations)
        for cp in config_products:
            new_configurations.extend(cp)
        configurations_with_feature = new_configurations
    if feature.is_alternative_group():
        _configurations = []
        for child in children:
            _configurations.append({child})
        # cartesian product
        new_configurations = []
        config_products = itertools.product(configurations_with_feature, _configurations)
        for cp in config_products:
            new_configurations.extend(cp)
        configurations_with_feature = new_configurations
    for child in children:
        configurations_with_feature = _get_configurations(child, configurations_with_feature)
        configurations.extend(configurations_with_feature)
    return configurations

def get_configurations(fm: FeatureModel) -> list[set[Feature]]:
    configurations = [{fm.root}]
    features = [fm.root]
    while features:
        feature = features.pop()
        for relation in feature.get_relations():
            if relation.is_mandatory():
                configurations = add_feature_to_configurations(relation.children[0], configurations)
                features.extend(relation.children)
            elif relation.is_optional():
                copy_configurations = copy.deepcopy(configurations)
                copy_configurations = add_feature_to_configurations(relation.children[0], copy_configurations)
                configurations.extend(copy_configurations)
                features.extend(relation.children)
            elif relation.is_alternative():
                xor_configurations = []
                for child in relation.children:
                    copy_configurations = copy.deepcopy(configurations)
                    copy_configurations = add_feature_to_configurations(child, copy_configurations)
                    xor_configurations.extend(copy_configurations)
                    features.append(child)
                configurations = xor_configurations
            elif relation.is_or():
                or_configurations = []
                for size in range(1, len(relation.children) + 1):
                    combinations = itertools.combinations(relation.children, size)
                    for combi in combinations:
                        copy_configurations = copy.deepcopy(configurations)
                        copy_configurations = add_features_to_configurations(combi, copy_configurations)
                        or_configurations.extend(copy_configurations)
                configurations = or_configurations
                features.extend(relation.children)
    return configurations
