"""Tree Species Geographic Data Fetcher and Visualizer.

A Python package for fetching and visualizing geographic distribution data
for tree species from the BGCI (Botanic Gardens Conservation International)
Global Tree Search database.

Basic Usage:
    >>> from pygts import request_data, plot_species_distribution
    >>> 
    >>> # Fetch species data
    >>> data = request_data("Abarema", "cochliocarpos")
    >>> print(f"Found in {len(data)} locations")
    >>> 
    >>> # Create visualization
    >>> plot_species_distribution("Abies", "alba", save_path="map.png")

CLI Usage:
    $ pygts check Abarema cochliocarpos
    $ pygts fetch Abies alba --json
    $ pygts visualize Abarema cochliocarpos -o map.png

Key Features:
    - Robust error handling for API requests
    - Parallel batch processing for multiple species
    - High-quality map visualizations
    - Both Python API and CLI interface

For more information:
    - BGCI Global Tree Search: https://www.bgci.org/resources/global-tree-search/
    - GitHub: https://github.com/charbel-el-khoury/pygts
"""

from .data_fetcher import fetch_species_data_parallel, request_data, species_exists
from .visualizer import plot_species_distribution

__version__ = "0.1.0"

__all__ = [
    "request_data",
    "species_exists",
    "fetch_species_data_parallel",
    "plot_species_distribution",
]
