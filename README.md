# Proposal for error reporting for designspaces

If we have different libraries looking at interpolating systems such as designspaces, it makes sense to have a shared vocabulary for the types of problems that can occur. This data generally is very diverse, font info, kerning info, all the glyph geometry and so on and it comes from different sources. Often edited by different people as well. So improved reporting of problems can help in improving interoperation between tools that edit, validate and generate.

## Terms
This list is not intended to be normative, just an explanation of what the terms mean in this document. 

* **Mutator**: an **object** that can interpolate. It has all the relevant source data and designspace geometry for one specific thing, for instance a glyph. The processor can generate instances for arbitrary locations in the designspace. This can be a `mutatorMath` object, but also a `fonttools varlib.model` object. I'm sure there will be more.
* **Designspace**: the **document** that contains data for the axes, the location of the sources, the location of the instances. The designspace can also contain data about the rules / feature variations.
* **Breaking errors**: the class of errors that prevents any calculations from happening.
* **Non-breaking errors**: the class of errors that calculate well, but are still wrong. For instance: the location of starting point on a contour. Or the order of contours in a glyph, when each contour has the same number of points.
* **Bootstrap errors**: Not enough data, or the wrong data. It is impossible to create an mutator.

## Classes of problems
1. can't build processor with available masters
2. can't generate instance data with processor
3. can't generate variable font from designspace
4. can't generate font from UFO
4. instance contains failing glyphs
5. instance is missing certain data (info, kerning, glyphs)

## 1. Designspace geometry
1. no axes defined in document
	* (for older designspaces)
	* no axis order defined
3. location out of bounds
3. mapping table has overlaps, switchbacks
4. tag misnamed / missing
5. axis name missing

## 2. Masters
1. master not found
2. layer not found in UFO
3. no master on default location
	3.1. in mutatormath systems: no flag found that indicates the default.
4. no master data in foreground layer
5. two or more masters on same location
6. anisotropic location
	* Allowed in mutatormath systems, not allowed in varlib systems.
7. different UFO font source versions (is this really a problem?)

## 3. Instances
1. no valid location
2. missing names

## 4. Glyph objects
1. different number of contours
2. different number of components
3. different number of anchors
4. different number of on-curve points on a contour
5. different number of off-curve points on a contour
6. wrong curve type
7. non-default glyph empty when default is not
8. default glyph empty when non-default is not

## 5. Kerning
1. kerning is missing in one of the masters
	* in neutral / one of the other masters
	* there may be differences between mutatormath and varlib systems.
3. specific exceptions are missing
4. specific pairs are wrong
	* through extrapolation

## 6. Font.info
1. Missing values
	* ascender, descender, unitsPerEm

## 6. Rules
1. source or destination glyph missing
2. condition values out of bounds
3. condition values empty
4. condition values the same

