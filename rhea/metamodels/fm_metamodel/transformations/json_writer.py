import inspect
import importlib
import sys
import json
from typing import Any 
from enum import Enum

from flamapy.core.models.ast import Node, ASTOperation
from flamapy.core.transformations import ModelToText

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Constraint, Attribute

from rhea import refactorings
from rhea import language_constructs
from rhea.fm_tools import fm_tool_info
from rhea.fm_characterization import FMAnalysis


class JSONFeatureType(Enum):
    FEATURE = 'FEATURE'
    XOR = 'XOR'
    OR = 'OR'
    MUTEX = 'MUTEX'
    CARDINALITY = 'CARDINALITY'
    OPTIONAL = 'OPTIONAL'
    MANDATORY = 'MANDATORY'


class JSONWriter(ModelToText):

    CTC_TYPES = {ASTOperation.NOT: 'NotTerm',
                 ASTOperation.AND: 'AndTerm',
                 ASTOperation.OR: 'OrTerm',
                 ASTOperation.XOR: 'XorTerm',
                 ASTOperation.IMPLIES: 'ImpliesTerm',
                 ASTOperation.REQUIRES: 'RequiresTerm',
                 ASTOperation.EXCLUDES: 'ExcludesTerm',
                 ASTOperation.EQUIVALENCE: 'EquivalentTerm',
                 'FEATURE': 'FeatureTerm'}

    @staticmethod
    def get_destination_extension() -> str:
        return '.json'

    def __init__(self, path: str, source_model: FeatureModel) -> None:
        self.path = path
        self.source_model = source_model

    def transform(self) -> str:
        json_object = _to_json(self.source_model)
        if self.path is not None:
            with open(self.path, 'w', encoding='utf8') as file:
                json.dump(json_object, file, indent=4)
        return json.dumps(json_object, indent=4)


def _to_json(feature_model: FeatureModel) -> dict[str, Any]:
    result: dict[str, Any] = {}
    result['name'] = f'FM_{feature_model.root.name}'
    result['hash'] = str(hash(feature_model))
    result['features'] = _get_tree_info(feature_model.root)
    result['constraints'] = _get_constraints_info(feature_model.get_constraints())
    result['refactorings'] = _get_refactorings_info(feature_model)
    result['language_constructs'] = _get_language_constructs_info(feature_model)
    result['semantics_metrics'] = _get_semantics_metrics(feature_model)
    result['tools_info'] = _get_tools_info()
    return result


def _get_tree_info(feature: Feature) -> dict[str, Any]:
    feature_info = {}
    feature_info['name'] = feature.name
    feature_info['abstract'] = feature.is_abstract

    relations = []
    for relation in feature.get_relations():
        relation_info = {}
        relation_type = JSONFeatureType.FEATURE.value
        if relation.is_alternative():
            relation_type = JSONFeatureType.XOR.value
        elif relation.is_or():
            relation_type = JSONFeatureType.OR.value
        elif relation.is_mutex():
            relation_type = JSONFeatureType.MUTEX.value
        elif relation.is_cardinal():
            relation_type = JSONFeatureType.CARDINALITY.value
        elif relation.is_mandatory():
            relation_type = JSONFeatureType.MANDATORY.value
        elif relation.is_optional():
            relation_type = JSONFeatureType.OPTIONAL.value
        relation_info['type'] = relation_type
        relation_info['card_min'] = relation.card_min
        relation_info['card_max'] = relation.card_max
        children = []
        for child in relation.children:
            children.append(_get_tree_info(child))
        relation_info['children'] = children
        relations.append(relation_info)

    feature_info['relations'] = relations

    # Attributes
    feature_info['attributes'] = _get_attributes_info(feature.get_attributes())
    return feature_info


def _get_attributes_info(attributes: list[Attribute]) -> list[dict[str, Any]]:
    attributes_info = []
    for attribute in attributes:
        attr_info = {}
        attr_info['name'] = attribute.name
        if attribute.default_value is not None:
            attr_info['value'] = attribute.default_value
        attributes_info.append(attr_info)
    return attributes_info


def _get_constraints_info(constraints: list[Constraint]) -> list[dict[str, Any]]:
    constraints_info = []
    for ctc in constraints:
        ctc_info = {}
        ctc_info['name'] = ctc.name
        ctc_info['expr'] = ctc.ast.pretty_str()
        ctc_info['ast'] = _get_ctc_info(ctc.ast.root)
        constraints_info.append(ctc_info)
    return constraints_info


def _get_ctc_info(ast_node: Node) -> dict[str, Any]:
    ctc_info: dict[str, Any] = {}
    if ast_node.is_term():
        ctc_info['type'] = JSONWriter.CTC_TYPES['FEATURE']
        ctc_info['operands'] = [ast_node.data]
    else:
        ctc_info['type'] = JSONWriter.CTC_TYPES[ast_node.data]
        operands = []
        left = _get_ctc_info(ast_node.left)
        operands.append(left)
        if ast_node.right is not None:
            right = _get_ctc_info(ast_node.right)
            operands.append(right)
        ctc_info['operands'] = operands
    return ctc_info


def _get_refactorings_info(feature_model: FeatureModel) -> list[dict[str, Any]]:
    # Get class names
    class_list = list(refactorings.__all__)
    class_list.remove('FMRefactoring')

    # Get modules and class objects
    modules = inspect.getmembers(refactorings)
    modules = filter(lambda x: inspect.ismodule(x[1]), modules)
    modules = [importlib.import_module(m[1].__name__) for m in modules]
    classes = [getattr(m, c) for m in modules for c in class_list if hasattr(m, c)]

    refactorings_info = []
    for class_ in classes:
        ref_info = {}
        ref_info['id'] = class_.__name__
        ref_info['name'] = class_.get_name()
        ref_info['description'] = class_.get_description()
        ref_info['type'] = class_.get_language_construct_name()
        ref_info['instances'] = [i.name for i in class_.get_instances(feature_model)]
        ref_info['applicable'] = class_.is_applicable(feature_model)
        refactorings_info.append(ref_info)
    return refactorings_info


def _get_language_constructs_info(feature_model: FeatureModel) -> list[dict[str, Any]]:
    # Get class names
    class_list = list(language_constructs.__all__)
    class_list.remove('LanguageConstruct')

    # Get modules and class objects
    modules = inspect.getmembers(language_constructs)
    modules = filter(lambda x: inspect.ismodule(x[1]), modules)
    modules = [importlib.import_module(m[1].__name__) for m in modules]
    classes = [getattr(m, c) for c in class_list for m in modules if hasattr(m, c)]

    language_constructs_info = []
    tools = fm_tool_info.get_tools_info()
    for class_ in classes:
        lc_info = {}
        lc_info['id'] = class_.__name__
        lc_info['name'] = class_.name()
        lc_info['value'] = len(class_.get_instances(feature_model))
        lc_info['refactorings'] = [r.__name__ for r in class_.get_refactorings()]
        tool_support = []
        for t in tools:
            for lc in t.support:
                if lc.__name__ == lc_info['id']:
                    tool_support.append(t.name)
        lc_info['tools'] = tool_support
        language_constructs_info.append(lc_info)
    return language_constructs_info


def _get_semantics_metrics(feature_model: FeatureModel) -> list[dict[str, Any]]:
    metrics_info = []
    fm_analysis = FMAnalysis(feature_model)
    for property in fm_analysis.get_analysis():
        metric = {}
        metric['name'] = property.property.name
        metric['description'] = property.property.description
        metric['value'] = str(property.value) if property.size is None else str(property.size)
        metrics_info.append(metric)
    return metrics_info
    

def _get_metric(name: str, description: str, value: Any) -> dict[str, Any]:
    metric = {}
    metric['name'] = name
    metric['description'] = description
    metric[value] = value
    return metric


def _get_tools_info() -> list[dict[str, Any]]:
    tools_info = []
    for tool in fm_tool_info.get_tools_info():
        info = {}
        info['name'] = tool.name
        info['extension'] = tool.extension
        tools_info.append(info)
    return tools_info