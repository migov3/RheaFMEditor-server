from typing import Any

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Constraint

from rhea.metamodels.fm_metamodel.models import Attribute, fm_utils


class FM():

    def __init__(self, feature_model: FeatureModel) -> None:
        self.fm: FeatureModel = feature_model
        self._attributes: dict[Feature, list[Attribute]] = {}
        self._constraints: dict[Constraint, ConstraintHelper] = {ctc: ConstraintHelper(ctc) for ctc in self.fm.get_constraints()}

    @property
    def attributes(self) -> dict[Feature, list[Attribute]]:
        return self._attributes

    @attributes.setter
    def attributes(self, features_attributes: dict[str, dict[str, Any]]):
        """features_attributes is a dictionary of 'feature name' -> 'attributes',
        where attributes is another dictionary of 'attribute name' -> 'value'."""
        self._attributes = {}
        for feature_name in features_attributes.keys():
            feature = self.fm.get_feature_by_name(feature_name)
            if feature is None:
                raise Exception(f'Feature {feature_name} does not exist in feature model.')
            attributes = []
            for attr in features_attributes[feature_name]:
                type, value = fm_utils.parse_type_value(features_attributes[attr])
                attribute = Attribute(attr, type, value)
                attributes.append(attribute)
            self._attributes[feature] = attributes

    def get_constraints(self) -> list[Constraint]:
        return list(self._constraints.keys())

    def get_simple_constraints(self) -> list[Constraint]:
        return [ctc for ctc in self._constraints if self._constraints[ctc].is_simple_constraint()]

    def get_complex_constraints(self) -> list[Constraint]:
        return [ctc for ctc in self._constraints if self._constraints[ctc].is_complex_constraint()]

    def get_requires_constraints(self) -> list[Constraint]:
        return [ctc for ctc in self._constraints if self._constraints[ctc].is_requires_constraint()]

    def get_excludes_constraints(self) -> list[Constraint]:
        return [ctc for ctc in self._constraints if self._constraints[ctc].is_excludes_constraint()]

    def get_pseudocomplex_constraints(self) -> list[Constraint]:
        return [ctc for ctc in self._constraints if self._constraints[ctc].is_pseudocomplex_constraint()]

    def get_strictcomplex_constraints(self) -> list[Constraint]:
        return [ctc for ctc in self._constraints if self._constraints[ctc].is_strictcomplex_constraint()]



class ConstraintHelper():

    def __init__(self, constraint: Constraint) -> None:
        self._constraint = constraint
        self._formulas = fm_utils.split_constraint(constraint)

    def is_simple_constraint(self) -> bool:
        return self.is_requires_constraint() or self.is_excludes_constraint()

    def is_complex_constraint(self) -> bool:
        return not self.is_simple_constraint()

    def is_requires_constraint(self) -> bool:
        return fm_utils.is_requires_constraint(self._constraint)

    def is_excludes_constraint(self) -> bool:
        return fm_utils.is_excludes_constraint(self._constraint)

    def is_strictcomplex_constraint(self) -> bool:
        return any(not fm_utils.is_simple_constraint(ctc) for ctc in self._formulas)

    def is_pseudocomplex_constraint(self) -> bool:
        return len(self._formulas) > 1 and all(fm_utils.is_simple_constraint(ctc) for ctc in self._formulas)
