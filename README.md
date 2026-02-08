# OutdoorFootprintNetworkPipeline (ONFP)

Source code for creating an outdoor activity footprint network from GNSS trajectories, representing the human footprint (e.g., hiking or running).

<p align="center">
<table style="border:none;border:0;width:60%"><tr>
  <td align="center" style="width:30%">
  	<img width="200px" src="https://github.com/IntForOut/HikersFootprint/blob/main/img/input.png" />
  	<label>Raw</label>
  </td>
  <td style="padding:16px;">
  	<img width="200px" src="https://github.com/IntForOut/HikersFootprint/blob/main/img/output.png" />
  	<label>Mobility Network</label>
  </td>
</tr></table>
</p>




## Prerequisites

You need to install the following libraries:

- Tracklib
- Netmatcher
- Plugin QGis "SciPy Filters"


## How to Run the Code


### Input

A GNSS trace dataset in CSV format is required.


### Execution

Run this source code in the QGIS Python console to display the created layers.

Execute MainWorkflow.py to start the creation scripts.



