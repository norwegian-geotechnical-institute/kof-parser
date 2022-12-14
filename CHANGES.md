# Python KOF Parser Package

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


