"""Geographic visualization module for tree species distribution.

This module provides functionality to create world maps showing the geographic
distribution of tree species. It uses GeoPandas and Matplotlib to generate
interactive or saved visualizations based on BGCI Global Tree Search data.

The maps distinguish between:
- Countries where the species is found throughout (darker green)
- Specific provinces/states where the species is found (lighter green)
- Areas where the species is absent (gray)

Example:
    >>> from pygts.visualizer import plot_species_distribution
    >>> plot_species_distribution("Abarema", "cochliocarpos", save_path="map.png")
    
Data Sources:
    - Species data: BGCI Global Tree Search API
    - Base maps: Natural Earth (via naciscdn.org)
"""

from typing import Dict, List

import geopandas as gpd
import matplotlib.pyplot as plt
import requests
from pygts.data_fetcher import request_data



def extract_locations(geo_data: List[Dict]) -> tuple[List[str], List[tuple[str, str]]]:
    """Extract and categorize geographic locations from API response data.
    
    This helper function processes raw BGCI API data and separates locations into
    two categories: countries where the species occurs throughout (no specific
    province data) and specific country-province pairs.

    Args:
        geo_data (List[Dict]): List of location dictionaries from BGCI API,
            each containing 'country' and optionally 'province' keys.

    Returns:
        tuple[List[str], List[tuple[str, str]]]: A tuple containing:
            - countries_only (List[str]): Countries without province-level data,
              indicating the species is found throughout the country.
            - country_province_pairs (List[tuple[str, str]]): List of (country, province)
              tuples for specific provincial occurrences.
              
    Example:
        >>> geo_data = [
        ...     {'country': 'Brazil', 'province': 'Bahia'},
        ...     {'country': 'Brazil', 'province': 'Ceará'},
        ...     {'country': 'France', 'province': None}
        ... ]
        >>> countries, provinces = extract_locations(geo_data)
        >>> print(countries)
        ['France']
        >>> print(provinces)
        [('Brazil', 'Bahia'), ('Brazil', 'Ceará')]
    """
    countries_only = set()
    country_province_pairs = []

    for entry in geo_data:
        country = entry.get("country")
        province = entry.get("province")

        if country:
            if province:
                country_province_pairs.append((country, province))
            else:
                countries_only.add(country)

    return list(countries_only), country_province_pairs


def plot_species_distribution(genus: str, species: str, save_path: str = None):
    """Create a world map visualization of a tree species' geographic distribution.
    
    This function generates a high-quality world map showing where a species is found,
    with different colors indicating country-level vs. province-level occurrences.
    The map includes a legend and automatically fetches base map data from Natural Earth.
    A summary of locations is printed to stdout.

    Args:
        genus (str): The genus name (e.g., "Abarema", "Abies").
        species (str): The species epithet (e.g., "cochliocarpos", "alba").
        save_path (str, optional): File path to save the map (e.g., "map.png", "output.pdf").
            If None, displays the map interactively using matplotlib's default backend.
            Supported formats: PNG, PDF, SVG, JPG.
            
    Returns:
        None: The function displays or saves the plot but does not return a value.
        
    Example:
        >>> # Display interactive map
        >>> plot_species_distribution("Abarema", "cochliocarpos")
        
        >>> # Save to file
        >>> plot_species_distribution("Abies", "alba", save_path="abies_alba.png")
        Map saved to abies_alba.png
        
    Map Legend:
        - Dark green (#2d8659): Countries where species occurs throughout
        - Light green (#5dba87): Specific provinces/states with occurrences
        - Gray: Areas where species is not recorded
        
    Note:
        Requires internet connection to download base map data on first run.
        Base maps are cached by GeoPandas for subsequent use.
        
    Raises:
        Does not raise exceptions. If species not found or data unavailable,
        prints an error message and returns without creating a plot.
    """
    # Fetch data from API
    geo_data = request_data(genus, species)

    if not geo_data:
        print(f"No geographical data found for {genus} {species}")
        return

    # Extract locations
    countries_only, country_province_pairs = extract_locations(geo_data)

    if not countries_only and not country_province_pairs:
        print(f"No location data found for {genus} {species}")
        return

    # Print summary
    print(f"\n{genus} {species} distribution:")
    if countries_only:
        print(f"  Countries (entire): {', '.join(sorted(countries_only))}")
    if country_province_pairs:
        print(f"  Specific provinces/states:")
        for country, province in sorted(country_province_pairs):
            print(f"    - {country}: {province}")

    # Load world map and provinces
    world = gpd.read_file(
        "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    )
    provinces = gpd.read_file(
        "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_1_states_provinces.zip"
    )

    # Mark countries where entire country has the species
    world["species_present"] = world["NAME"].isin(countries_only)

    # Mark specific provinces
    provinces["species_present"] = False
    for country, province in country_province_pairs:
        # Match provinces by both country and province name
        mask = (provinces["admin"] == country) & (provinces["name"] == province)
        provinces.loc[mask, "species_present"] = True

    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))

    # Plot all countries in light gray (base layer)
    world.plot(ax=ax, color="lightgray", edgecolor="black", linewidth=0.5)

    # Plot countries where entire country has species (darker green)
    if world["species_present"].any():
        world[world["species_present"]].plot(
            ax=ax, color="#2d8659", edgecolor="black", linewidth=0.5
        )

    # Plot specific provinces where species is present (lighter green)
    if provinces["species_present"].any():
        provinces[provinces["species_present"]].plot(
            ax=ax, color="#5dba87", edgecolor="black", linewidth=0.3
        )

    # Set title and remove axes
    plt.title(
        f"Geographic Distribution of {genus} {species}", fontsize=16, fontweight="bold"
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_yticks([])

    # Add legend
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="#2d8659", edgecolor="black", label="Entire country"),
        Patch(facecolor="#5dba87", edgecolor="black", label="Specific provinces"),
        Patch(facecolor="lightgray", edgecolor="black", label="Species absent"),
    ]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=10)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Map saved to {save_path}")
    else:
        plt.show()



if __name__ == "__main__":
    # Example usage
    plot_species_distribution("Abarema", "cochliocarpos")
    plot_species_distribution("abies", "alba")