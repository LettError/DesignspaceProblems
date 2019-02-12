# generated from errors.py
from designspaceProblems import DesignSpaceProblem
def fileCorruptError(**kwargs):
    # file corrupt, (0, 0)
    return DesignSpaceProblem(0,0,data=kwargs)

def noAxesDefinedError(**kwargs):
    # no axes defined, (1, 0)
    return DesignSpaceProblem(1,0,data=kwargs)

def axisMissingError(**kwargs):
    # axis missing, (1, 1)
    return DesignSpaceProblem(1,1,data=kwargs)

def axisMaximumMissingError(**kwargs):
    # axis maximum missing, (1, 2)
    return DesignSpaceProblem(1,2,data=kwargs)

def axisMinimumMissingError(**kwargs):
    # axis minimum missing, (1, 3)
    return DesignSpaceProblem(1,3,data=kwargs)

def axisDefaultMissingError(**kwargs):
    # axis default missing, (1, 4)
    return DesignSpaceProblem(1,4,data=kwargs)

def axisNameMissingError(**kwargs):
    # axis name missing, (1, 5)
    return DesignSpaceProblem(1,5,data=kwargs)

def axisTagMissingError(**kwargs):
    # axis tag missing, (1, 6)
    return DesignSpaceProblem(1,6,data=kwargs)

def axisTagMismatchError(**kwargs):
    # axis tag mismatch, (1, 7)
    return DesignSpaceProblem(1,7,data=kwargs)

def mappingTableHasOverlapsError(**kwargs):
    # mapping table has overlaps, (1, 8)
    return DesignSpaceProblem(1,8,data=kwargs)

def minimumAndMaximumValueAreTheSameError(**kwargs):
    # minimum and maximum value are the same, (1, 9)
    return DesignSpaceProblem(1,9,data=kwargs)

def defaultNotBetweenMinimumAndMaximumError(**kwargs):
    # default not between minimum and maximum, (1, 10)
    return DesignSpaceProblem(1,10,data=kwargs)

def noSourcesDefinedError(**kwargs):
    # no sources defined, (2, 0)
    return DesignSpaceProblem(2,0,data=kwargs)

def sourceUFOMissingError(**kwargs):
    # source UFO missing, (2, 1)
    return DesignSpaceProblem(2,1,data=kwargs)

def sourceUFOFormatTooOldError(**kwargs):
    # source UFO format too old, (2, 2)
    return DesignSpaceProblem(2,2,data=kwargs)

def sourceLayerMissingError(**kwargs):
    # source layer missing, (2, 3)
    return DesignSpaceProblem(2,3,data=kwargs)

def sourceLocationMissingError(**kwargs):
    # source location missing, (2, 4)
    return DesignSpaceProblem(2,4,data=kwargs)

def sourceLocationHasValueForUndefinedAxisError(**kwargs):
    # source location has value for undefined axis, (2, 5)
    return DesignSpaceProblem(2,5,data=kwargs)

def sourceLocationHasOutOfBoundsValueError(**kwargs):
    # source location has out of bounds value, (2, 6)
    return DesignSpaceProblem(2,6,data=kwargs)

def noSourceOnDefaultLocationError(**kwargs):
    # no source on default location, (2, 7)
    return DesignSpaceProblem(2,7,data=kwargs)

def multipleSourcesOnDefaultLocationError(**kwargs):
    # multiple sources on default location, (2, 8)
    return DesignSpaceProblem(2,8,data=kwargs)

def multipleSourcesOnLocationError(**kwargs):
    # multiple sources on location, (2, 9)
    return DesignSpaceProblem(2,9,data=kwargs)

def sourceLocationIsAnisotropicError(**kwargs):
    # source location is anisotropic, (2, 10)
    return DesignSpaceProblem(2,10,data=kwargs)

def instanceLocationMissingError(**kwargs):
    # instance location missing, (3, 1)
    return DesignSpaceProblem(3,1,data=kwargs)

def instanceLocationHasValueForUndefinedAxisError(**kwargs):
    # instance location has value for undefined axis, (3, 2)
    return DesignSpaceProblem(3,2,data=kwargs)

def instanceLocationHasOutOfBoundsValueError(**kwargs):
    # instance location has out of bounds value, (3, 3)
    return DesignSpaceProblem(3,3,data=kwargs)

def multipleInstancesOnLocationError(**kwargs):
    # multiple instances on location, (3, 4)
    return DesignSpaceProblem(3,4,data=kwargs)

def instanceLocationIsAnisotropicError(**kwargs):
    # instance location is anisotropic, (3, 5)
    return DesignSpaceProblem(3,5,data=kwargs)

def missingFamilyNameError(**kwargs):
    # missing family name, (3, 6)
    return DesignSpaceProblem(3,6,data=kwargs)

def missingStyleNameError(**kwargs):
    # missing style name, (3, 7)
    return DesignSpaceProblem(3,7,data=kwargs)

def missingOutputPathError(**kwargs):
    # missing output path, (3, 8)
    return DesignSpaceProblem(3,8,data=kwargs)

def duplicateInstancesError(**kwargs):
    # duplicate instances, (3, 9)
    return DesignSpaceProblem(3,9,data=kwargs)

def noInstancesDefinedError(**kwargs):
    # no instances defined, (3, 10)
    return DesignSpaceProblem(3,10,data=kwargs)

def differentNumberOfContoursInGlyphError(**kwargs):
    # different number of contours in glyph, (4, 0)
    return DesignSpaceProblem(4,0,data=kwargs)

def differentNumberOfComponentsInGlyphError(**kwargs):
    # different number of components in glyph, (4, 1)
    return DesignSpaceProblem(4,1,data=kwargs)

def differentNumberOfAnchorsInGlyphError(**kwargs):
    # different number of anchors in glyph, (4, 2)
    return DesignSpaceProblem(4,2,data=kwargs)

def differentNumberOfOncurvePointsOnContourError(**kwargs):
    # different number of on-curve points on contour, (4, 3)
    return DesignSpaceProblem(4,3,data=kwargs)

def differentNumberOfOffcurvePointsOnContourError(**kwargs):
    # different number of off-curve points on contour, (4, 4)
    return DesignSpaceProblem(4,4,data=kwargs)

def curveHasWrongTypeError(**kwargs):
    # curve has wrong type, (4, 5)
    return DesignSpaceProblem(4,5,data=kwargs)

def nondefaultGlyphIsEmptyError(**kwargs):
    # non-default glyph is empty, (4, 6)
    return DesignSpaceProblem(4,6,data=kwargs)

def defaultGlyphIsEmptyError(**kwargs):
    # default glyph is empty, (4, 7)
    return DesignSpaceProblem(4,7,data=kwargs)

def contourHasWrongDirectionError(**kwargs):
    # contour has wrong direction, (4, 8)
    return DesignSpaceProblem(4,8,data=kwargs)

def incompatibleConstructionsForGlyphError(**kwargs):
    # incompatible constructions for glyph, (4, 9)
    return DesignSpaceProblem(4,9,data=kwargs)

def noKerningInSourceError(**kwargs):
    # no kerning in source, (5, 0)
    return DesignSpaceProblem(5,0,data=kwargs)

def noKerningInDefaultError(**kwargs):
    # no kerning in default, (5, 1)
    return DesignSpaceProblem(5,1,data=kwargs)

def kerningGroupMembersDoNotMatchError(**kwargs):
    # kerning group members do not match, (5, 2)
    return DesignSpaceProblem(5,2,data=kwargs)

def kerningGroupMissingInDefaultError(**kwargs):
    # kerning group missing in default, (5, 3)
    return DesignSpaceProblem(5,3,data=kwargs)

def kerningPairMissingError(**kwargs):
    # kerning pair missing, (5, 4)
    return DesignSpaceProblem(5,4,data=kwargs)

def noKerningGroupsInDefaultError(**kwargs):
    # no kerning groups in default, (5, 5)
    return DesignSpaceProblem(5,5,data=kwargs)

def noKerningGroupsInSourceError(**kwargs):
    # no kerning groups in source, (5, 6)
    return DesignSpaceProblem(5,6,data=kwargs)

def defaultFontInfoMissingValueForUnitsPerEmError(**kwargs):
    # default font info missing value for units per em, (6, 0)
    return DesignSpaceProblem(6,0,data=kwargs)

def defaultFontInfoMissingValueForAscenderError(**kwargs):
    # default font info missing value for ascender, (6, 1)
    return DesignSpaceProblem(6,1,data=kwargs)

def defaultFontInfoMissingValueForDescenderError(**kwargs):
    # default font info missing value for descender, (6, 2)
    return DesignSpaceProblem(6,2,data=kwargs)

def defaultFontInfoMissingValueForXheightError(**kwargs):
    # default font info missing value for xheight, (6, 3)
    return DesignSpaceProblem(6,3,data=kwargs)

def sourceFontUnitsPerEmValueDifferentFromDefaultUnitsPerEmError(**kwargs):
    # source font unitsPerEm value different from default unitsPerEm, (6, 4)
    return DesignSpaceProblem(6,4,data=kwargs)

def sourceGlyphMissingError(**kwargs):
    # source glyph missing, (7, 0)
    return DesignSpaceProblem(7,0,data=kwargs)

def destinationGlyphMissingError(**kwargs):
    # destination glyph missing, (7, 1)
    return DesignSpaceProblem(7,1,data=kwargs)

def sourceAndDestinationGlyphsTheSameError(**kwargs):
    # source and destination glyphs the same, (7, 2)
    return DesignSpaceProblem(7,2,data=kwargs)

def noSubstitionGlyphsDefinedError(**kwargs):
    # no substition glyphs defined, (7, 3)
    return DesignSpaceProblem(7,3,data=kwargs)

def noConditionsetDefinedError(**kwargs):
    # no conditionset defined, (7, 4)
    return DesignSpaceProblem(7,4,data=kwargs)

def conditionValuesOnUnknownAxisError(**kwargs):
    # condition values on unknown axis, (7, 5)
    return DesignSpaceProblem(7,5,data=kwargs)

def conditionValuesOutOfAxisBoundsError(**kwargs):
    # condition values out of axis bounds, (7, 6)
    return DesignSpaceProblem(7,6,data=kwargs)

def conditionValuesAreTheSameError(**kwargs):
    # condition values are the same, (7, 7)
    return DesignSpaceProblem(7,7,data=kwargs)

def duplicateConditionsError(**kwargs):
    # duplicate conditions, (7, 8)
    return DesignSpaceProblem(7,8,data=kwargs)
