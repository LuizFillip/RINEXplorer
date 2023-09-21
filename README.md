# GNSS (data pipeline)

This repository aims to describe the processing of GNSS data in order to obtain TEC from RINEX files and your projection in the ionosphere. See IBGE and NASA orbit repository

- Read RINEX, orbits (Sp3 and MGEX) and DCB (bias) files
- Compute slant TEC 
- Compute TEC time variation
- Cycle-slips correction 
- Compute ionospheric piercing point
- save receivers coordinates
- Get the best combinations for pseudoranges and phases



