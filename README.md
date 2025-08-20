# KOF Parser

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![security: safety](https://img.shields.io/badge/security-safety-yellow.svg)](https://github.com/pyupio/safety)
[![code style](https://img.shields.io/badge/style-ruff-41B5BE)](https://github.com/astral-sh/ruff)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)


Python package for parsing and generating KOF files.

References:

NORWEGIAN GEOTECHNICAL SOCIETY
- [NGF - VEILEDNING FOR
SYMBOLER OG DEFINISJONER I GEOTEKNIKK](http://ngf.no/wp-content/uploads/2015/03/2_NGF-ny-melding-2-endelig-utgave-2011-12-04-med-topp-og-bunntekst-Alt-3.pdf)
- [Norkart KOF specification](http://www.anleggsdata.no/wp-content/uploads/2018/04/KOF-BESKRIVELSE-Oppdatert2005.pdf)

Latest releases see [CHANGES.md](https://github.com/norwegian-geotechnical-institute/kof-parser/blob/main/CHANGES.md)

# Installation (end user) 

```bash
pip install kof-parser
```

## Basic usage

### Read a kof file

```python
from kof_parser import KOFParser

parser = KOFParser()

# ETRS89/NTM10:
srid = 5110

locations = parser.parse('tests/data/test.kof', result_srid=srid, file_srid=srid)

for location in locations:
    print(location)

# Output:
# name='SMPLOC1' methods=[] point_easting=112892.81 point_northing=1217083.64 point_z=1.0 srid=5110
# name='SMPLOC2' methods=['TOT'] point_easting=112893.15 point_northing=1217079.46 point_z=2.0 srid=5110
# name='SMPLOC3' methods=['CPT'] point_easting=112891.88 point_northing=1217073.01 point_z=0.0 srid=5110
# name='SMPLOC4' methods=['RP'] point_easting=112891.9 point_northing=1217067.54 point_z=0.0 srid=5110
# name='SMPLOC5' methods=['SA'] point_easting=112902.92 point_northing=1217074.73 point_z=0.0 srid=5110
# name='SMPLOC6' methods=['PZ'] point_easting=112901.11 point_northing=1217069.56 point_z=0.0 srid=5110
# name='SMPLOC7' methods=['PZ'] point_easting=1217069.56 point_northing=112901.11 point_z=0.0 srid=5110

```

### Write a kof file

To write a KOF file you need to build up a model of locations and methods.

```python
from kof_parser import KOFWriter
from kof_parser import Location

kof_writer = KOFWriter()

srid = 5110
locations = [Location(name='SMPLOC1', point_easting=112892.81, point_northing=1217083.64, point_z=1.0),
             Location(name='SMPLOC2', point_easting=112893.15, point_northing=1217079.46, point_z=2.0, methods=['TOT']),
             Location(name='SMPLOC3', point_easting=112891.88, point_northing=1217073.01, point_z=0.0, methods=['CPT'])]

kof_string = kof_writer.writeKOF(
    project_id='project_id', project_name='cool-name', locations=locations, srid=srid
)

print(kof_string)
# Output:
# 00 KOF Export from NGI's KOF parser
# 00 Project: project_id. Name: cool-name
# 00 Spatial Reference ID (SRID): 5110
# 00 Export date (UTC): 2022-08-22 13:49:44.394607
# 00 Oppdrag      Dato     Ver K.sys   Komm $21100000000 Observer    
# 01 cool-name    22082022   1     210      $11100000000             
# 05 SMPLOC1             1217083.640  112892.810  1.000                
# 05 SMPLOC2    2418     1217079.460  112893.150  2.000                
# 05 SMPLOC3    2407     1217073.010  112891.880  0.000                
```

# Getting Started developing

## Software dependencies

Before you start, install:

   - Python 3.11 or higher
   - uv (see https://docs.astral.sh/uv/)
   - Ruff formatter
   
## Clone this repository

Use git to clone this repository.

## Install

There are several combinations of how to set up a local development environment.

We use uv for dependency management. See the uv docs if needed.

Then, from the project root folder run:

    uv sync --dev

This will create a virtual environment (by default in .venv) and install all dependencies including dev tools.

# Build and Test

Run tests in the project root folder: 

    uv run pytest

Build the package wheel: 

    uv build

# Contribute

Please start by adding an issue before submitting any pull requests.