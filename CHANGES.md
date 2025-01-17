# Python KOF Parser Package

## Version 0.1.2
_2025-01-17_

Add

- Add support for all EPSG SRIDs (that the coordinate-projector package supports).

## Version 0.1.1
_2023-11-09_

Add

- Add error message if the KOF file contains TAB characters (not allowed).

## Version 0.1.0
_2023-10-17_

Change

- Upgrade packages, including Pydantic version "^2.4.2"

## Version 0.0.19
_2023-10-04_

Fix

- Fix a bug in the KOF writer format (output). Now right align the coordinate numbers in the coordinate block (05).

## Version 0.0.18
_2023-08-24_

Change

- Update packages

## Version 0.0.17

_2023-05-16_

Change

- Support Python version 3.11.
- Update packages.


## Version 0.0.16

_2023-04-28_

Change

- Fail to parse a KOF file, now raise an exception containing the offending line number in the problem file. 

## Version 0.0.15

_2023-04-25_

Fix

- A bug that skipped lines beginning with " 05" (space, zero, five) that contained " 01" (space, zero, one), is fixed.

## Version 0.0.14

_2023-03-14_

Update

- Upgrade package coordinate-projector to 0.0.7

## Version 0.0.13

_2023-03-03_

Update

- Upgrade package coordinate-projector to 0.0.6

## Version 0.0.12

_2022-11-02_

Add

- Add missing srid/epsg 3857 and SOSI code 300 for WGS84 Web Mercator / Pseudo-Mercator.

Fix

- Crash in KOF writer if target srid/epsg has no SOSI definition.

## Version 0.0.11

_2022-10-21_

Change

- Upgrade packages.
- Replace the cchardet package with charset-normalizer due to murky licensing.

## Version 0.0.10

_2022-10-21_

Change

- Upgrade packages.

## Version 0.0.9

_2022-10-04_

Fix

- If a location had Z (height) empty, then parser crashed. Now fixed.

## Version 0.0.8

_2022-08-22_

Add

- Refractoring to support most encodings in input files.

## Version 0.0.7

_2022-04-20_

Add

- Transformation of coordinates in output file.
- Add support for swapping easting and northing in the input or output kof file.

## Version 0.0.6

_2022-03-02_

Add

- Use new ngi-projector version 0.0.3.
- Add transformations.
- Support for more methods. Complete list:
  - RO: 2251
  - RW: 2401
  - SA: 2402
  - TP: 2403
  - SS: 2405
  - RP: 2406
  - CPT: 2407
  - RS: 2409
  - SR: 2410
  - SPT: 2411
  - RCD: 2412
  - PZ: 2413
  - PT: 2414
  - SVT: 2415
  - INC: 2417
  - TOT: 2418
- Support parsing of letter tema codes F, VB and GVR.
- KOF Writer for creating KOF files.
- Add coordinate system handling in the admin block (01).

## Version 0.0.5

_2022-02-10_

## Version 0.0.3

_2022-01-31_

- Initial version
