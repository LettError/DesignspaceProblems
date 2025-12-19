import os, glob, plistlib, math
import plistlib
import math
import io

from fontTools.feaLib.parser import Parser as FeatureParser
from fontTools.feaLib import ast as featureElements

from ufoProcessor import getUFOVersion, getLayer
from ufoProcessor.ufoOperator import UFOOperator
from ufoProcessor.varModels import AxisMapper

from fontPens.digestPointPen import DigestPointStructurePen

from designspaceProblems.problems import DesignSpaceProblem


def parseDigestContours(pat):
    """Parse a digest tuple into per-contour statistics.

    Returns a list of dicts, one per contour:
        {'on_curves': int, 'off_curves': int, 'types': tuple}
    """
    contours = []
    current = None
    for item in pat:
        if isinstance(item, tuple) and item[0] == 'beginPath':
            current = {'on_curves': 0, 'off_curves': 0, 'types': []}
        elif item == 'endPath':
            if current is not None:
                current['types'] = tuple(current['types'])
                contours.append(current)
            current = None
        elif current is not None:
            if item is None:
                current['off_curves'] += 1
            else:
                current['on_curves'] += 1
                current['types'].append(item)
    return contours


def getContourDirection(contour):
    """Calculate contour direction using signed area (shoelace formula).

    Returns 1 for counter-clockwise, -1 for clockwise, 0 for degenerate.
    """
    area = 0
    points = [(p.x, p.y) for p in contour if p.segmentType is not None]
    n = len(points)
    if n < 3:
        return 0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    if area > 0:
        return 1
    elif area < 0:
        return -1
    return 0


def prettyLocation(loc):
    if loc is None:
        return "[no location]"
    t = []
    names = list(loc.keys())
    names.sort()
    for n in names:
        t.append(f'{n}:{loc[n]:9.3f}')
    return '[' + ' '.join(t) + ']'


def prettyFontName(font):
    return f"{font.info.familyName} {font.info.styleName}"


def getUFOLayers(ufoPath):
    # Peek into a ufo to read its layers.
    # <?xml version='1.0' encoding='UTF-8'?>
    # <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    # <plist version="1.0">
    #   <array>
    #     <array>
    #       <string>public.default</string>
    #       <string>glyphs</string>
    #     </array>
    #   </array>
    # </plist>
    layercontentsPath = os.path.join(ufoPath, "layercontents.plist")
    if os.path.exists(layercontentsPath):
        with open(layercontentsPath, 'rb') as f:
            p = plistlib.load(f)
        return [a for a, b in p]
    return []


class UnicodeCollector(object):
    def __init__(self):
        # do some admin on the unicodes of master glyphs
        # each glyph can have multiple unicodes
        # so rake in all unicodes of all masters
        self.unicodes = {}
        self.masterCount = 0

    def add(self, glyph):
        # assume these are mathglyphs
        self.masterCount += 1
        if not glyph.unicodes:
            if None not in self.unicodes:
                self.unicodes[None] = 0
            self.unicodes[None] += 1
            return
        for u in glyph.unicodes:
            if u not in self.unicodes:
                self.unicodes[u] = 0
            self.unicodes[u] += 1

    def evaluate(self):
        # so what do we think of what we've seen
        incomplete = []
        for u, count in self.unicodes.items():
            if count != self.masterCount:
                if u is None:
                    incomplete.append("None")
                else:
                    incomplete.append(f"0x{u:X}")
        return incomplete


class DesignSpaceChecker(object):

    _registeredTags = dict(wght='weight', wdth='width', slnt='slant', opsz='optical', ital='italic')
    _structuralProblems = []

    def __init__(self, pathOrObject):
        # check things

        self.problems = []
        self.axesOK = None
        self.mapper = None
        if isinstance(pathOrObject, str):
            #self.ds = DesignSpaceProcessor()
            self.ds = UFOOperator()
            if os.path.exists(pathOrObject):
                try:
                    self.ds.read(pathOrObject)
                except Exception:
                    self.problems.append(DesignSpaceProblem(0, 0, dict()))
        else:
            self.ds = pathOrObject

    def data_getAxisValues(self, axisName=None, mapped=True):
        # return the minimum / default / maximum for the axis
        # it's possible we ask for an axis that is not in the document.
        if self.ds is None:
            return None
        if axisName is None:
            # get all of them
            axes = {}
            for ad in self.ds.axes:
                if hasattr(ad, "values"):
                    axisMinimum = min(ad.values)
                    axisMaximum = max(ad.values)
                    axisDefault = ad.default
                else:
                    axisMinimum = ad.minimum
                    axisMaximum = ad.maximum
                    axisDefault = ad.default
                # should these be mapped?
                #$$
                if mapped:
                    #axes[ad.name] = (ad.map_forward(ad.minimum), ad.map_forward(ad.default), ad.map_forward(ad.maximum))
                    axes[ad.name] = (ad.map_forward(axisMinimum), ad.map_forward(axisDefault), ad.map_forward(axisMaximum))
                else:
                    #axes[ad.name] = (ad.minimum, ad.default, ad.maximum)
                    axes[ad.name] = (axisMinimum, axisDefault, axisMaximum)
            return axes
        for ad in self.ds.axes:
            if ad.name == axisName:
                if mapped:
                    return (ad.map_forward(ad.minimum), ad.map_forward(ad.default), ad.map_forward(ad.maximum))
                else:
                    return ad.minimum, ad.default, ad.maximum
        return None

    def hasStructuralProblems(self):
        # check if we have any errors from categories file / axes / sources
        # this does not guarantee there won't be other problems!
        for err in self.problems:
            if err.isStructural():
                return True
        return False

    def hasDesignProblems(self):
        # check if there are errors in font data itself, glyphs, fontinfo, kerning
        if self.hasStructuralProblems():
            return -1
        for err in self.problems:
            if err.category in [4, 5, 6]:
                return True
        return False

    def hasRulesProblems(self):
        # check if there are errors in rule data
        if self.hasStructuralProblems():
            return -1
        for err in self.problems:
            if err.category in [7]:
                return True
        return False

    def checkEverything(self):
        if not self.ds:
            return False
        # designspace specific
        self.checkDesignSpaceGeometry()
        # check sources, discrete or continuous
        discreteLocations = self.ds.getDiscreteLocations()
        if not discreteLocations:
            discreteLocations = [None]
        for dloc in discreteLocations:
            self.checkSources(discreteLocation=dloc)
            self.checkInstances(discreteLocation=dloc)
        if not self.hasStructuralProblems():
            # font specific
            self.ds.loadFonts()
            for dloc in discreteLocations:
                #self.nf = self.ds.getNeutralFont()
                self.checkKerning(discreteLocation=dloc)
                self.checkFontInfo(discreteLocation=dloc)
                self.checkGlyphs(discreteLocation=dloc)
            self.checkRules()
            self.checkFeatures()

    def checkDesignSpaceGeometry(self):
        # 1.0	no axes defined
        if len(self.ds.axes) == 0:
            self.problems.append(DesignSpaceProblem(1,0))
        # 1.1	axis missing
        allAxes = []
        for i, ad in enumerate(self.ds.axes):
            axisIsDiscrete = hasattr(ad, "values")
            axisOK = True
            # 1.5	axis name missing
            if ad.name is None:
                axisName = f"unnamed_axis_{i}"
                self.problems.append(DesignSpaceProblem(1,5, dict(axisName=axisName)))
                axisOK = False
            else:
                axisName = ad.name
            # 1.2	axis maximum missing
            if not axisIsDiscrete and ad.maximum is None:
                self.problems.append(DesignSpaceProblem(1,2, dict(axisName=axisName)))
                axisOK = False
            # 1.3	axis minimum missing
            if not axisIsDiscrete and ad.minimum is None:
                self.problems.append(DesignSpaceProblem(1,3, dict(axisName=axisName)))
                axisOK = False
            # 1.4	axis default missing
            if ad.default is None:
                self.problems.append(DesignSpaceProblem(1,4, dict(axisName=axisName)))
                axisOK = False

            # problem: in order to check the validity of the axis values
            # we need to get the mapped values for minimum, default and maximum.
            # but any problems in the axis map can only be determined if we
            # are sure the axis is valid.
            if not axisIsDiscrete:
                # its a continuous axis
                axisMin, axisDef, axisMax = self.data_getAxisValues(axisName, mapped=False)
                mappedAxisMin, mappedAxisDef, mappedAxisMax = self.data_getAxisValues(axisName, mapped=True)
                # 1,13 mapped minimum > mapped maximum
                if mappedAxisMin > mappedAxisMax:
                    self.problems.append(DesignSpaceProblem(1,13, dict(axisName=axisName, maximum=mappedAxisMax, minimum=mappedAxisMin)))
                    axisOK = False
                # 1,14 mapped minimum > mapped maximum
                if axisMin > axisMax:
                    self.problems.append(DesignSpaceProblem(1,14, dict(axisName=axisName, maximum=mappedAxisMax, minimum=mappedAxisMin)))
                    axisOK = False

                # 1,9 minimum and maximum value are the same and not None
                if (mappedAxisMin == mappedAxisMax) and mappedAxisMin != None:
                    self.problems.append(DesignSpaceProblem(1,9, dict(axisName=axisName)))
                    axisOK = False
                # 1,10 default not between minimum and maximum
                if mappedAxisMin is not None and mappedAxisMax is not None and mappedAxisDef is not None:
                    if not ((mappedAxisMin < mappedAxisDef <= mappedAxisMax) or (mappedAxisMin <= mappedAxisDef < mappedAxisMax)):
                        self.problems.append(DesignSpaceProblem(1,10, dict(axisName=axisName)))
                        axisOK = False
            else:
                # its a discrete axis
                if ad.values is None:
                    # 1,30 discrete axis values missing
                    self.problems.append(DesignSpaceProblem(1,30, dict(axisName=axisName)))
                    axisOK = False
                elif ad.default not in ad.values:
                    # 1,31 discrete axis default not in values
                    self.problems.append(DesignSpaceProblem(1,31, dict(axisName=axisName)))
                    axisOK = False
            # 1.6	axis tag missing
            if ad.tag is None:
                self.problems.append(DesignSpaceProblem(1,6, dict(axisName=axisName)))
                axisOK = False
            # 1.7	axis tag mismatch
            else:
                if ad.tag in self._registeredTags:
                    regName = self._registeredTags[ad.tag]
                    # no casing preference
                    if regName not in axisName.lower():
                        self.problems.append(DesignSpaceProblem(1,6, dict(axisName=axisName)))
                        axisOK = False
            allAxes.append(axisOK)
            if axisOK:
                # get the mapped values
                # check the map for this axis
                # 1.8	mapping table has overlaps
                inputs = []
                outputs = []
                if len(ad.map)>0:
                    last = None
                    for a, b in ad.map:
                        if last is None:
                            last = a, b
                            continue
                        da = a-last[0]
                        db = b-last[1]
                        inputs.append(da)
                        outputs.append(db)
                        last = a,b
                if len(outputs)>0:
                    if min(outputs)<=0 and max(outputs)>=0:
                        p = DesignSpaceProblem(1,12, dict(axisName=axisName, axisMap=ad.map))
                        self.problems.append(p)
                if len(inputs)>0:
                    # the graph can only be positive or negative
                    # it can't be both, so that's what we test for
                    if min(inputs)<=0 and max(inputs)>=0:
                        p = DesignSpaceProblem(1,11, dict(axisName=axisName, axisMap=ad.map))
                        self.problems.append(p)

        # XX
        if all(allAxes):
            self.mapper = AxisMapper(self.ds.axes)

    def hasDiscreteAxes(self):
        if hasattr(self.ds, "hasDiscreteAxes"):
            return self.ds.hasDiscreteAxes()
        return None

    def getDiscreteLocations(self, bend=True):
        # wrapper for ds.getDiscreteLocations
        # XX not sure we need the bends here
        # if we have discrete axes: return a list of all the defaults
        # if we don't: return a list with the one default.
        # so we can iterate over the answer no matter where it is from
        if hasattr(self.ds, "getDiscreteLocations"):
            return self.ds.getDiscreteLocations()
        return [self.ds.newDefaultLocation(bend=True)]

    def checkLocationForIllegalDiscreteValues(self, location, descriptorType="source"):
        # check this location for values on discrete axes that are not defined.
        discreteAxes = self.ds.getOrderedDiscreteAxes()
        for d in discreteAxes:
            if not location.get(d.name, None) in d.values:
                if descriptorType == "source":
                    self.problems.append(DesignSpaceProblem(2,13, dict(axisValues=d.values, locationValue=location.get(d.name, None))))
                elif descriptorType == "instance":
                    self.problems.append(DesignSpaceProblem(3,12, dict(axisValues=d.values, locationValue=location.get(d.name, None))))

    def checkSources(self, discreteLocation=None):
        #@@
        axisValues = self.data_getAxisValues()
        if discreteLocation is None:
            # no discrete location means no discrete axes, so we only have one interpolating system
            # 2,0 no sources defined
            if len(self.ds.sources) == 0:
                self.problems.append(DesignSpaceProblem(2,0))
        else:
            # we're in a space with mixed axes, we can have multiple interpolation systems
            sources = self.ds.findSourceDescriptorsForDiscreteLocation(discreteLocation)
            if len(sources) == 0:
                self.problems.append(DesignSpaceProblem(2,0, details=f'no sources for discrete location {discreteLocation}'))

        for i, sd in enumerate(self.ds.sources):
            if sd.path is None:
                self.problems.append(DesignSpaceProblem(2,1, dict(path=sd.path)))
            # 2,1 source UFO missing
            elif not os.path.exists(sd.path):
                self.problems.append(DesignSpaceProblem(2,1, dict(path=sd.path)))
            else:
                # 2,2 source UFO format too old
                # XX what is too old, what to do with UFOZ
                formatVersion = getUFOVersion(sd.path)
                if formatVersion < 3:
                    self.problems.append(DesignSpaceProblem(2,2, dict(path=sd.path, version=formatVersion)))
                else:
                    # 2,3 source layer missing
                    if sd.layerName is not None:
                        # XX make this more lazy?
                        # or a faster scan that doesn't load the whole ufo?
                        if not sd.layerName in getUFOLayers(sd.path):
                            self.problems.append(DesignSpaceProblem(2,3, dict(path=sd.path, layerName=sd.layerName)))
                if sd.location is None:
                    # 2,4 source location missing
                    self.problems.append(DesignSpaceProblem(2,4, dict(path=sd.path)))
                else:
                    for axisName, axisValue in sd.location.items():
                        if type(axisValue) == tuple:
                            axisValues = list(axisValue)
                            self.problems.append(DesignSpaceProblem(2,10, dict(location=sd.location)))
                        else:
                            if axisName in axisValues:
                                # 2,6 source location has out of bounds value
                                mn, df, mx = axisValues[axisName]
                                if axisValue < mn or axisValue > mx:
                                    self.problems.append(DesignSpaceProblem(2,6, dict(axisMinimum=mn, axisMaximum=mx, locationValue=axisValue)))
                            else:
                                # 2,5 source location has value for undefined axis
                                self.problems.append(DesignSpaceProblem(2,5, dict(axisName=axisName)))
        mappedDefaultLocation = self.ds.newDefaultLocation(bend=True)
        mappedDefaultCandidates = []
        for i, sd in enumerate(self.ds.sources):
            if sd.location == mappedDefaultLocation:
                mappedDefaultCandidates.append(sd)
        if len(mappedDefaultCandidates) == 0:
            # 2,7 no source on mapped default location
            self.problems.append(DesignSpaceProblem(2,7))
        elif len(mappedDefaultCandidates) > 1:
            # 2,8 multiple sources on default location
            self.problems.append(DesignSpaceProblem(2,8))
        allLocations = {}
        hasAnisotropicLocation = False
        for i, sd in enumerate(self.ds.sources):
            key = list(sd.location.items())
            key.sort()
            key = tuple(key)
            if key not in allLocations:
                allLocations[key] = []
            allLocations[key].append(sd)
            # if tuple in [type(n) for n in sd.location.values()]:
            #     # 2,10 source location is anisotropic
            #     self.problems.append(DesignSpaceProblem(2,10))
        for key, items in allLocations.items():
            if len(items) > 1 and items[0].location != mappedDefaultLocation:
                # 2,9 multiple sources on location
                self.problems.append(DesignSpaceProblem(2,9))
        onAxis = set()
        # check if the discrete values in the source location are valid
        for i, sd in enumerate(self.ds.sources):
            self.checkLocationForIllegalDiscreteValues(sd.location)
        # check if all axes have on-axis masters
        for i, sd in enumerate(self.ds.sources):
            name = self.isOnAxis(sd.location)
            if name is not None and name is not False:
                onAxis |= set([name])
        for axisName in axisValues:
            if axisName not in onAxis:
                self.problems.append(DesignSpaceProblem(2,11, dict(axisName=axisName)))

    def isOnAxis(self, loc):
        # test of a location is on-axis
        # if a location is on the default, this will return None.
        axisValues = self.data_getAxisValues(mapped=True)
        checks = []
        lastAxis = None
        for axisName in axisValues.keys():
            default = axisValues.get(axisName)[1]
            if not axisName in loc:
                # the axisName is not in the location
                # assume it is the default, we don't need to test
                isClose = False
            elif type(loc[axisName]) is tuple:
                # let's think about what we're testing here
                # we want to find out whether this location is on an axis
                # in case of an anisotropic value one of the values
                # could be on the default and the other could be somewhere else.
                # That would qualify as an on-axis.
                vx, vy = loc[axisName]
                isClose = math.isclose(vx, default) or math.isclose(vy, default)
            else:
                isClose = math.isclose(loc.get(axisName, default), default)
            if not isClose:
                checks.append(1)
                lastAxis = axisName
        if sum(checks)<=1:
            return lastAxis
        return False

    def checkInstances(self, discreteLocation=None):
        axisValues = self.data_getAxisValues()
        defaultLocation = self.ds.newDefaultLocation(bend=True)
        defaultCandidates = []

        discreteName = ""
        if discreteLocation:
            # check f there are instances defined for this discrete location
            discreteName = self.discreteLocationAsString(discreteLocation)
        if len(self.ds.instances) == 0:
            self.problems.append(DesignSpaceProblem(3,10))
        for i, jd in enumerate(self.ds.instances):
            # it's `jd` because `id` is obviously a reserved word
            jdLocation = jd.getFullDesignLocation(self.ds)
            
            if jdLocation is None:
                # 3,1   instance location missing
                self.problems.append(DesignSpaceProblem(3,1, dict(path=jd.path)))
            else:
                continuous, discrete = self.ds.splitLocation(jdLocation)
                for axisName, axisValue in continuous.items():
                    if type(axisValue) == tuple:
                        thisAxisValues = list(axisValue)
                    else:
                        thisAxisValues = [axisValue]
                    for axisValue in thisAxisValues:
                        if axisName in axisValues:
                            mn, df, mx = axisValues[axisName]
                            if not  (mn <= axisValue <= mx):
                                # 3,5   instance location requires extrapolation
                                # 3,3   instance location has out of bounds value
                                deets = f'{jd.familyName}-{jd.styleName} {axisName}: {axisValue} is outside of extremes'
                                self.problems.append(DesignSpaceProblem(3,3, dict(min=mn, max=mx, value=axisValue), details=deets))
                                self.problems.append(DesignSpaceProblem(3,5, dict(min=mn, max=mx, value=axisValue), details=deets))
                        else:
                            # doesn't happen as ufoprocessor won't read add undefined axes to the locations
                            # 3,2   instance location has value for undefined axis
                            self.problems.append(DesignSpaceProblem(3,2, dict(axisName=axisName)))
        # check for illegal values in discrete locations
        for i, jd in enumerate(self.ds.instances):
            jdLocation = jd.getFullUserLocation(self.ds)
            self.checkLocationForIllegalDiscreteValues(jdLocation, descriptorType="instance")
        allLocations = {}
        for i, jd in enumerate(self.ds.instances):
            if not jd.designLocation and not jd.userLocation:
                deets = f'No design or user location for {jd.familyName} {jd.styleName}'
                self.problems.append(DesignSpaceProblem(3,1, dict(instance=i), details=deets))
            else:
                key = list(jd.getFullDesignLocation(self.ds).items())
                key.sort()
                key = tuple(key)
                if key not in allLocations:
                    allLocations[key] = []
                allLocations[key].append((i, jd))
        for key, items in allLocations.items():
            # 3,4   multiple instances on location
            if len(items) > 1:
                deets = f"multiple instances at {prettyLocation(items[0][1].location)}"
                self.problems.append(DesignSpaceProblem(3,4, dict(location=items[0][1].location, instances=[b for a, b in items]), details=deets))

        # 3,5   instance location is anisotropic
        for i, jd in enumerate(self.ds.instances):
            jdLocation = jd.getFullUserLocation(self.ds)
            
            # 3,6   missing family name
            if not jd.familyName:
                deets = f"instance at {prettyLocation(jdLocation)}"
                self.problems.append(DesignSpaceProblem(3,6, dict(instance=jd), details=deets))
            # 3,7   missing style name
            if not jd.styleName:
                deets = f"instance at {prettyLocation(jdLocation)}"
                self.problems.append(DesignSpaceProblem(3,7, dict(instance=jd), details=deets))
            # 3,8   missing output path
            if not jd.filename:
                deets = f"no location for {jd.familyName} {jd.styleName}"
                self.problems.append(DesignSpaceProblem(3,8, dict(instance=jd), details=deets))
        # 3,9   duplicate instances

    def checkGlyphs(self, discreteLocation=None):
        # check all glyphs in all sources for this discrete location
        # need to load the fonts before we can do this
        #nf = self.ds.getNeutralFont(discreteLocation=discreteLocation)

        glyphNames = set()
        # 4.7 default glyph is empty
        sourceDescriptors = self.ds.findSourceDescriptorsForDiscreteLocation(discreteLocation)
        for sourceDescriptor in sourceDescriptors:
            sourceFont = self.ds.fonts[sourceDescriptor.name]
            if sourceFont is None:
                continue
            for glyphName in sourceFont.keys():
                glyphNames.add(glyphName)

        defaultFont = self.ds.findDefaultFont(discreteLocation)
        if defaultFont is not None:
            for glyphName in glyphNames:
                if glyphName not in defaultFont:
                    deets = f'empty glyph at default: {glyphName}'
                    self.problems.append(DesignSpaceProblem(4, 7, dict(glyphName=glyphName), details=deets))
                else:
                    self.checkGlyph(glyphName, discreteLocation=discreteLocation)

    def discreteLocationAsString(self, loc=None):
        if loc is None:
            return ""
        t = []
        axisNames = list(loc.keys())
        axisNames.sort()
        for name in axisNames:
            v = loc[name]
            if int(v) == v:
                vt = f"{int(v)}"
            else:
                vt = f"{v:3.2f}"
            t.append(f"{name}:{vt}")
        return " ".join(t)

    def checkGlyph(self, glyphName, discreteLocation=None):
        # For this test all glyphs will be loaded.
        # 4.6 non-default glyph is empty
        # 4.8 contour has wrong direction
        # 4.9 incompatible constructions for glyph
        # 4.10 different unicodes in glyph
        dLocString = self.discreteLocationAsString(discreteLocation)
        items, unicodesFromOperator = self.ds.collectSourcesForGlyph(glyphName, discreteLocation=discreteLocation, asMathGlyph=False)
        patterns = {}
        contours = {}
        components = {}
        unicodes = UnicodeCollector()
        anchors = {}
        contourStats = {}  # pat -> list of contour stats
        contourDirections = []  # list of (loc, directions) per master
        for loc, mg, masters in items:
            masterName = masters.get('sourceName')
            masterFont = self.ds.fonts.get(masterName)
            masterGlyphName = masters.get('glyphName')
            masterLayerName = masters.get('layerName')
            if masterFont is not None and masterGlyphName is not None:
                masterLayer = getLayer(masterFont, masterLayerName)
                if masterGlyphName in masterLayer:
                    mg = masterLayer[masterGlyphName]
            pp = DigestPointStructurePen()
            # get the structure of the glyph, count a couple of things
            unicodes.add(mg)
            mg.drawPoints(pp)
            pat = pp.getDigest()
            for cm in mg.components:
                # collect component counts
                if not cm.baseGlyph in components:
                    components[cm.baseGlyph] = 0
                components[cm.baseGlyph] += 1
            for ad in mg.anchors:
                # collect anchor counts
                if not hasattr(ad, 'name'):
                    # what kind of object do we have here?
                    continue
                if ad.name not in anchors:
                    anchors[ad.name] = 0
                anchors[ad.name] += 1
            # collect patterns of the whole glyph
            # the pattern is the key
            if pat not in patterns:
                patterns[pat] = []
            patterns[pat].append(loc)
            contourCount = 0
            for item in pat:
                if item is None: continue
                if "beginPath" in item:
                    contourCount += 1
            if contourCount not in contours:
                contours[contourCount] = 0
            contours[contourCount] += 1
            # collect per-contour stats for detailed checks
            if pat not in contourStats:
                contourStats[pat] = parseDigestContours(pat)
            # collect contour directions for 4.8
            directions = tuple(getContourDirection(c) for c in mg)
            contourDirections.append((loc, directions))
        unicodeResults = unicodes.evaluate()
        if unicodeResults:
            deets = f'multiple unicode values in glyph {glyphName} {dLocString}: {", ".join(unicodeResults)}'
            if discreteLocation is not None:
                self.problems.append(DesignSpaceProblem(4,10, dict(glyphName=glyphName, unicodes=unicodeResults, discreteLocation=dLocString)))
            else:
                self.problems.append(DesignSpaceProblem(4,10, dict(glyphName=glyphName, unicodes=unicodeResults)))
        if len(components) != 0:
            for baseGlyphName, refCount in components.items():
                if refCount % len(items) != 0:
                    # there can be multiples of components with the same baseglyph
                    # so the actual number of components is not important
                    # but each master should have the same number
                    self.problems.append(DesignSpaceProblem(4,1, dict(glyphName=glyphName, baseGlyph=baseGlyphName, discreteLocation=dLocString)))
        if len(anchors) != 0:
            for anchorName, anchorCount in anchors.items():
                if anchorCount < len(items):
                    # 4.2 different number of anchors in glyph
                    self.problems.append(DesignSpaceProblem(4,2, dict(glyphName=glyphName, anchorName=anchorName, discreteLocation=dLocString)))
        if len(contours) != 1:
            # 4.0 different number of contours in glyph
            self.problems.append(DesignSpaceProblem(4,0, dict(glyphName=glyphName, discreteLocation=dLocString)))
        if len(patterns.keys()) > 1:
            # 4,9 incompatible constructions for glyph
            self.problems.append(DesignSpaceProblem(4,9, dict(glyphName=glyphName, discreteLocation=dLocString)))
            # detailed checks: compare first pattern to others
            pats = list(contourStats.keys())
            refStats = contourStats[pats[0]]
            reported43 = set()
            reported44 = set()
            reported45 = set()
            for otherPat in pats[1:]:
                otherStats = contourStats[otherPat]
                # compare contour by contour
                minLen = min(len(refStats), len(otherStats))
                for ci in range(minLen):
                    ref = refStats[ci]
                    other = otherStats[ci]
                    if ref['on_curves'] != other['on_curves'] and ci not in reported43:
                        # 4.3 different number of on-curve points on contour
                        self.problems.append(DesignSpaceProblem(4,3, dict(glyphName=glyphName, contourIndex=ci, discreteLocation=dLocString)))
                        reported43.add(ci)
                    if ref['off_curves'] != other['off_curves'] and ci not in reported44:
                        # 4.4 different number of off-curve points on contour
                        self.problems.append(DesignSpaceProblem(4,4, dict(glyphName=glyphName, contourIndex=ci, discreteLocation=dLocString)))
                        reported44.add(ci)
                    if ref['types'] != other['types'] and ci not in reported45:
                        # 4.5 curve has wrong type
                        self.problems.append(DesignSpaceProblem(4,5, dict(glyphName=glyphName, contourIndex=ci, discreteLocation=dLocString)))
                        reported45.add(ci)
        # 4.8 contour has wrong direction
        if len(contourDirections) > 1:
            refDirs = contourDirections[0][1]
            reportedContours = set()
            for loc, dirs in contourDirections[1:]:
                if dirs != refDirs:
                    for ci, (rd, od) in enumerate(zip(refDirs, dirs)):
                        if rd != od and rd != 0 and od != 0 and ci not in reportedContours:
                            self.problems.append(DesignSpaceProblem(4,8, dict(glyphName=glyphName, contourIndex=ci, discreteLocation=dLocString)))
                            reportedContours.add(ci)

    def _anyKerning(self):
        # return True if there is kerning in one of the masters
        for fontName, fontObj in self.ds.fonts.items():
            if fontObj is not None:
                if len(fontObj.kerning.items()) > 0:
                    return True
        return False

    def checkKerning(self, discreteLocation=None):
        # 5,4 kerning pair missing
        # 5,1 no kerning in default
        nf = self.ds.getNeutralFont(discreteLocation=discreteLocation)
        if nf is None:
            return
        if not self._anyKerning():
            # Check if there is *any* kerning first. If there is no kerning anywhere,
            # we should assume this is intentional and not flood warnings.
            return
        if len(nf.kerning.items()) == 0:
            self.problems.append(DesignSpaceProblem(5,1, dict(fontObj=nf)))
        # 5,5 no kerning groups in default
        if len(nf.groups) == 0:
            self.problems.append(DesignSpaceProblem(5,5, dict(fontObj=nf)))
        defaultGroupNames = list(nf.groups.keys())
        for fontName, fontObj in self.ds.fonts.items():
            if fontObj == nf:
                continue
            if fontObj is None:
                continue
            # 5,0 no kerning in source
            if len(fontObj.kerning.keys()) == 0:
                self.problems.append(DesignSpaceProblem(5,0, dict(font=prettyFontName(fontObj))))
            # 5,6 no kerning groups in source
            if len(fontObj.groups.keys()) == 0:
                self.problems.append(DesignSpaceProblem(5,6, dict(font=prettyFontName(fontObj))))
            for sourceGroupName in fontObj.groups.keys():
                if sourceGroupName not in defaultGroupNames:
                    # 5,3 kerning group missing
                    self.problems.append(DesignSpaceProblem(5,3, dict(font=prettyFontName(fontObj), groupName=sourceGroupName)))
                else:
                    # check if they have the same members
                    sourceGroupMembers = list(fontObj.groups[sourceGroupName])
                    defaultGroupMembers = list(nf.groups[sourceGroupName])
                    if sourceGroupMembers != defaultGroupMembers:  # They're different
                        if sorted(sourceGroupMembers) == sorted(defaultGroupMembers): # but when sorted, they're the same
                             # 5,7 kerning group members sorted differently
                            deets = f'{sourceGroupName}: {sourceGroupMembers}, {defaultGroupMembers}'
                            self.problems.append(DesignSpaceProblem(5,7, dict(font=prettyFontName(fontObj), groupName=sourceGroupName), details=deets))
                        else: # after sorting, the group members was different
                            # 5,2 kerning group members do not match
                            deets = f'{sourceGroupName}: {sourceGroupMembers}, {defaultGroupMembers}'
                            self.problems.append(DesignSpaceProblem(5,2, dict(font=prettyFontName(fontObj), groupName=sourceGroupName), details=deets))

    def checkFontInfo(self, discreteLocation=None):
        nf = self.ds.getNeutralFont(discreteLocation=discreteLocation)
        # check some basic font info values
        # entirely debateable what we should be testing.
        # Let's start with basic geometry
        # 6,3 source font info missing value for xheight
        if nf is None:
            return
        if nf.info.unitsPerEm is None:
            # 6,0 default font info missing value for units per em
            self.problems.append(DesignSpaceProblem(6,0, dict(font=prettyFontName(nf))))
        if nf.info.ascender is None:
            # 6,1 default font info missing value for ascender
            self.problems.append(DesignSpaceProblem(6,1, dict(font=prettyFontName(nf))))
        if nf.info.descender is None:
            # 6,2 default font info missing value for descender
            self.problems.append(DesignSpaceProblem(6,2, dict(font=prettyFontName(nf))))
        if nf.info.descender is None:
            # 6,3 default font info missing value for xheight
            self.problems.append(DesignSpaceProblem(6,3, dict(font=prettyFontName(nf))))
        for fontName, fontObj in self.ds.fonts.items():
            if fontObj == nf:
                continue
            if fontObj is None:
                continue
            # 6,4 source font unitsPerEm value different from default unitsPerEm
            if fontObj.info.unitsPerEm != nf.info.unitsPerEm:
                self.problems.append(DesignSpaceProblem(6,4, dict(font=prettyFontName(fontObj), fontValue=fontObj.info.unitsPerEm, defaultValue=nf.info.unitsPerEm)))

    def checkRules(self, discreteLocation=None):
        # check the rules in the designspace
        # 7.0 source glyph missing
        # 7.1 destination glyph missing
        # 7.8 duplicate conditions
        axisValues = self.data_getAxisValues()
        for i, rd in enumerate(self.ds.rules):
            if rd.name is None:
                name = "unnamed_rule_%d" % i
                self.problems.append(DesignSpaceProblem(7,9, data=dict(rule=name)))
            else:
                name = rd.name
            for a, b in rd.subs:
                if a == b:
                    # 7.2 source and destination glyphs the same
                    self.problems.append(DesignSpaceProblem(7,2, data=dict(rule=name, glyphName=a)))
                for fontName, fontObj in self.ds.fonts.items():
                    if fontObj is None:
                        continue
                    if a not in fontObj:
                        # 7.0 source glyph missing
                        self.problems.append(DesignSpaceProblem(7,0, data=dict(rule=name, glyphName=a, font=prettyFontName(fontObj))))
                    if b not in fontObj:
                        # 7.1 destination glyph missing
                        self.problems.append(DesignSpaceProblem(7,1, data=dict(rule=name, glyphName=b, font=prettyFontName(fontObj))))
            if not rd.subs:
                # 7.3 no substition glyphs defined
                self.problems.append(DesignSpaceProblem(7,3, data=dict(rule=name)))

            if len(rd.conditionSets) == 0:
                # 7.4 no conditionset defined
                self.problems.append(DesignSpaceProblem(7,4, data=dict(rule=name)))
            for cds in rd.conditionSets:
                patterns = {}
                for cd in cds:
                    # check duplicate conditions
                    pat = list(cd.items())
                    pat.sort()
                    pat = tuple(pat)
                    if pat not in patterns:
                        patterns[pat] = True
                    else:
                        self.problems.append(DesignSpaceProblem(7,8, data=dict(rule=name)))

                    if cd['minimum'] == cd['maximum']:
                        # 7.7 condition values are the same
                        self.problems.append(DesignSpaceProblem(7,7, data=dict(rule=name)))
                    if cd['minimum'] is not None and cd['maximum'] is not None:
                        if cd['name'] not in axisValues.keys():
                            # 7.5 condition values on unknown axis
                            self.problems.append(DesignSpaceProblem(7,5, data=dict(rule=name, axisName=cd['name'])))
                        else:
                            if cd['minimum'] < min(axisValues[cd['name']]) or cd['maximum'] > max(axisValues[cd['name']]):
                                # 7.6 condition values out of axis bounds
                                self.problems.append(DesignSpaceProblem(7,6, data=dict(rule=name, axisValues=axisValues[cd['name']],
                                    conditionMinimum=cd.get('minimum'), conditionDefault=cd.get('default'), conditionMaximum=cd.get('maximum'))))
                    else:
                        if cd.get('minimum') is None:
                            self.problems.append(DesignSpaceProblem(7,10, data=dict(rule=name, axisValues=axisValues[cd['name']])))
                        if cd.get('maximum') is None:
                            self.problems.append(DesignSpaceProblem(7,11, data=dict(rule=name, axisValues=axisValues[cd['name']])))

    def checkFeatures(self):
        # check the rules in the designspace
        # 8,0 source features file corrupt
        # 8,1 source is missing feature
        countedFeaturesTags = dict(
            kern=0,
            mark=0,
            mkmk=0
        )
        for fontName, fontObj in self.ds.fonts.items():
            try:
                feaData = io.StringIO(fontObj.features.text)
                feaParser = FeatureParser(feaData, set(fontObj.keys()), followIncludes=True, includeDir=os.path.dirname(fontObj.path))
                existingFeaFile = feaParser.parse()
                for element in existingFeaFile.statements:
                    if isinstance(element, featureElements.FeatureBlock):
                        if element.name in countedFeaturesTags:
                            countedFeaturesTags[element.name] += 1
            except Exception as err:
                self.problems.append(DesignSpaceProblem(8,0, details=str(err)))

        sourceCount = len(self.ds.fonts)
        for tag, value in countedFeaturesTags.items():
            if value == 0:
                # non of the sources have this feature
                continue
            elif value == sourceCount:
                # all fo the sources have this features
                continue
            else:
                self.problems.append(DesignSpaceProblem(8,1, data=dict(feature=tag)))



if __name__ == "__main__":
    import os
    path = "../../tests_ds5/ds5.designspace"
    print(f"testing {path}")
    print("exists:",    os.path.exists(path))
    dc = DesignSpaceChecker(path)
    dc.checkEverything()
    for problem in dc.problems:
        print(problem)


    print(dc.discreteLocationAsString({'countedItems': 1.0, 'outlined': 0.0}))
    print(dc.discreteLocationAsString())
    print(dc.discreteLocationAsString({}))

