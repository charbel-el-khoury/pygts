"""Tests for utils module."""

import pytest
import pandas as pd
from pathlib import Path
from pygts.utils import load_species_data
import tempfile
import os


class TestLoadSpeciesData:
    """Tests for load_species_data function."""
    
    def test_loads_csv_correctly(self):
        """Test that CSV is loaded and parsed correctly."""
        # Create temporary CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("TaxonName\n")
            f.write("Abarema cochliocarpos\n")
            f.write("Abies alba\n")
            temp_path = f.name
        
        try:
            df = load_species_data(temp_path)
            
            assert len(df) == 2
            assert list(df.columns) == ["TaxonName", "Genus", "Species"]
            assert df.iloc[0]["Genus"] == "Abarema"
            assert df.iloc[0]["Species"] == "cochliocarpos"
            assert df.iloc[1]["Genus"] == "Abies"
            assert df.iloc[1]["Species"] == "alba"
        finally:
            os.unlink(temp_path)
    
    def test_accepts_path_object(self):
        """Test that function accepts Path object."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("TaxonName\n")
            f.write("Abarema cochliocarpos\n")
            temp_path = f.name
        
        try:
            df = load_species_data(Path(temp_path))
            assert len(df) == 1
        finally:
            os.unlink(temp_path)
    
    def test_missing_file_raises_error(self):
        """Test that missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_species_data("nonexistent_file.csv")
    
    def test_missing_taxon_column_raises_error(self):
        """Test that missing TaxonName column raises KeyError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("WrongColumn\n")
            f.write("Abarema cochliocarpos\n")
            temp_path = f.name
        
        try:
            with pytest.raises(KeyError):
                load_species_data(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_handles_multiword_species_names(self):
        """Test that only first two words are used."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("TaxonName\n")
            f.write("Abarema cochliocarpos var. something\n")
            temp_path = f.name
        
        try:
            df = load_species_data(temp_path)
            assert df.iloc[0]["Genus"] == "Abarema"
            assert df.iloc[0]["Species"] == "cochliocarpos"
        finally:
            os.unlink(temp_path)
    
    def test_empty_csv_returns_empty_dataframe(self):
        """Test that empty CSV returns empty DataFrame."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("TaxonName\n")
            temp_path = f.name
        
        try:
            df = load_species_data(temp_path)
            assert len(df) == 0
            assert list(df.columns) == ["TaxonName", "Genus", "Species"]
        finally:
            os.unlink(temp_path)
    
    def test_preserves_original_taxon_name(self):
        """Test that original TaxonName is preserved."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("TaxonName\n")
            f.write("Abarema cochliocarpos\n")
            temp_path = f.name
        
        try:
            df = load_species_data(temp_path)
            assert df.iloc[0]["TaxonName"] == "Abarema cochliocarpos"
        finally:
            os.unlink(temp_path)


class TestUtilsIntegration:
    """Integration tests for utils with real data file."""
    
    def test_load_sample_data_file(self):
        """Test loading the actual sample data file if it exists."""
        data_path = Path("data/global_tree_search_trees_1_9.csv")
        
        if data_path.exists():
            df = load_species_data(data_path)
            
            assert len(df) > 0
            assert "TaxonName" in df.columns
            assert "Genus" in df.columns
            assert "Species" in df.columns
            
            # Verify data structure
            assert all(isinstance(x, str) for x in df["Genus"])
            assert all(isinstance(x, str) for x in df["Species"])
