import csv
import datetime
from typing import Any 


class AttributesCSVReader():
    """Reader for feature attributes in .csv.

    The csv format is as follow:

    Feature, Attribute1, Attribute2, Attribute3,...
    featureAname, valueA1, valueA2, valueA3,... 
    featureBname, valueB1, valueB2, valueB3,...
    ...
    """

    def __init__(self, path: str) -> None:
        self.path = path

    def transform(self) -> dict[str, dict[str, Any]]:
        """Return a dictionary of 'feature name' -> 'attributes',
        where attributes is another dictionary of 'attribute name' -> 'value'."""
        attributes = dict()
        with open(self.path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', skipinitialspace=True)
            header = reader.fieldnames
            for row in reader:
                feature_name = row[header[0]]
                feature_attributes = dict()
                for attr_index in header[1:]:
                    feature_attributes[attr_index] = row[attr_index]
                attributes[feature_name] = feature_attributes
        return attributes
