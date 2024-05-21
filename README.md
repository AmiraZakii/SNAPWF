# SNAPWF (SNAP Automated Python Workflow)
## Usage
This workflow can generate PSI and SBAS interferometric time series for full Sentinel-1 scenes by using the available open-source tools ASF-Search and SNAP-ESA, which are integrated into Python-based codes to perform the processing chain from dealing with the raw Sentinel-1 data until generating the time series interferometric stacks.
for more details, please read our publication https://www.sciencedirect.com/science/article/pii/S1364815224001361?via%3Dihub
## Prerequisites
Before running the code, ensure you have the following libraries installed:
asf_search
NumPy
shapely
matplotlib
geopandas
folium
## How to Run SNAPWF
Please follow these steps to run the scripts:
1. `00_get_stack.ipynb`
2. `01_get_intf.ipynb`
3. `02_plot_frames.ipynb`
4. `03_download.ipynb`
Here you can:
1. Utilize ASF's Vertex and API Tools: Identify available scenes in the targeted study area.
2. Identify Target Scene: Use the path number and frame number.
3. Download Metadata: Once you have the name of the scene, download the metadata.
4. Visual and Area Check:
5. Use the geometry attributes of the SAR images to plot the boundaries and visually check them.
6. Perform an area check to reject images with less than 80% of the area size of the selected original scene, preventing interferogram calculations on incomplete images.
7. Filter Stack Metadata: Filter the stack metadata by calculating the required perpendicular and temporal baseline information. Reject incomplete scenes.
8. Download Data: After filtering, use the ASF-Search data download functionalities to download the Sentinel-1 data from the ASF servers.
## Then, depending on your choice for applying PSI or SBAS, you can choose one of the following workflow
5. 04_run_psi.ipynb
6. 05_run_sbas.ipynb
## Citation
please refer to our publication Zaki, A., Chang, L., Manzella, I., van der Meijde, M., Girgin, S., Tanyas, H. and Fadel, I., 2024. Automated Python workflow for generating Sentinel-1 PSI and SBAS interferometric stacks using SNAP on Geospatial Computing Platform. Environmental Modelling & Software, p.106075.

