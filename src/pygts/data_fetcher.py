"""Data fetcher module for BGCI Global Tree Search API.

This module provides functions to interact with the Botanic Gardens Conservation
International (BGCI) Global Tree Search API. It includes methods for checking species
existence, fetching geographic distribution data, and performing parallel batch requests.

Example:
    >>> from pygts.data_fetcher import request_data, species_exists
    >>> exists = species_exists("Abarema", "cochliocarpos")
    >>> data = request_data("Abarema", "cochliocarpos")
    >>> print(len(data))  # Number of geographic locations
    11

API Reference:
    BGCI Global Tree Search: https://www.bgci.org/resources/global-tree-search/
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from tqdm import tqdm


def species_exists(genus: str, species: str) -> bool:
    """Check if a species exists in the BGCI database without fetching full data.
    
    This function performs a lightweight validation by checking if the species
    has any results in the BGCI database. It's useful for validating user input
    or filtering species lists before expensive operations.
    
    Note:
        This still makes an API call. For most use cases, prefer request_data()
        which returns None for non-existent species and provides the actual data
        in a single call.
    
    Args:
        genus (str): The genus name (e.g., "Abarema", "Abies").
        species (str): The species epithet (e.g., "cochliocarpos", "alba").
        
    Returns:
        bool: True if the species exists in the database, False otherwise.
        
    Example:
        >>> species_exists("Abarema", "cochliocarpos")
        True
        >>> species_exists("InvalidGenus", "invalid_species")
        False
        
    Raises:
        Does not raise exceptions. Network errors return False.
    """
    try:
        url = f"https://data.bgci.org/treesearch/genus/{genus}/species/{species}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        response_dict = response.json()
        results = response_dict.get("results", [])
        
        return bool(results and isinstance(results, list) and len(results) > 0)
    except Exception:
        return False


def request_data(genus: str, species: str) -> list | None:
    """Request geographic distribution data from the BGCI Global Tree Search API.
    
    This is the primary function for fetching species data. It retrieves detailed
    geographic information including countries and provinces where the species is found.
    The function includes robust error handling and will gracefully return None for
    network errors, invalid species, or API issues.
    
    Args:
        genus (str): The genus name (e.g., "Abarema", "Abies").
        species (str): The species epithet (e.g., "cochliocarpos", "alba").
        
    Returns:
        list[dict] | None: List of geographic location dictionaries, each containing:
            - country (str): Country name
            - province (str | None): Province/state name if available
            - uncertainty (str | None): Data uncertainty indicator
        Returns None if species not found or request fails.
        
    Example:
        >>> data = request_data("Abarema", "cochliocarpos")
        >>> if data:
        ...     print(f"Found in {len(data)} locations")
        ...     print(f"First location: {data[0]['country']}")
        Found in 11 locations
        First location: Brazil
        
    Raises:
        Does not raise exceptions. All errors are handled internally and logged
        to stdout. Network/API errors return None.
    """
    try:
        url = f"https://data.bgci.org/treesearch/genus/{genus}/species/{species}"
        response = requests.get(url, timeout=10)
        
        # Check for HTTP errors
        response.raise_for_status()
        
        response_dict = response.json()
        
        # Safely navigate the response structure
        results = response_dict.get("results", [])
        if not results or not isinstance(results, list):
            return None
            
        first_result = results[0]
        if not isinstance(first_result, dict):
            return None
            
        countries_dicts = first_result.get("TSGeolinks", [])
        return countries_dicts if countries_dicts else None
        
    except requests.exceptions.RequestException as e:
        # Handle network errors, timeouts, etc.
        print(f"Request error for {genus} {species}: {e}")
        return None
    except (KeyError, IndexError, ValueError, TypeError) as e:
        # Handle JSON parsing or structure errors
        print(f"Data parsing error for {genus} {species}: {e}")
        return None
    except Exception as e:
        # Catch any unexpected errors
        print(f"Unexpected error for {genus} {species}: {e}")
        return None


def fetch_species_data_parallel(
    species_df: pd.DataFrame, max_workers: int = 10
) -> list:
    """Fetch geographic data for multiple species in parallel.
    
    This function enables efficient batch processing of species data by making
    concurrent API requests. It maintains the order of results to match the input
    DataFrame and provides progress feedback via tqdm. Ideal for processing large
    species lists from CSV files or databases.

    Args:
        species_df (pd.DataFrame): DataFrame containing at minimum:
            - 'Genus' (str): Genus names
            - 'Species' (str): Species epithets
        max_workers (int, optional): Maximum concurrent threads. Default is 10.
            Increase for faster processing (if API allows) or decrease to be
            more conservative with API load.

    Returns:
        list: Ordered list of results matching input DataFrame rows. Each element:
            - list[dict]: Geographic data if successful
            - None: If species not found or request failed
            - dict with 'error' key: If unexpected exception occurred
            
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Genus': ['Abarema', 'Abies'],
        ...     'Species': ['cochliocarpos', 'alba']
        ... })
        >>> results = fetch_species_data_parallel(df, max_workers=5)
        Fetching species data: 100%|██████| 2/2 [00:01<00:00,  1.5it/s]
        Completed: 2 successful, 0 failed/no data
        >>> df['geo_data'] = results
        
    Note:
        Progress bar and summary statistics are printed to stdout.
    """
    results = [None] * len(species_df)
    failed_count = 0
    success_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(request_data, row["Genus"], row["Species"]): idx
            for idx, row in species_df.iterrows()
        }

        # Process completed tasks with progress bar
        for future in tqdm(
            as_completed(future_to_index),
            total=len(species_df),
            desc="Fetching species data",
        ):
            idx = future_to_index[future]
            try:
                result = future.result()
                results[idx] = result
                if result is None:
                    failed_count += 1
                else:
                    success_count += 1
            except Exception as e:
                # This should rarely happen now since request_data handles its own errors
                results[idx] = {"error": str(e)}
                failed_count += 1

    print(f"\nCompleted: {success_count} successful, {failed_count} failed/no data")
    return results


if __name__ == "__main__":
    # Example usage - test with both valid and invalid species
    print("Testing species_exists():")
    print(f"  Abarema cochliocarpos exists: {species_exists('Abarema', 'cochliocarpos')}")
    print(f"  Abarema invalid_sp exists: {species_exists('Abarema', 'invalid_sp')}\n")
    
    print("Testing request_data() with invalid species name:")
    data = request_data("Abarema", "cochliopos")
    print(f"Result: {data}\n")
    
    print("Testing request_data() with valid species name:")
    data = request_data("Abarema", "cochliocarpos")
    print(f"Result: {data[:2] if data else None}...\n")  # Show first 2 entries
    
    # Test parallel fetching with mix of valid and invalid species
    print("Testing parallel fetching:")
    test_df = pd.DataFrame({
        "Genus": ["Abarema", "Abarema", "InvalidGenus", "Abies"],
        "Species": ["cochliocarpos", "invalid_sp", "invalid_sp", "alba"]
    })
    results = fetch_species_data_parallel(test_df, max_workers=2)
    for idx, row in test_df.iterrows():
        result = results[idx]
        status = "✓ Success" if result and isinstance(result, list) else "✗ No data"
        print(f"  {row['Genus']} {row['Species']}: {status}")