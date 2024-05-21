# SNAPWF (SNAP Automated Python Workflow)

## Usage

This workflow can generate PSI and SBAS interferometric time series for full Sentinel-1 scenes by using the available open-source tools ASF-Search and SNAP-ESA, which are integrated into Python-based codes to perform the processing chain from dealing with the raw Sentinel-1 data to generating the time series interferometric stacks. For more details, please read our publication: [here](https://www.sciencedirect.com/science/article/pii/S1364815224001361?via%3Dihub).

## Prerequisites

Ensure you have the following libraries installed:

- `asf_search`
- `NumPy`
- `shapely`
- `matplotlib`
- `geopandas`
- `folium`

## How to Run SNAPWF

Please follow these steps to run the scripts:

1. `00_get_stack.ipynb`
2. `01_get_intf.ipynb`
3. `02_plot_frames.ipynb`
4. `03_download.ipynb`

Here you can:

1. Utilize ASF's Vertex and API Tools to identify available scenes in the targeted study area.
2. Identify the target scene using the path number and frame number.
3. Download metadata: Once you have the name of the scene, download the metadata.
4. Visual and area check:
   - Use the geometry attributes of the SAR images to plot the boundaries and visually check them.
   - Perform an area check to reject images with less than 80% of the area size of the selected original scene, preventing interferogram calculations on incomplete images.
5. Filter stack metadata: Filter the stack metadata by calculating the required perpendicular and temporal baseline information. Reject incomplete scenes.
6. Download data: After filtering, use the ASF-Search data download functionalities to download the Sentinel-1 data from the ASF servers.

## Depending on your choice of applying PSI or SBAS, you can choose one of the following workflows:

5. `04_run_psi.ipynb`
6. `05_run_sbas.ipynb`

## Citation

Please refer to our publication: Zaki, A., Chang, L., Manzella, I., van der Meijde, M., Girgin, S., Tanyas, H., and Fadel, I., 2024. Automated Python workflow for generating Sentinel-1 PSI and SBAS interferometric stacks using SNAP on Geospatial Computing Platform. Environmental Modelling & Software, p.106075.
