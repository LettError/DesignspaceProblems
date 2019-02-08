
"""

Run some tests on the designspace.
Some sort of validator

"""

class DesignSpaceError(object):
    _categories = {
        1: "designspace geometry",
        2: "sources",
        3: "instances",
        4: "glyphs",
        5: "kerning",
        6: "font info",
        7: "rules",
        }
    _errors = {
        # 1 designspace geometry
        (1,0): "no axes defined",
        (1,1): "axis missing",
        (1,2): "axis maximum missing",
        (1,3): "axis minimum missing",
        (1,4): "axis default missing",
        (1,5): "axis name missing",
        (1,6): "axis tag missing",
        (1,7): "axis tag mismatch",

        (1,8): "mapping table has overlaps",

        # 2 sources
        (2,0): "no sources defined",
        (2,1): "source UFO missing",
        (2,2): "source UFO format too old",
        (2,3): "source layer missing",
        (2,4): "source location missing",
        (2,5): "source location has value for undefined axis",
        (2,6): "source location has out of bounds value",
        (2,7): "no source on default location",
        (2,8): "multiple sources on default location",
        (2,9): "multiple sources on location",
        (2,10): "source location is anisotropic",
        
        # 3 instances
        (3,1): 'instance location missing',
        (3,2): "instance location has value for undefined axis",
        (3,3): "instance location has out of bounds value",
        (3,4): "multiple sources on default location",
        (3,5): "instance location requires extrapolation",
        (3,5): "instance location is anisotropic",
        (3,6): "missing family name",
        (3,7): "missing style name",
        (3,8): "missing output path",
        (3,9): "duplicate instances",
        
        # 4 glyphs
        (4,0): 'different number of contours in glyph',
        (4,1): 'different number of components in glyph',
        (4,2): 'different number of anchors in glyph',
        (4,3): 'different number of on-curve points on contour',
        (4,4): 'different number of off-curve points on contour',
        (4,5): 'curve has wrong type',
        (4,6): 'non-default glyph is empty',
        (4,7): 'default glyph is empty',
        (4,8): 'contour has wrong direction',

        # 5 kerning
        (5,0): 'no kerning in source',
        (5,1): 'no kerning in default',
        (5,2): 'kerning group members do not match',
        (5,3): 'kerning group missing',
        (5,4): 'kerning pair missing',

        # 6 font info
        (6,0): 'source font info missing value for units per em',
        (6,1): 'source font info missing value for ascender',
        (6,2): 'source font info missing value for descender',
        (6,3): 'source font info missing value for xheight',

        # 7 rules
        (7,0): 'source glyph missing',
        (7,1): 'destination glyph missing',
        (7,2): 'source and destination glyphs the same',
        (7,3): 'no substition glyphs defined',
        (7,4): 'no conditionset defined',
        (7,5): 'condition values on unknown axis',
        (7,6): 'condition values out of axis bounds',
        (7,7): 'condition values are the same',
        (7,8): 'duplicate conditions',
        }
        
    def __init__(self, category=None, error=None):
        self.category = category
        self.error = error
    
    def __repr__(self):
        t = []
        key = (self.category, self.error)
        print(key)
        if self.category in self._categories:
            t.append(self._categories.get(self.category))
        if key in self._errors:
            t.append(self._errors.get(key))
        return "Designspace Error: " + ": ".join(t)
            
def allErrors():
    e = DesignSpaceError()
    return e._errors
    
def makeErrorDocumentationTable():
    # Print the categories and the errors in a md format for the docs page. 
    t = ["# Classes of problems"]
    e = DesignSpaceError()
    cats = list(e._categories.keys())
    cats.sort()
    for cat in cats:
        t.append("  * %d. %s" % (cat, e._categories[cat]))
    errs = list(e._errors.keys())
    errs.sort()
    lastCat = None
    for cat, err in errs:
        if cat != lastCat:
            t.append("\n## %d %s\n" % (cat, e._categories[cat]))
            lastCat = cat
        t.append("  * `%d.%d\t%s`" % (cat, err, e._errors[(cat,err)]))
    print("\n".join(t))
    
makeErrorDocumentationTable()

def makeFunctions():
    # make descriptive function names
    for key, desc in allErrors().items():
        new = []
        for i, p in enumerate(desc.split(" ")):
            if i == 0:
                new.append(p)
            else:
                new.append(p[0].upper()+ p[1:])
        new.append("Error")
        print("def %s():\n    # %s, %s\n    return DesignSpaceError(%d,%d)\n" % (''.join(new), desc, key, key[0], key[1]))
        
makeFunctions()