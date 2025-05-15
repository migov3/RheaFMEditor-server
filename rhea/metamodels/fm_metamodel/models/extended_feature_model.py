from typing import Any, Optional

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, Constraint


class Range:
    
    def __init__(self, min_value: Any, max_value: Any):
        self.min_value: Any = min_value
        self.max_value: Any = max_value

    def __str__(self) -> str:
        return f'[{str(self.min_value)}, {str(self.max_value)}]'


class Domain:

    def __init__(self, 
                 ranges: Optional[list['Range']] = None, 
                 elements: Optional[list['Any']] = None):
        self.ranges = [] if ranges is None else ranges
        self.elements = [] if elements is None else elements

    def __str__(self) -> str:
        result = ''
        if self.elements:
            result += f'{self.elements}'
        if self.ranges:
            for rng in self.ranges:
                result += f'{rng}'
        return result


class Type:

    def __init__(self, 
                 name: str, 
                 domain: Optional[Domain] = None, 
                 default_value: Optional[Any] = None, 
                 null_value: Optional[Any] = None):
        self.name: 'str' = name
        self.domain: 'Domain' = domain
        self.default_value: 'Any' = default_value
        self.null_value: 'Any' = null_value

    def __str__(self) -> str:
        result = self.name
        if self.domain is not None:
            result += f'Domain: {self.domain}'
        if self.default_value is not None:
            result += f'Default value: {self.default_value}'
        if self.null_value is not None:
            result += f'Null value: {self.null_value}'
        return result


class Annotation:

    def __init__(self, name: str, value: Any):
        self.name = name,
        self.value = value

    def __str__(self) -> str:
        return f'@{self.name} {self.value}'


class Attribute:

    def __init__(self, name: str, type: Type, value: Any):
        self.name = name
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return f'{{{self.name}: {self.type} = {self.value}}}' 


class ExtendedFeature(Feature):
    """An extended feature is feature that can contain additional (configurable) information.
    For example, a Non-Boolean feature, attributed feature, or documentation information.
    
    A Non-Boolean feature is a normal feature that includes a configurable type
    (e.g., Integer, Date). The most common example of non-boolean feature is the numerical feature.

    An attributed feature is a normal feature that can contain one or more attributes.
    """
    
    def __init__(
        self,
        name: str,
        relations: Optional[list[Relation]] = None,
        parent: Optional['Feature'] = None,
        is_abstract: bool = False,
        type: Optional[Type] = None,
        attributes: Optional[list[Attribute]] = None,
        annotations: Optional[list[Annotation]] = None
    ):
        super().__init__(name, relations, parent, is_abstract)
        self.type: Type = type
        self.attributes = [] if attributes is None else attributes
        self.annotations = [] if annotations is None else annotations
    
    # @staticmethod
    # def extend_feature(feature: Feature, 
    #                    type: Optional[Type] = None,
    #                    attributes: Optional[list[Attribute]] = None,
    #                    annotations: Optional[list[Annotation]] = None) -> 'ExtendedFeature':
    #     return ExtendedFeature(feature.name, 
    #                            feature.relations, 
    #                            feature.parent, 
    #                            feature.is_abstract,
    #                            type,
    #                            attributes,
    #                            annotations)


class ExtendedFeatureModel(FeatureModel):

    @staticmethod
    def get_extension() -> str:
        return 'efm'

    def __init__(
        self,
        root: Feature,
        constraints: Optional[list[Constraint]] = None
    ) -> None:
        super().__init__(root, constraints)

    def get_attributes(self) -> dict[Feature, list[Attribute]]:
        attributes = {}
        for feature in self.get_features():
            if isinstance(ExtendedFeature, feature):
                attributes[feature] = feature.attributes
            else:
                attributes[feature] = []
        return attributes

    def get_annotations(self) -> dict[Feature, list[Annotation]]:
        annotations = {}
        for feature in self.get_features():
            if isinstance(ExtendedFeature, feature):
                annotations[feature] = feature.annotations
            else:
                annotations[feature] = []
        return annotations
