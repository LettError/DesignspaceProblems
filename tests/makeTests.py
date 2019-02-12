# make some tests

import os, glob
from pprint import pprint
import designspaceProblems.problems
from importlib import reload
reload(designspaceProblems.problems)
from designspaceProblems.problems import DesignSpaceProblem
import designspaceProblems
reload(designspaceProblems)
from designspaceProblems import DesignSpaceChecker
import ufoProcessor
from ufoProcessor import DesignSpaceProcessor, getUFOVersion, getLayer, AxisDescriptor, SourceDescriptor, InstanceDescriptor
from fontParts.fontshell import RFont

def makeTests():
    path = os.getcwd()
    errs = designspaceProblems.problems.allProblems()

    # empty designspace
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "empty.designspace")
    d.write(tp)
    dc = DesignSpaceChecker(tp)
    dc.checkEverything()
    assert (1,0) in dc.problems    # no axes defined
    assert (2,0) in dc.problems    # no sources defined
    assert (2,7) in dc.problems    # no source on default location

    # malformed file
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "malformed_file.designspace")
    d.write(tp)
    f = open(tp, 'r')
    d = f.read()
    f.close()
    d += "garbage"*100
    f = open(tp, 'w')
    f.write(d)
    f.close()
    dc = DesignSpaceChecker(tp)
    dc.checkEverything()
    assert (0,0) in dc.problems    # no axes defined

    # malformed axes
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "malformed_axis.designspace")
    a1 = AxisDescriptor()
    a1.name = "snap"
    a1.minimum = 1000
    a1.maximum = 1000
    a1.default = 1000
    a1.tag = "1111"
    d.addAxis(a1)
    a2 = AxisDescriptor()
    a2.name = "crackle"
    a2.minimum = 0
    a2.maximum = 1000
    a2.default = -1000
    a2.tag = "222"
    d.addAxis(a2)
    d.write(tp)
    dc = DesignSpaceChecker(tp)
    dc.checkEverything()
    assert (1,9) in dc.problems    # minimum and maximum value are the same
    assert (1,10) in dc.problems   # minimum and maximum value are the same
    assert (2,0) in dc.problems    # no sources defined
    assert (2,7) in dc.problems    # no source on default location
    
    # ok axis, a source, but no default
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "no_default.designspace")
    a1 = AxisDescriptor()
    a1.name = "snap"
    a1.minimum = 0
    a1.maximum = 1000
    a1.default = 0
    a1.tag = "snap"
    d.addAxis(a1)
    s1 = SourceDescriptor()
    s1.location = dict(snap=500)
    s1.path = os.path.join(path, 'masters','geometryMaster1.ufo')
    d.addSource(s1)
    d.write(tp)
    dc = DesignSpaceChecker(tp)
    dc.checkEverything()
    assert (2,7) in dc.problems    # no source on default location

    # ok axis, multiple sources on default
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "multiple_defaults.designspace")
    a1 = AxisDescriptor()
    a1.name = "snap"
    a1.minimum = 0
    a1.maximum = 1000
    a1.default = 0
    a1.tag = "snap"
    d.addAxis(a1)
    s1 = SourceDescriptor()
    s1.location = dict(snap=0)
    s1.path = os.path.join(path, 'masters','geometryMaster1.ufo')
    d.addSource(s1)
    s2 = SourceDescriptor()
    s2.location = dict(snap=0)
    s2.path = os.path.join(path, 'masters','geometryMaster2.ufo')
    d.addSource(s2)
    d.write(tp)
    dc = DesignSpaceChecker(tp)
    dc.checkEverything()
    assert (2,8) in dc.problems        # multiple sources on default location
    assert (2,1) not in dc.problems    # not: source UFO missing

    # ok axis, source without location
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "source-without-location.designspace")
    a1 = AxisDescriptor()
    a1.name = "snap"
    a1.minimum = 0
    a1.maximum = 1000
    a1.default = 0
    a1.tag = "snap"
    d.addAxis(a1)
    s1 = SourceDescriptor()
    s1.location = dict(snap=0)
    s1.path = os.path.join(path, 'masters','geometryMaster1.ufo')
    d.addSource(s1)
    s2 = SourceDescriptor()
    s2.location = dict(snap=(10,11))
    s2.path = os.path.join(path, 'masters','geometryMaster2.ufo')
    d.addSource(s2)
    d.write(tp)
    dc = DesignSpaceChecker(tp)
    dc.checkEverything()
    assert (2,10) in dc.problems        # source location is anisotropic

    # ok axis, ok sources
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "viable.designspace")
    a1 = AxisDescriptor()
    a1.name = "snap"
    a1.minimum = 0
    a1.maximum = 1000
    a1.default = 0
    a1.tag = "snap"
    d.addAxis(a1)
    s1 = SourceDescriptor()
    #s1.name = "master.1"
    s1.location = dict(snap=0)
    s1.path = os.path.join(path, 'masters','geometryMaster1.ufo')
    d.addSource(s1)
    #s2.name = "master.2"
    s2 = SourceDescriptor()
    s2.location = dict(snap=1000)
    s2.path = os.path.join(path, 'masters','geometryMaster2.ufo')
    d.addSource(s2)
    s3 = SourceDescriptor()
    s3.location = dict(snap=500)
    s3.path = os.path.join(path, 'masters','geometryMaster3.ufo')   # bad kerning
    d.addSource(s3)
    jd = InstanceDescriptor()
    jd.familyName = "TestFamily"
    jd.styleName = "TestStyle"
    jd.location = dict(snap=500)
    jd.path = os.path.join(path, 'instances','generatedInstance.ufo')
    d.addInstance(jd)
    d.write(tp)
    dc = DesignSpaceChecker(tp)
    dc.checkEverything()
    pprint(dc.problems)
    assert not dc.hasStructuralProblems()   # minimum working designspace, ready for fonts
    assert (4,7) in dc.problems        # default glyph is empty, glyphName
    assert (4,9) in dc.problems        # incompatible constructions for glyph
    assert (5,0) in dc.problems        # kerning: no kerning in source
    assert (5,6) in dc.problems        # no kerning groups in source
    assert (6,4) in dc.problems        # source font unitsPerEm value different from default unitsPerEm

def makeEdit(path, find, replace):
    f = open(path, 'r')
    t = f.read()
    f.close()
    t = t.replace(find, replace)
    f = open(path, 'w')
    f.write(t)
    f.close()
makeTests()