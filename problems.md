# problem categories
  * `0. file`
  * `1. designspace geometry`
  * `2. sources`
  * `3. instances`
  * `4. glyphs`
  * `5. kerning`
  * `6. font info`
  * `7. rules`

## 0. file

  * `0.0	file corrupt`

## 1. designspace geometry

  * `1.0	no axes defined`
  * `1.1	axis missing`
  * `1.2	axis maximum missing`
  * `1.3	axis minimum missing`
  * `1.4	axis default missing`
  * `1.5	axis name missing`
  * `1.6	axis tag missing`
  * `1.7	axis tag mismatch`
  * `1.9	minimum and maximum value are the same`
  * `1.10	default not between minimum and maximum`
  * `1.11	mapping table has overlapping input values`
  * `1.12	mapping table has overlapping output values`

## 2. sources

  * `2.0	no sources defined`
  * `2.1	source UFO missing`
  * `2.2	source UFO format too old, recommend update.`
  * `2.3	source layer missing`
  * `2.4	source location missing`
  * `2.5	source location has value for undefined axis`
  * `2.6	source location has out of bounds value`
  * `2.7	no source on default location`
  * `2.8	multiple sources on default location`
  * `2.9	multiple sources on location`
  * `2.10	source location is anisotropic`
  * `2.11	axis without on-axis sources`

## 3. instances

  * `3.1	instance location missing`
  * `3.2	instance location has value for undefined axis`
  * `3.3	instance location has out of bounds value`
  * `3.4	multiple instances on location`
  * `3.5	instance location requires extrapolation`
  * `3.6	missing family name`
  * `3.7	missing style name`
  * `3.8	missing output path`
  * `3.9	instance location is anisotropic`
  * `3.10	no instances defined`

## 4. glyphs

  * `4.0	different number of contours in glyph`
  * `4.1	different components in glyph`
  * `4.2	different anchors in glyph`
  * `4.3	different number of on-curve points on contour`
  * `4.4	different number of off-curve points on contour`
  * `4.5	curve has wrong type`
  * `4.6	non-default glyph is empty`
  * `4.7	default glyph is empty`
  * `4.8	contour has wrong direction`
  * `4.9	incompatible constructions for glyph`

## 5. kerning

  * `5.0	no kerning in source`
  * `5.1	no kerning in default`
  * `5.2	kerning group members do not match`
  * `5.3	kerning group missing in default`
  * `5.4	kerning pair missing`
  * `5.5	no kerning groups in default`
  * `5.6	no kerning groups in source`

## 6. font info

  * `6.0	default font info missing value for units per em`
  * `6.1	default font info missing value for ascender`
  * `6.2	default font info missing value for descender`
  * `6.3	default font info missing value for xheight`
  * `6.4	source font unitsPerEm value different from default unitsPerEm`

## 7. rules

  * `7.0	source glyph missing`
  * `7.1	destination glyph missing`
  * `7.2	source and destination glyphs the same`
  * `7.3	no substition glyphs defined`
  * `7.4	no conditionset defined`
  * `7.5	condition values on unknown axis`
  * `7.6	condition values out of axis bounds`
  * `7.7	condition values are the same`
  * `7.8	duplicate conditions`
  * `7.9	rule without a name`
  * `7.10	condition with missing minimum`
  * `7.11	condition with missing maximum`