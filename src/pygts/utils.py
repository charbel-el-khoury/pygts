"""Utility functions for data loading and processing.

This module provides helper functions for loading and processing species data
from various file formats, particularly for batch operations.
"""

import pandas as pd
from pathlib import Path


def load_species_data(csv_path: str | Path) -> pd.DataFrame:
    """Load and parse species data from a CSV file.
    
    This function reads a CSV file containing species names in the 'TaxonName'
    column and splits them into separate 'Genus' and 'Species' columns for use
    with the data fetching functions.

    Args:
        csv_path (str | Path): Path to the CSV file. Must contain a 'TaxonName'
            column with species names in the format "Genus species".

    Returns:
        pd.DataFrame: DataFrame with three columns:
            - TaxonName (str): Original full species name
            - Genus (str): Extracted genus name
            - Species (str): Extracted species epithet
            
    Example:
        >>> df = load_species_data("data/species_list.csv")
        >>> print(df.head())
           TaxonName              Genus        Species
        0  Abarema cochliocarpos  Abarema      cochliocarpos
        1  Abies alba             Abies        alba
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
        KeyError: If 'TaxonName' column is not found in the CSV.
        IndexError: If species names don't contain at least two words.
    """
    path = Path(csv_path)
    species_df = pd.read_csv(path)[["TaxonName"]]
    species_df["Genus"] = species_df["TaxonName"].apply(lambda x: str(x).split(" ")[0])
    species_df["Species"] = species_df["TaxonName"].apply(
        lambda x: str(x).split(" ")[1]
    )
    return species_df