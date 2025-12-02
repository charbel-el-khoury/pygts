"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_geo_data():
    """Sample geographic data from API."""
    return [
        {"country": "Brazil", "province": "Bahia", "uncertainty": None},
        {"country": "Brazil", "province": "Ceará", "uncertainty": None},
        {"country": "France", "province": None, "uncertainty": None}
    ]


@pytest.fixture
def sample_species_df():
    """Sample species DataFrame for testing."""
    import pandas as pd
    return pd.DataFrame({
        "Genus": ["Abarema", "Abies", "InvalidGenus"],
        "Species": ["cochliocarpos", "alba", "invalid"]
    })
