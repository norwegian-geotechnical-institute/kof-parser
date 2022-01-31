# NGI KOF Parser

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

```python
from ngi_kof_parser import KOFParser

parser = KOFParser()

# ETRS89/NTM10:
srid = 5110
locations = parser.parse('tests/data/test.kof', srid)

for location in locations:
   print(location)

# Output:
# name='SMPLOC1' point_easting=112892.81 point_northing=1217083.64 point_z=1.0 srid=5110 methods=[]
# name='SMPLOC2' point_easting=112893.15 point_northing=1217079.46 point_z=2.0 srid=5110 methods=['TOT']
# name='SMPLOC3' point_easting=112891.88 point_northing=1217073.01 point_z=0.0 srid=5110 methods=['CPT']
# name='SMPLOC4' point_easting=112891.9 point_northing=1217067.54 point_z=0.0 srid=5110 methods=['RP']
# name='SMPLOC5' point_easting=112902.92 point_northing=1217074.73 point_z=0.0 srid=5110 methods=['SA']
# name='SMPLOC6' point_easting=112901.11 point_northing=1217069.56 point_z=0.0 srid=5110 methods=['PZ']
# name='SMPLOC7' point_easting=1217069.56 point_northing=112901.11 point_z=0.0 srid=5110 methods=['PZ']

```

# Getting Started developing

1. Software dependencies

   - Python 3.9 or higher
   - Poetry
   - black code formatter

2. Clone this repository

3. Install

   `poetry install`



# Build and Test

Run in the project root folder: 

    poetry install
    pytest 

Build the package wheel: 

    poetry build


# Publish

To publish the package to NGI's private Azure Artifacts repository set the following configuration: 

    # poetry config repositories.ngi https://pkgs.dev.azure.com/ngi001/_packaging/ngi001%40Local/pypi/simple/
    # poetry config repositories.ngi https://pkgs.dev.azure.com/ngi001/_packaging/ngi001%40Local/pypi/upload
#    poetry config repositories.ngi https://pkgs.dev.azure.com/ngi001/_packaging/ngi001/pypi/upload
    poetry config repositories.ngi https://pkgs.dev.azure.com/ngi001/_packaging/ngi001%40Local/pypi/upload

To publish the package to Azure Artifacts, make sure you have set up your NGI credentials.

You need to generate Personal Access Token (PAT). Follow
[this guide](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate)
for how to get a PAT via the Azure DevOps GUI. `Packaging (Read, write, & manage)` access is sufficient.

If you want to publish your newly built package you need to set your NGI credentials: 

    poetry config http-basic.ngi build <PAT>
    poetry config pypi-token.ngi <PAT>
    poetry config http-basic.ngi <your user name> <PAT>

    poetry publish -r ngi

# TODOs

- Add tests
- Extend with position transformation from file data srid (input) to project srid (output)
- Extend with position transformation from file srid (input) to new output fields in wgs84 


# Scrap

   poetry config repositories.ngi https://pkgs.dev.azure.com/ngi001/_packaging/ngi001%40Local/pypi/simple/
