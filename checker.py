import os, glob
from errorFunctions import *
import errors
from importlib import reload
reload(errors)
from errors import DesignSpaceError
import ufoProcessor
from ufoProcessor import DesignSpaceProcessor, getUFOVersion, getLayer
from fontParts.fontshell import RFont

class DesignSpaceChecker(object):
    _registeredTags = dict(wght = 'weight', wdth = 'width', slnt = 'slant', opsz = 'optical', ital = 'italic')
    def __init__(self, path):
        # check things
        self.errors = []
        self.ds = DesignSpaceProcessor()
        if os.path.exists(path):
            self.ds.read(path)

    def data_getAxisValues(self, axisName=None):
        # return the minimum / default / maximum for the axis
        # it's possible we ask for an axis that is not in the document.
        if self.ds is None:
            return None
        if axisName is None:
            # get all of them
            axes = {}
            for ad in self.ds.axes:
                axes[ad.name] = (ad.minimum, ad.default, ad.maximum)
            return axes
        for ad in self.ds.axes:
            if ad.name == axisName:
                return ad.minimum, ad.default, ad.maximum
        return None
        
    def checkEverything(self):
        if not self.ds:
            return False
        self.checkDesignSpaceGeometry()
        self.checkSources()
        self.checkInstances()
        self.checkGlyphs()
        self.checkKerning()
        self.checkFontInfo()
        self.checkRules()
    
    def checkDesignSpaceGeometry(self):
        # 1.0	no axes defined
        if len(self.ds.axes) == 0:
            self.errors.append(DesignSpaceError(1,0))
        # 1.1	axis missing
        for i, ad in enumerate(self.ds.axes):
            # 1.5	axis name missing
            if ad.name is None:
                name = "unnamed_axis_%d" %i
                self.errors.append(DesignSpaceError(1,5), dict(name=name))
            else:
                name = ad.name
            # 1.2	axis maximum missing
            if ad.maximum is None:
                self.errors.append(DesignSpaceError(1,2), dict(name=name))
            # 1.3	axis minimum missing
            if ad.minimum is None:
                self.errors.append(DesignSpaceError(1,3), dict(name=name))
            # 1.4	axis default missing
            if ad.default is None:
                self.errors.append(DesignSpaceError(1,4), dict(name=name))
            # 1.6	axis tag missing
            if ad.tag is None:
                self.errors.append(DesignSpaceError(1,6), dict(name=name))
            # 1.7	axis tag mismatch
            else:
                if ad.tag in self._registeredTags:
                    regName = self._registeredTags[ad.tag]
                    if regName not in name.lower():
                        self.errors.append(DesignSpaceError(1,6), dict(name=name))
            # 1.8	mapping table has overlaps
            # XX
    
    def checkSources(self):
        axisValues = self.data_getAxisValues()
        # 2,0 no sources defined
        if len(self.ds.sources) == 0:
            self.errors.append(DesignSpaceError(2,0))
        for i, sd in enumerate(self.ds.sources):
            # 2,1 source UFO missing
            if not os.path.exists(sd.path):
                self.errors.append(DesignSpaceError(2,1, dict(path=sd.path)))
            else:
                # 2,2 source UFO format too old
                # XX what is too old, what to do with UFOZ
                formatVersion = getUFOVersion(sd.path)
                if formatVersion < 3:
                    self.errors.append(DesignSpaceError(2,2, dict(path=sd.path, version=formatVersion)))
                else:
                    # 2,3 source layer missing
                    if sd.layerName is not None:
                        ufo = RFont(sd.path, showInterface=False)    
                        layerObj = getLayer(ufo, sd.layerName)
                        if layerObj is None:
                            self.errors.append(DesignSpaceError(2,3, dict(path=sd.path, layerName=sd.layerName)))
                if sd.location is None:            
                    # 2,4 source location missing
                    self.errors.append(DesignSpaceError(2,4, dict(path=sd.path)))
                else:
                    for axisName, axisValue in sd.location.items():
                        if axisName in axisValues:
                            # 2,6 source location has out of bounds value
                            mn, df, mx = axisValues[axisName]
                            if axisValue < mn or axisValue > mx:
                                self.errors.append(DesignSpaceError(2,6, dict(axisMinimum=mn, axisMaximum=mx, locationValue=axisValue)))
                        else:
                            # 2,5 source location has value for undefined axis
                            self.errors.append(DesignSpaceError(2,5, dict(axisName=axisName)))
        defaultLocation = self.ds.newDefaultLocation()
        defaultCandidates = []
        for i, sd in enumerate(self.ds.sources):
            if sd.location == defaultLocation:
                defaultCandidates.append(sd)
        if len(defaultCandidates) == 0:
            # 2,7 no source on default location
            self.errors.append(DesignSpaceError(2,7))
        elif len(defaultCandidates) > 1:
            # 2,8 multiple sources on default location
            self.errors.append(DesignSpaceError(2,8))
        allLocations = {}
        hasAnisotropicLocation = False
        for i, sd in enumerate(self.ds.sources):
            key = list(sd.location.items())
            key.sort()
            key = tuple(key)
            if key not in allLocations:
                allLocations[key] = []
            allLocations[key].append(sd)
            if tuple in [type(n) for n in sd.location.values()]:
                # 2,10 source location is anisotropic
                self.errors.append(DesignSpaceError(2,10))
        for key, items in allLocations.items():
            if len(items) > 1 and items[0].location != defaultLocation:
                # 2,9 multiple sources on location
                self.errors.append(DesignSpaceError(2,9))
    
    def checkInstances(self):
        axisValues = self.data_getAxisValues()
        defaultLocation = self.ds.newDefaultLocation()
        defaultCandidates = []
        for i, jd in enumerate(self.ds.instances):
            if jd.location is None:            
                # 3,1   instance location missing
                self.errors.append(DesignSpaceError(3,1, dict(path=jd.path)))
            else:
                for axisName, axisValue in jd.location.items():
                    if type(axisValue) == tuple:
                        axisValues = list(axisValue)
                    else:
                        axisValues = [axisValue]
                    for axisValue in axisValues:
                        if axisName in axisValues:
                            # 3,5   instance location requires extrapolation
                            # 3,3   instance location has out of bounds value
                            mn, df, mx = axisValues[axisName]
                            if axisValue < mn or axisValue > mx:
                                self.errors.append(DesignSpaceError(3,3, dict(axisMinimum=mn, axisMaximum=mx, locationValue=axisValue)))
                                self.errors.append(DesignSpaceError(3,5, dict(axisMinimum=mn, axisMaximum=mx, locationValue=axisValue)))
                            else:
                                # 3,2   instance location has value for undefined axis
                                self.errors.append(DesignSpaceError(3,2, dict(axisName=axisName)))

        allLocations = {}
        for i, jd in enumerate(self.ds.instances):
            key = list(jd.location.items())
            key.sort()
            key = tuple(key)
            if key not in allLocations:
                allLocations[key] = []
            allLocations[key].append((i,jd))
        for key, items in allLocations.items():
            # 3,4   multiple sources on location
            if len(items) > 1:
                self.errors.append(DesignSpaceError(3,4, dict(location=items[0][1].location, instances=[a for a,b in items])))
        
        # 3,5   instance location is anisotropic
        for i, jd in enumerate(self.ds.instances):
            # 3,6   missing family name
            if jd.familyName is None:
                self.errors.append(DesignSpaceError(3,6, dict(instance=i)))
            # 3,7   missing style name
            if jd.styleName is None:
                self.errors.append(DesignSpaceError(3,7, dict(instance=i)))
            # 3,8   missing output path
            if jd.path is None:
                self.errors.append(DesignSpaceError(3,8, dict(instance=i)))
        # 3,9   duplicate instances
    
    def checkGlyphs(self):
        pass
    
    def checkKerning(self):
        pass
    
    def checkFontInfo(self):
        pass
    
    def checkRules(self):
        pass
        

if __name__ == "__main__":
    ufoProcessorRoot = "/Users/erik/code/ufoProcessor/Tests"
    paths = []
    for name in os.listdir(ufoProcessorRoot):
        p = os.path.join(ufoProcessorRoot, name)
        if os.path.isdir(p):
            p2 = os.path.join(p, "*.designspace")
            paths += glob.glob(p2)
    for p in paths:
        dc = DesignSpaceChecker(p)
        dc.checkEverything()
        if dc.errors:
            print("\n")
            print(os.path.basename(p))
            # search for specific errors!
            for n in dc.errors:
                print("\t" + str(n))
            for n in dc.errors:
                if n.category == 3:
                    print("\t -- "+str(n))