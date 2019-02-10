# Proposal for error reporting for designspaces

If we have different libraries looking at interpolating systems such as designspaces, it makes sense to have a shared vocabulary for the types of problems that can occur. This data generally is very diverse, font info, kerning info, all the glyph geometry and so on and it comes from different sources. Often edited by different people as well. So improved reporting of problems can help in improving interoperation between tools that edit, validate and generate.

## Terms
This list is not intended to be normative, just an explanation of what the terms mean in this document. 

* **Mutator**: an **object** that can interpolate. It has all the relevant source data and designspace geometry for one specific thing, for instance a glyph. The processor can generate instances for arbitrary locations in the designspace. This can be a `mutatorMath` object, but also a `fonttools varlib.model` object. I'm sure there will be more.
* **Designspace**: the **document** that contains data for the axes, the location of the sources, the location of the instances. The designspace can also contain data about the rules / feature variations.
* **Breaking errors**: the class of errors that prevents any calculations from happening.
* **Non-breaking errors**: the class of errors that calculate well, but are still wrong. For instance: the location of starting point on a contour. Or the order of contours in a glyph, when each contour has the same number of points.
* **Bootstrap errors**: Not enough data, or the wrong data. It is impossible to create an mutator.

## Conclusions
1. can't build processor with available masters
2. can't generate instance data with processor
3. can't generate variable font from designspace
4. can't generate font from UFO
4. instance contains failing glyphs
5. instance is missing certain data (info, kerning, glyphs)

# Classes of problems
  * `0. file`
  * `1. designspace geometry`
  * `2. sources`
  * `3. instances`
  * `4. glyphs`
  * `5. kerning`
  * `6. font info`
  * `7. rules`

## 0 file

  * `0.0	file corrupt`

## 1 designspace geometry

  * `1.0	no axes defined`
  * `1.1	axis missing`
  * `1.2	axis maximum missing`
  * `1.3	axis minimum missing`
  * `1.4	axis default missing`
  * `1.5	axis name missing`
  * `1.6	axis tag missing`
  * `1.7	axis tag mismatch`
  * `1.8	mapping table has overlaps`
  * `1.9	minimum and maximum value are the same`
  * `1.10	default not between minimum and maximum`

## 2 sources

  * `2.0	no sources defined`
  * `2.1	source UFO missing`
  * `2.2	source UFO format too old`
  * `2.3	source layer missing`
  * `2.4	source location missing`
  * `2.5	source location has value for undefined axis`
  * `2.6	source location has out of bounds value`
  * `2.7	no source on default location`
  * `2.8	multiple sources on default location`
  * `2.9	multiple sources on location`
  * `2.10	source location is anisotropic`

## 3 instances

  * `3.1	instance location missing`
  * `3.2	instance location has value for undefined axis`
  * `3.3	instance location has out of bounds value`
  * `3.4	multiple instances on location`
  * `3.5	instance location is anisotropic`
  * `3.6	missing family name`
  * `3.7	missing style name`
  * `3.8	missing output path`
  * `3.9	duplicate instances`

## 4 glyphs

  * `4.0	different number of contours in glyph`
  * `4.1	different number of components in glyph`
  * `4.2	different number of anchors in glyph`
  * `4.3	different number of on-curve points on contour`
  * `4.4	different number of off-curve points on contour`
  * `4.5	curve has wrong type`
  * `4.6	non-default glyph is empty`
  * `4.7	default glyph is empty`
  * `4.8	contour has wrong direction`

## 5 kerning

  * `5.0	no kerning in source`
  * `5.1	no kerning in default`
  * `5.2	kerning group members do not match`
  * `5.3	kerning group missing`
  * `5.4	kerning pair missing`

## 6 font info

  * `6.0	source font info missing value for units per em`
  * `6.1	source font info missing value for ascender`
  * `6.2	source font info missing value for descender`
  * `6.3	source font info missing value for xheight`

## 7 rules

  * `7.0	source glyph missing`
  * `7.1	destination glyph missing`
  * `7.2	source and destination glyphs the same`
  * `7.3	no substition glyphs defined`
  * `7.4	no conditionset defined`
  * `7.5	condition values on unknown axis`
  * `7.6	condition values out of axis bounds`
  * `7.7	condition values are the same`
  * `7.8	duplicate conditions`
