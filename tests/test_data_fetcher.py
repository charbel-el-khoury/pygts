"""Tests for data_fetcher module."""

import pandas as pd
import pytest
from unittest.mock import Mock, patch, MagicMock
from pygts.data_fetcher import species_exists, request_data, fetch_species_data_parallel


class TestSpeciesExists:
    """Tests for species_exists function."""
    
    def test_existing_species_returns_true(self):
        """Test that an existing species returns True."""
        result = species_exists("Abarema", "cochliocarpos")
        assert result is True
    
    def test_invalid_species_returns_false(self):
        """Test that an invalid species returns False."""
        result = species_exists("InvalidGenus", "invalid_species")
        assert result is False
    
    @patch('pygts.data_fetcher.requests.get')
    def test_network_error_returns_false(self, mock_get):
        """Test that network errors return False gracefully."""
        mock_get.side_effect = Exception("Network error")
        result = species_exists("Abarema", "cochliocarpos")
        assert result is False
    
    @patch('pygts.data_fetcher.requests.get')
    def test_empty_results_returns_false(self, mock_get):
        """Test that empty results return False."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response
        
        result = species_exists("Abarema", "cochliocarpos")
        assert result is False
    
    @patch('pygts.data_fetcher.requests.get')
    def test_valid_response_returns_true(self, mock_get):
        """Test that valid API response returns True."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"TSGeolinks": [{"country": "Brazil"}]}]
        }
        mock_get.return_value = mock_response
        
        result = species_exists("Abarema", "cochliocarpos")
        assert result is True


class TestRequestData:
    """Tests for request_data function."""
    
    def test_existing_species_returns_data(self):
        """Test that an existing species returns data."""
        result = request_data("Abarema", "cochliocarpos")
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        # Check data structure
        assert "country" in result[0]
    
    def test_invalid_species_returns_none(self):
        """Test that an invalid species returns None."""
        result = request_data("InvalidGenus", "invalid_species")
        assert result is None
    
    @patch('pygts.data_fetcher.requests.get')
    def test_network_error_returns_none(self, mock_get):
        """Test that network errors return None gracefully."""
        mock_get.side_effect = Exception("Network error")
        result = request_data("Abarema", "cochliocarpos")
        assert result is None
    
    @patch('pygts.data_fetcher.requests.get')
    def test_malformed_json_returns_none(self, mock_get):
        """Test that malformed JSON returns None."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        result = request_data("Abarema", "cochliocarpos")
        assert result is None
    
    @patch('pygts.data_fetcher.requests.get')
    def test_empty_results_returns_none(self, mock_get):
        """Test that empty results return None."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response
        
        result = request_data("Abarema", "cochliocarpos")
        assert result is None
    
    @patch('pygts.data_fetcher.requests.get')
    def test_valid_response_structure(self, mock_get):
        """Test that valid response has correct structure."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{
                "TSGeolinks": [
                    {"country": "Brazil", "province": "Bahia", "uncertainty": None},
                    {"country": "Brazil", "province": "Ceará", "uncertainty": None}
                ]
            }]
        }
        mock_get.return_value = mock_response
        
        result = request_data("Abarema", "cochliocarpos")
        assert result is not None
        assert len(result) == 2
        assert result[0]["country"] == "Brazil"
        assert result[0]["province"] == "Bahia"


class TestFetchSpeciesDataParallel:
    """Tests for fetch_species_data_parallel function."""
    
    def test_empty_dataframe_returns_empty_list(self):
        """Test that empty DataFrame returns empty list."""
        df = pd.DataFrame(columns=["Genus", "Species"])
        result = fetch_species_data_parallel(df)
        assert result == []
    
    @patch('pygts.data_fetcher.request_data')
    def test_single_species_success(self, mock_request):
        """Test successful fetch for single species."""
        mock_request.return_value = [{"country": "Brazil"}]
        
        df = pd.DataFrame({
            "Genus": ["Abarema"],
            "Species": ["cochliocarpos"]
        })
        
        results = fetch_species_data_parallel(df, max_workers=1)
        assert len(results) == 1
        assert results[0] == [{"country": "Brazil"}]
    
    @patch('pygts.data_fetcher.request_data')
    def test_multiple_species_maintains_order(self, mock_request):
        """Test that results maintain input order."""
        def mock_response(genus, species):
            if genus == "Abarema":
                return [{"country": "Brazil"}]
            elif genus == "Abies":
                return [{"country": "France"}]
            return None
        
        mock_request.side_effect = mock_response
        
        df = pd.DataFrame({
            "Genus": ["Abarema", "Abies", "InvalidGenus"],
            "Species": ["cochliocarpos", "alba", "invalid"]
        })
        
        results = fetch_species_data_parallel(df, max_workers=2)
        assert len(results) == 3
        assert results[0] == [{"country": "Brazil"}]
        assert results[1] == [{"country": "France"}]
        assert results[2] is None
    
    @patch('pygts.data_fetcher.request_data')
    def test_handles_failures_gracefully(self, mock_request):
        """Test that failures don't break the entire batch."""
        def mock_response(genus, species):
            if genus == "Abarema":
                return [{"country": "Brazil"}]
            return None
        
        mock_request.side_effect = mock_response
        
        df = pd.DataFrame({
            "Genus": ["Abarema", "InvalidGenus"],
            "Species": ["cochliocarpos", "invalid"]
        })
        
        results = fetch_species_data_parallel(df, max_workers=1)
        assert len(results) == 2
        assert results[0] is not None
        assert results[1] is None
    
    @patch('pygts.data_fetcher.request_data')
    def test_exception_handling(self, mock_request):
        """Test that exceptions are caught and recorded."""
        mock_request.side_effect = Exception("Unexpected error")
        
        df = pd.DataFrame({
            "Genus": ["Abarema"],
            "Species": ["cochliocarpos"]
        })
        
        results = fetch_species_data_parallel(df, max_workers=1)
        assert len(results) == 1
        assert isinstance(results[0], dict)
        assert "error" in results[0]


class TestIntegration:
    """Integration tests using real API."""
    
    def test_real_species_workflow(self):
        """Test complete workflow with real species."""
        # Check existence
        exists = species_exists("Abarema", "cochliocarpos")
        assert exists is True
        
        # Fetch data
        data = request_data("Abarema", "cochliocarpos")
        assert data is not None
        assert len(data) > 0
        assert "country" in data[0]
    
    def test_parallel_fetch_real_species(self):
        """Test parallel fetching with real species."""
        df = pd.DataFrame({
            "Genus": ["Abarema", "Abies"],
            "Species": ["cochliocarpos", "alba"]
        })
        
        results = fetch_species_data_parallel(df, max_workers=2)
        assert len(results) == 2
        assert all(r is not None for r in results)
        assert all(isinstance(r, list) for r in results)
