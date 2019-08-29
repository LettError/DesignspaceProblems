# make some tests

import os, glob
from pprint import pprint
import designspaceProblems.problems
from importlib import reload
reload(designspaceProblems.problems)
from designspaceProblems.problems import DesignSpaceProblem, allProblems
import designspaceProblems
reload(designspaceProblems)
from designspaceProblems import DesignSpaceChecker
import ufoProcessor
from ufoProcessor import DesignSpaceProcessor, getUFOVersion, getLayer, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor
from fontParts.fontshell import RFont

testedProblems = {}
def showProblems(dc):
    global testedProblems
    for pr in dc.problems:
        key = (pr.category,pr.problem)
        if not key in testedProblems:
            testedProblems[key] = 0
        testedProblems[key] += 1

def showUntested():
    global testedProblems
    # these problems can't be tested because UFOprocessor already ignores these faults
    untestable = [(1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (1,7),
        (2, 4), (2,5), (3, 2),
        (6, 0), (6, 1), (6, 2), (6, 3), 
        (4, 5),
    ]
    print("\n\nTested problems")
    app = allProblems()
    for ap in list(app.keys()):
        if ap in testedProblems:
            print("✅", ap, app.get(ap))
        elif ap in untestable:
            print("❔", ap, app.get(ap))
        else:
            print("❌", ap, app.get(ap))

def makeTests():
    path = os.getcwd()
    errs = designspaceProblems.problems.allProblems()

    # empty designspace
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "empty.designspace")
    d.write(tp)
    dc = DesignSpaceChecker(tp)
    dc.checkEverything()
    showProblems(dc)
    assert (1,0) in dc.problems    # no axes defined
    assert (2,0) in dc.problems    # no sources defined
    assert (2,7) in dc.problems    # no source on default location
    assert (3,10) in dc.problems    # no instances defined

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
    showProblems(dc)
    assert (0,0) in dc.problems    # no axes defined
    assert (1,0) in dc.problems    # no axes defined
    assert (2,0) in dc.problems    # no sources defined
    assert (2,7) in dc.problems    # no source on default location
    assert (3,10) in dc.problems    # no instances defined

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
    showProblems(dc)
    assert (1,9) in dc.problems    # minimum and maximum value are the same
    assert (1,10) in dc.problems   # minimum and maximum value are the same
    assert (2,0) in dc.problems    # no sources defined
    assert (2,7) in dc.problems    # no source on default location
    assert (3,10) in dc.problems    # no instances defined

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
    showProblems(dc)
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
    showProblems(dc)
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
    showProblems(dc)
    print(dc.problems)
    assert (2,10) in dc.problems        # source location is anisotropic

    # ok space, no kerning in default
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "no-kerning-in-default.designspace")
    a1 = AxisDescriptor()
    a1.name = "snap"
    a1.minimum = 0
    a1.maximum = 1000
    a1.default = 0
    a1.tag = "snap"
    d.addAxis(a1)
    s1 = SourceDescriptor()
    s1.location = dict(snap=0)
    s1.path = os.path.join(path, 'masters','geometryMaster1_no_kerning.ufo')
    d.addSource(s1)
    s2 = SourceDescriptor()
    s2.location = dict(snap=1000)
    s2.path = os.path.join(path, 'masters','geometryMaster2.ufo')
    d.addSource(s2)
    d.write(tp)
    dc = DesignSpaceChecker(tp)
    dc.checkEverything()
    showProblems(dc)
    assert (5,1) in dc.problems    # ok axis, source without location
    
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
    showProblems(dc)
    assert (2,10) in dc.problems        # source location is anisotropic

    # ok space, missing UFO
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "source-ufo-missing.designspace")
    a1 = AxisDescriptor()
    a1.name = "snap"
    a1.minimum = 0
    a1.maximum = 1000
    a1.default = 0
    a1.tag = "snap"
    d.addAxis(a1)

    a2 = AxisDescriptor()
    a2.name = "pop"
    a2.minimum = 0
    a2.maximum = 1000
    a2.default = 0
    a2.tag = "pop_"
    d.addAxis(a1)

    s1 = SourceDescriptor()
    s1.location = dict(snap=0)
    s1.path = os.path.join(path, 'masters','geometryMaster1.ufo')
    d.addSource(s1)
    s2 = SourceDescriptor()
    s2.location = dict(snap=500)
    s2.path = os.path.join(path, 'masters','geometryMaster2.ufo')
    s2.layerName = "missing_layer"
    d.addSource(s2)
    s3 = SourceDescriptor()
    s3.location = dict(snap=1000)
    s3.path = os.path.join(path, 'masters','geometryMaster_missing.ufo')
    d.addSource(s3)
    d.write(tp)
    dc = DesignSpaceChecker(tp)
    dc.checkEverything()
    showProblems(dc)
    assert (2,1) in dc.problems        # source location is anisotropic
    assert (2,3) in dc.problems        # source layer missing

    # multiple ssources in same location
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "multiple_sources_on_same_location.designspace")
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
    for i in range(3):
        s2 = SourceDescriptor()
        s2.location = dict(snap=1500)
        s2.path = os.path.join(path, 'masters','geometryMaster2.ufo')
        d.addSource(s2)
    d.write(tp)
    dc = DesignSpaceChecker(d)
    dc.checkEverything()
    showProblems(dc)

    # instance without location
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "instance_without_location.designspace")
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
    jd = InstanceDescriptor()
    jd.familyName = None
    jd.styleName = None
    jd.location = None
    jd.path = None
    d.addInstance(jd)

    for i in range(3):
        jd = InstanceDescriptor()
        jd.familyName = "Duped"
        jd.styleName = "Duped"
        jd.location = dict(snap=666)
        jd.path = "some/path.ufo"
        d.addInstance(jd)

    d.write(tp)
    dc = DesignSpaceChecker(d)
    dc.checkEverything()
    showProblems(dc)
    assert (3,1) in dc.problems        # instance location missing
    assert (3,4) in dc.problems        # multiple instances on location*

    # mapping tests
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "axismapping.designspace")
    a1 = AxisDescriptor()
    a1.name = "ok_axis"
    a1.minimum = 200
    a1.maximum = 800
    a1.default = 200
    a1.tag = "ax01"
    a1.map = [(200,0), (500, 500), (800, 1000)] # map is ok
    d.addAxis(a1)

    a2 = AxisDescriptor()
    a2.name = "input_regression_axis"
    a2.minimum = 200
    a2.maximum = 800
    a2.default = 500
    a2.tag = "ax02"
    a2.map = [(200,100), (190, 150), (800, 200)] # input regresses ok, output ok
    d.addAxis(a2)

    a3 = AxisDescriptor()
    a3.name = "output_regression_axis"
    a3.minimum = 500
    a3.maximum = 800
    a3.default = 600
    a3.tag = "ax03"
    a3.map = [(500,0), (600, 500), (800, 490)] # input progresses ok, output regresses
    d.addAxis(a3)

    s1 = SourceDescriptor()
    #s1.name = "master.1"
    s1.location = dict(ok_axis=a1.default, output_regression_axis=a3.default)
    s1.path = os.path.join(path, 'masters','geometryMaster1.ufo')
    d.addSource(s1)
    #s2.name = "master.2"
    s2 = SourceDescriptor()
    s2.location = dict(ok_axis=a1.default, output_regression_axis=a3.maximum)
    s2.path = os.path.join(path, 'masters','geometryMaster2.ufo')
    d.addSource(s2)
    d.write(tp)
    dc = DesignSpaceChecker(d)
    print('\taxisvalues for mapped', dc.data_getAxisValues(mapped=True))
    print('\taxisvalues for unmapped', dc.data_getAxisValues(mapped=False))

    dc.checkEverything()
    showProblems(dc)
    assert (1,11) in dc.problems
    assert (1,12) in dc.problems
    pprint(dc.problems)

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

    jd = InstanceDescriptor()
    jd.familyName = None
    jd.styleName = None
    jd.location = dict(snap=600)
    jd.path = os.path.join(path, 'instances','generatedInstance2.ufo')
    d.addInstance(jd)

    jd = InstanceDescriptor()
    jd.familyName = "Aa"
    jd.styleName = "Bb"
    jd.location = dict(snap=600)
    jd.path = None
    d.addInstance(jd)

    r1 = RuleDescriptor()
    r1.name = "rule_no_subs"
    cd1 = dict(name='lalala', minimum=100, maximum=200)
    cd2 = dict(name='snap', minimum=10000, maximum=2000)
    cd3 = dict(name='snap', minimum=10000, maximum=None)    # problem 7,10
    cd4 = dict(name='snap', minimum=None, maximum=10000)    # problem 7,11
    r1.conditionSets.append([cd1, cd2, cd3, cd4])
    d.addRule(r1)

    r2 = RuleDescriptor()
    r2.name = "rule_no_conditionset"
    r2.subs.append(('glyphFour', 'glyphFour'))
    d.addRule(r2)
    
    r3 = RuleDescriptor()
    r3.name = "rule_values_the_same"
    cd1 = dict(name='samesees', minimum=200, maximum=200)
    r1.conditionSets.append([cd1, cd1, cd1])
    r3.subs.append(('glyphFour', 'glyphFour'))
    d.addRule(r3)

    # data for 7, 9 rule without a name
    r4 = RuleDescriptor()
    r4.name = None
    cd1 = dict(name='samesees', minimum=200, maximum=200)
    r1.conditionSets.append([cd1, cd1, cd1])
    r4.subs.append(('glyphFour', 'glyphFour'))
    d.addRule(r4)
    
    d.write(tp)
    dc = DesignSpaceChecker(d)
    dc.checkEverything()
    showProblems(dc)
    assert not dc.hasStructuralProblems()   # minimum working designspace, ready for fonts
    assert (3,6) in dc.problems        # missing family name
    assert (3,7) in dc.problems        # missing style name
    assert (4,1) in dc.problems        # components
    assert (4,2) in dc.problems        # default glyph is empty, glyphName
    assert (4,7) in dc.problems        # default glyph is empty, glyphName
    assert (4,9) in dc.problems        # incompatible constructions for glyph
    assert (5,0) in dc.problems        # kerning: no kerning in source
    assert (5,6) in dc.problems        # no kerning groups in source
    assert (6,4) in dc.problems        # source font unitsPerEm value different from default unitsPerEm
    assert (7,2) in dc.problems        # source and destination glyphs the same
    assert (7,3) in dc.problems        # no substition glyphs defined
    assert (7,4) in dc.problems        # no conditionset defined
    assert (7,5) in dc.problems        # condition values on unknown axis
    assert (7,6) in dc.problems        # condition values out of axis bounds

    # badly populated designspace
    # this system does not have on-axis masters
    # but a couple of non-aligned off-axis masters.
    # Varlib will complain
    d = DesignSpaceProcessor()
    tp = os.path.join(path, "badly_populated.designspace")
    a1 = AxisDescriptor()
    a1.name = "weight"
    a1.minimum = 0
    a1.maximum = 1000
    a1.default = 0
    a1.tag = "wght"
    d.addAxis(a1)

    a2.name = "width"
    a2.minimum = -500
    a2.maximum = 500
    a2.default = 0
    a2.tag = "wdth"
    d.addAxis(a2)

    a3.name = "optical"
    a3.minimum = 0
    a3.maximum = 1000
    a3.default = 0
    a3.tag = "opsz"
    d.addAxis(a3)

    # neutral
    s1 = SourceDescriptor()
    s1.location = dict(weight=0, width=0, optical=0)
    s1.path = os.path.join(path, 'masters','geometryMaster1.ufo')
    d.addSource(s1)

    # offaxis master 1
    s2 = SourceDescriptor()
    s2.location = dict(width=-500, weight=1000, optical=0)
    s2.path = os.path.join(path, 'masters','geometryMaster2.ufo')
    d.addSource(s2)

    # offaxis master 2
    s3 = SourceDescriptor()
    s3.location = dict(width=0, weight=1000, optical=1000)
    s3.path = os.path.join(path, 'masters','geometryMaster2.ufo')
    d.addSource(s3)

    # offaxis master 2
    s4 = SourceDescriptor()
    s4.location = dict(width=500, weight=1000, optical=1000)
    s4.path = os.path.join(path, 'masters','geometryMaster2.ufo')
    d.addSource(s4)

    d.write(tp)
    dc = DesignSpaceChecker(d)
    dc.checkEverything()
    
    showProblems(dc)
    
    showUntested()

def makeEdit(path, find, replace):
    f = open(path, 'r')
    t = f.read()
    f.close()
    t = t.replace(find, replace)
    f = open(path, 'w')
    f.write(t)
    f.close()
makeTests()