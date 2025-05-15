from rhea import language_constructs as lc


class FMToolInfo():

    def __init__(self, name: str, extension: str, support: set[lc.LanguageConstruct]) -> None:
        self._name = name 
        self._extension = extension
        self._support = support

    @property
    def name(self) -> str:
        return self._name

    @property
    def support(self) -> set[lc.LanguageConstruct]:
        return self._support

    @property
    def extension(self) -> str:
        return self._extension


def get_tools_info() -> list[FMToolInfo]:
    tools = []
    tools.append(FMToolInfo('UVL', 'uvl', [lc.LCFeature,
                                    lc.LCNonUniqueFeature,
                                    lc.LCAbstractFeature,
                                    lc.LCOptionalFeature,
                                    lc.LCMandatoryFeature,
                                    lc.LCOrGroupFeature,
                                    lc.LCXorGroupFeature,
                                    lc.LCConstraint,
                                    lc.LCRequiresConstraint,
                                    lc.LCExcludesConstraint,
                                    lc.LCPseudoComplexConstraint,
                                    lc.LCStrictComplexConstraint]))
    tools.append(FMToolInfo('FeatureIDE', 'xml', [lc.LCFeature,
                                           lc.LCAbstractFeature,
                                           lc.LCOptionalFeature,
                                           lc.LCMandatoryFeature,
                                           lc.LCOrGroupFeature,
                                           lc.LCXorGroupFeature,
                                           lc.LCConstraint,
                                           lc.LCRequiresConstraint,
                                           lc.LCExcludesConstraint,
                                           lc.LCPseudoComplexConstraint,
                                           lc.LCStrictComplexConstraint]))
    tools.append(FMToolInfo('Glencoe', 'gfm.json', [lc.LCFeature,
                                        lc.LCOptionalFeature,
                                        lc.LCMandatoryFeature,
                                        lc.LCOrGroupFeature,
                                        lc.LCXorGroupFeature,
                                        lc.LCCardinalityGroupFeature,
                                        lc.LCOrGroupMandatoryFeature,
                                        lc.LCConstraint,
                                        lc.LCRequiresConstraint,
                                        lc.LCExcludesConstraint,
                                        lc.LCPseudoComplexConstraint,
                                        lc.LCStrictComplexConstraint]))
    tools.append(FMToolInfo('SPLOT', 'sxfm.xml', [lc.LCFeature,
                                        lc.LCOptionalFeature,
                                        lc.LCMandatoryFeature,
                                        lc.LCOrGroupFeature,
                                        lc.LCXorGroupFeature,
                                        lc.LCMultipleGroupDecomposition,
                                        lc.LCConstraint,
                                        lc.LCRequiresConstraint,
                                        lc.LCExcludesConstraint,
                                        lc.LCPseudoComplexConstraint,
                                        lc.LCStrictComplexConstraint]))
    tools.append(FMToolInfo('Rhea', 'json', [lc.LCFeature,
                                    lc.LCNonUniqueFeature,
                                    lc.LCAbstractFeature,
                                    lc.LCOptionalFeature,
                                    lc.LCMandatoryFeature,
                                    lc.LCOrGroupFeature,
                                    lc.LCXorGroupFeature,
                                    lc.LCMutexGroupFeature,
                                    lc.LCCardinalityGroupFeature,
                                    lc.LCOrGroupMandatoryFeature,
                                    lc.LCMultipleGroupDecomposition,
                                    lc.LCConstraint,
                                    lc.LCRequiresConstraint,
                                    lc.LCExcludesConstraint,
                                    lc.LCPseudoComplexConstraint,
                                    lc.LCStrictComplexConstraint]))
    return tools
