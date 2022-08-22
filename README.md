# NGI KOF Parser

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

This is the NGI Python package for parsing kof files.

References:

NORWEGIAN GEOTECHNICAL SOCIETY
- [NGF - VEILEDNING FOR
SYMBOLER OG DEFINISJONER I GEOTEKNIKK](http://ngf.no/wp-content/uploads/2015/03/2_NGF-ny-melding-2-endelig-utgave-2011-12-04-med-topp-og-bunntekst-Alt-3.pdf)
- [Norkart KOF specification](http://www.anleggsdata.no/wp-content/uploads/2018/04/KOF-BESKRIVELSE-Oppdatert2005.pdf)

Latest releases see [CHANGES.md](CHANGES.md)

# Installation (end user) 

```bash

pip install ngi-kof-parser

```

## Basic usage

### Read a kof file
```python
from ngi_kof_parser import KOFParser

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

```python
from ngi_kof_parser import KOFWriter
from ngi_kof_parser import Location

kof_writer = KOFWriter()

srid = 5110
locations = [Location(name='SMPLOC1', point_easting=112892.81, point_northing=1217083.64, point_z=1.0),
             Location(name='SMPLOC2', point_easting=112893.15, point_northing=1217079.46, point_z=2.0, methods=['TOT']),
             Location(name='SMPLOC3',point_easting=112891.88, point_northing=1217073.01, point_z=0.0, methods=['CPT'])]
 
kof_string = kof_writer.writeKOF(
    project_id='project_id', project_name='cool-name', locations=locations, srid=srid
)

print(kof_string)
# Output:
# 00 KOF Export from NGI Field Manager
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

1. Software dependencies

2. Clone this repository

3. Install

## Software dependencies

Before you start, install:

   - Python 3.9 or higher
   - Poetry
   - black code formatter
   
## Clone this repository

Use git to clone this repository.

## Install

There are several combinations of how to set up a local development environment.

We use Poetry for dependency management. See [Install poetry](https://python-poetry.org/docs/) if needed.

To set up a local development environment on you local machine, make sure you have set up your NGI credentials.
You need to generate Personal Access Token (PAT). Follow
[this guide](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate)
for how to get a PAT via the Azure DevOps GUI. `Packaging (Read)` access is sufficient.

After generating the PAT, run this command:

    poetry config http-basic.ngi-fm build <PAT>

Then, from the project root folder run:

    poetry install



# Build and Test

Run in the project root folder: 

    poetry install
    pytest 

Build the package wheel: 

    poetry build


# Publish

To publish the package to NGI's private Azure Artifacts repository set the following configuration: 

    poetry config repositories.ngi https://pkgs.dev.azure.com/ngi001/277b2f77-691a-4d92-bd89-8e7cac121676/_packaging/fieldmanager/pypi/upload

To publish the package to Azure Artifacts, make sure you have set up your NGI credentials.

You need to generate Personal Access Token (PAT). Follow
[this guide](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate)
for how to get a PAT via the Azure DevOps GUI. `Packaging (Read, write, & manage)` access is sufficient.

If you want to publish your newly built package you need to set your NGI credentials: 

    poetry config pypi-token.ngi <PAT>

    poetry publish -r ngi

# TODOs

- Add tests
- Extend with position transformation from file data srid (input) to project srid (output)
- Extend with position transformation from file srid (input) to new output fields in wgs84 
