"""Tests for visualizer module."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pygts.visualizer import extract_locations, plot_species_distribution


class TestExtractLocations:
    """Tests for extract_locations function."""
    
    def test_empty_list_returns_empty_results(self):
        """Test that empty list returns empty results."""
        countries, provinces = extract_locations([])
        assert countries == []
        assert provinces == []
    
    def test_countries_only(self):
        """Test extraction of country-only data."""
        geo_data = [
            {"country": "France", "province": None},
            {"country": "Spain", "province": None}
        ]
        
        countries, provinces = extract_locations(geo_data)
        assert set(countries) == {"France", "Spain"}
        assert provinces == []
    
    def test_provinces_only(self):
        """Test extraction of province data."""
        geo_data = [
            {"country": "Brazil", "province": "Bahia"},
            {"country": "Brazil", "province": "Ceará"}
        ]
        
        countries, provinces = extract_locations(geo_data)
        assert countries == []
        assert set(provinces) == {("Brazil", "Bahia"), ("Brazil", "Ceará")}
    
    def test_mixed_countries_and_provinces(self):
        """Test extraction of mixed data."""
        geo_data = [
            {"country": "France", "province": None},
            {"country": "Brazil", "province": "Bahia"},
            {"country": "Spain", "province": None}
        ]
        
        countries, provinces = extract_locations(geo_data)
        assert set(countries) == {"France", "Spain"}
        assert provinces == [("Brazil", "Bahia")]
    
    def test_duplicate_countries_deduplication(self):
        """Test that duplicate countries are deduplicated."""
        geo_data = [
            {"country": "France", "province": None},
            {"country": "France", "province": None}
        ]
        
        countries, provinces = extract_locations(geo_data)
        assert countries == ["France"]
        assert provinces == []
    
    def test_missing_country_ignored(self):
        """Test that entries without country are ignored."""
        geo_data = [
            {"province": "Unknown"},
            {"country": "France", "province": None}
        ]
        
        countries, provinces = extract_locations(geo_data)
        assert countries == ["France"]
        assert provinces == []


class TestPlotSpeciesDistribution:
    """Tests for plot_species_distribution function."""
    
    @patch('pygts.visualizer.request_data')
    def test_no_data_returns_early(self, mock_request, capsys):
        """Test that function returns early when no data is available."""
        mock_request.return_value = None
        
        plot_species_distribution("InvalidGenus", "invalid")
        
        captured = capsys.readouterr()
        assert "No geographical data found" in captured.out
    
    @patch('pygts.visualizer.request_data')
    def test_empty_locations_returns_early(self, mock_request, capsys):
        """Test that function returns early when locations are empty."""
        mock_request.return_value = [{"country": None, "province": None}]
        
        plot_species_distribution("InvalidGenus", "invalid")
        
        captured = capsys.readouterr()
        assert "No location data found" in captured.out
    
    @patch('pygts.visualizer.plt.show')
    @patch('pygts.visualizer.gpd.read_file')
    @patch('pygts.visualizer.request_data')
    def test_displays_map_when_no_save_path(self, mock_request, mock_gdf, mock_show):
        """Test that map is displayed when no save path is provided."""
        # Mock data
        mock_request.return_value = [{"country": "France", "province": None}]
        
        # Mock GeoDataFrames
        mock_world = MagicMock()
        mock_provinces = MagicMock()
        mock_gdf.side_effect = [mock_world, mock_provinces]
        
        plot_species_distribution("Abies", "alba")
        
        mock_show.assert_called_once()
    
    @patch('pygts.visualizer.plt.savefig')
    @patch('pygts.visualizer.gpd.read_file')
    @patch('pygts.visualizer.request_data')
    def test_saves_map_when_save_path_provided(self, mock_request, mock_gdf, mock_savefig, capsys):
        """Test that map is saved when save path is provided."""
        # Mock data
        mock_request.return_value = [{"country": "France", "province": None}]
        
        # Mock GeoDataFrames
        mock_world = MagicMock()
        mock_provinces = MagicMock()
        mock_gdf.side_effect = [mock_world, mock_provinces]
        
        plot_species_distribution("Abies", "alba", save_path="test_map.png")
        
        mock_savefig.assert_called_once_with("test_map.png", dpi=300, bbox_inches="tight")
        captured = capsys.readouterr()
        assert "Map saved to test_map.png" in captured.out
    
    @patch('pygts.visualizer.plt.show')
    @patch('pygts.visualizer.gpd.read_file')
    @patch('pygts.visualizer.request_data')
    def test_prints_country_distribution(self, mock_request, mock_gdf, mock_show, capsys):
        """Test that country distribution is printed."""
        mock_request.return_value = [
            {"country": "France", "province": None},
            {"country": "Spain", "province": None}
        ]
        
        mock_world = MagicMock()
        mock_provinces = MagicMock()
        mock_gdf.side_effect = [mock_world, mock_provinces]
        
        plot_species_distribution("Abies", "alba")
        
        captured = capsys.readouterr()
        assert "Abies alba distribution:" in captured.out
        assert "Countries (entire):" in captured.out
    
    @patch('pygts.visualizer.plt.show')
    @patch('pygts.visualizer.gpd.read_file')
    @patch('pygts.visualizer.request_data')
    def test_prints_province_distribution(self, mock_request, mock_gdf, mock_show, capsys):
        """Test that province distribution is printed."""
        mock_request.return_value = [
            {"country": "Brazil", "province": "Bahia"},
            {"country": "Brazil", "province": "Ceará"}
        ]
        
        mock_world = MagicMock()
        mock_provinces = MagicMock()
        mock_gdf.side_effect = [mock_world, mock_provinces]
        
        plot_species_distribution("Abarema", "cochliocarpos")
        
        captured = capsys.readouterr()
        assert "Specific provinces/states:" in captured.out
        assert "Brazil: Bahia" in captured.out
        assert "Brazil: Ceará" in captured.out
    
    @patch('pygts.visualizer.plt.show')
    @patch('pygts.visualizer.gpd.read_file')
    @patch('pygts.visualizer.request_data')
    def test_loads_geodata_correctly(self, mock_request, mock_gdf, mock_show):
        """Test that GeoDataFrames are loaded with correct URLs."""
        mock_request.return_value = [{"country": "France", "province": None}]
        
        mock_world = MagicMock()
        mock_provinces = MagicMock()
        mock_gdf.side_effect = [mock_world, mock_provinces]
        
        plot_species_distribution("Abies", "alba")
        
        # Check that both world map and provinces were loaded
        assert mock_gdf.call_count == 2
        calls = mock_gdf.call_args_list
        assert "ne_110m_admin_0_countries" in calls[0][0][0]
        assert "ne_10m_admin_1_states_provinces" in calls[1][0][0]


class TestIntegrationVisualizer:
    """Integration tests for visualizer (real API, mocked plotting)."""
    
    @patch('pygts.visualizer.plt.show')
    @patch('pygts.visualizer.gpd.read_file')
    def test_real_species_visualization(self, mock_gdf, mock_show):
        """Test visualization with real species data."""
        mock_world = MagicMock()
        mock_provinces = MagicMock()
        mock_gdf.side_effect = [mock_world, mock_provinces]
        
        # This should succeed without errors
        plot_species_distribution("Abarema", "cochliocarpos")
        
        # Verify that geodata was loaded
        assert mock_gdf.call_count == 2
