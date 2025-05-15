from rhea.refactorings import FMRefactoring

from flamapy.metamodels.fm_metamodel.models import FeatureModel


class RefactoringEngine():

    def __init__(self, refactorings: list[FMRefactoring]) -> None:
        self.refactorings = refactorings

    def apply_refactorings(self, model: FeatureModel) -> FeatureModel:
        for ref in self.refactorings:
            if ref.get_language_construct_instances(model) > 0:
                model = ref.transform(model)
        return model
