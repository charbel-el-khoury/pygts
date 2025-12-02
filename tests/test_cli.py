"""Tests for CLI module."""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from pygts.cli import cli_check, cli_fetch, cli_visualize, main


class TestCliCheck:
    """Tests for cli_check function."""
    
    @patch('pygts.cli.species_exists')
    def test_existing_species_exits_zero(self, mock_exists):
        """Test that existing species exits with code 0."""
        mock_exists.return_value = True
        args = Mock(genus="Abarema", species="cochliocarpos")
        
        with pytest.raises(SystemExit) as exc_info:
            cli_check(args)
        
        assert exc_info.value.code == 0
    
    @patch('pygts.cli.species_exists')
    def test_non_existing_species_exits_one(self, mock_exists):
        """Test that non-existing species exits with code 1."""
        mock_exists.return_value = False
        args = Mock(genus="InvalidGenus", species="invalid")
        
        with pytest.raises(SystemExit) as exc_info:
            cli_check(args)
        
        assert exc_info.value.code == 1
    
    @patch('pygts.cli.species_exists')
    def test_prints_success_message(self, mock_exists, capsys):
        """Test that success message is printed."""
        mock_exists.return_value = True
        args = Mock(genus="Abarema", species="cochliocarpos")
        
        with pytest.raises(SystemExit):
            cli_check(args)
        
        captured = capsys.readouterr()
        assert "✓" in captured.out
        assert "Abarema cochliocarpos exists" in captured.out
    
    @patch('pygts.cli.species_exists')
    def test_prints_failure_message(self, mock_exists, capsys):
        """Test that failure message is printed."""
        mock_exists.return_value = False
        args = Mock(genus="InvalidGenus", species="invalid")
        
        with pytest.raises(SystemExit):
            cli_check(args)
        
        captured = capsys.readouterr()
        assert "✗" in captured.out
        assert "not found" in captured.out


class TestCliFetch:
    """Tests for cli_fetch function."""
    
    @patch('pygts.cli.request_data')
    def test_no_data_exits_one(self, mock_request):
        """Test that no data exits with code 1."""
        mock_request.return_value = None
        args = Mock(genus="InvalidGenus", species="invalid", json=False)
        
        with pytest.raises(SystemExit) as exc_info:
            cli_fetch(args)
        
        assert exc_info.value.code == 1
    
    @patch('pygts.cli.request_data')
    def test_displays_human_readable_output(self, mock_request, capsys):
        """Test human-readable output format."""
        mock_request.return_value = [
            {"country": "Brazil", "province": "Bahia"},
            {"country": "Brazil", "province": "Ceará"},
            {"country": "France", "province": None}
        ]
        args = Mock(genus="Abarema", species="cochliocarpos", json=False)
        
        cli_fetch(args)
        
        captured = capsys.readouterr()
        assert "Geographic data for Abarema cochliocarpos" in captured.out
        assert "Total locations: 3" in captured.out
        assert "Brazil:" in captured.out
        assert "Bahia" in captured.out
        assert "Ceará" in captured.out
        assert "France:" in captured.out
    
    @patch('pygts.cli.request_data')
    def test_displays_json_output(self, mock_request, capsys):
        """Test JSON output format."""
        mock_request.return_value = [
            {"country": "Brazil", "province": "Bahia"},
            {"country": "France", "province": None}
        ]
        args = Mock(genus="Abarema", species="cochliocarpos", json=True)
        
        cli_fetch(args)
        
        captured = capsys.readouterr()
        assert '"country": "Brazil"' in captured.out
        assert '"province": "Bahia"' in captured.out
    
    @patch('pygts.cli.request_data')
    def test_groups_by_country(self, mock_request, capsys):
        """Test that output is grouped by country."""
        mock_request.return_value = [
            {"country": "Brazil", "province": "Bahia"},
            {"country": "Brazil", "province": "Ceará"},
            {"country": "France", "province": None}
        ]
        args = Mock(genus="Test", species="test", json=False)
        
        cli_fetch(args)
        
        captured = capsys.readouterr()
        # Check that Brazil appears before its provinces
        brazil_idx = captured.out.find("Brazil:")
        bahia_idx = captured.out.find("Bahia")
        assert brazil_idx < bahia_idx


class TestCliVisualize:
    """Tests for cli_visualize function."""
    
    @patch('pygts.cli.plot_species_distribution')
    def test_calls_plot_function(self, mock_plot):
        """Test that plot function is called with correct arguments."""
        args = Mock(genus="Abarema", species="cochliocarpos", output=None)
        
        cli_visualize(args)
        
        mock_plot.assert_called_once_with("Abarema", "cochliocarpos", save_path=None)
    
    @patch('pygts.cli.plot_species_distribution')
    def test_calls_plot_with_save_path(self, mock_plot):
        """Test that plot function receives save path."""
        args = Mock(genus="Abarema", species="cochliocarpos", output="map.png")
        
        cli_visualize(args)
        
        mock_plot.assert_called_once_with("Abarema", "cochliocarpos", save_path="map.png")
    
    @patch('pygts.cli.plot_species_distribution')
    def test_prints_save_confirmation(self, mock_plot, capsys):
        """Test that save confirmation is printed."""
        args = Mock(genus="Abarema", species="cochliocarpos", output="map.png")
        
        cli_visualize(args)
        
        captured = capsys.readouterr()
        assert "Map saved to map.png" in captured.out
    
    @patch('pygts.cli.plot_species_distribution')
    def test_prints_display_message(self, mock_plot, capsys):
        """Test that display message is printed."""
        args = Mock(genus="Abarema", species="cochliocarpos", output=None)
        
        cli_visualize(args)
        
        captured = capsys.readouterr()
        assert "Displaying map" in captured.out


class TestMainFunction:
    """Tests for main function."""
    
    @patch('sys.argv', ['pygts'])
    def test_no_command_prints_help(self):
        """Test that no command prints help and exits."""
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('sys.argv', ['pygts', 'check', 'Abarema', 'cochliocarpos'])
    @patch('pygts.cli.species_exists')
    def test_check_command_execution(self, mock_exists):
        """Test that check command is executed."""
        mock_exists.return_value = True
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        mock_exists.assert_called_once_with('Abarema', 'cochliocarpos')
        assert exc_info.value.code == 0
    
    @patch('sys.argv', ['pygts', 'fetch', 'Abarema', 'cochliocarpos'])
    @patch('pygts.cli.request_data')
    def test_fetch_command_execution(self, mock_request):
        """Test that fetch command is executed."""
        mock_request.return_value = [{"country": "Brazil"}]
        
        main()
        
        mock_request.assert_called_once_with('Abarema', 'cochliocarpos')
    
    @patch('sys.argv', ['pygts', 'fetch', 'Abarema', 'cochliocarpos', '--json'])
    @patch('pygts.cli.request_data')
    def test_fetch_with_json_flag(self, mock_request, capsys):
        """Test that JSON flag is processed."""
        mock_request.return_value = [{"country": "Brazil"}]
        
        main()
        
        captured = capsys.readouterr()
        assert '"country": "Brazil"' in captured.out
    
    @patch('sys.argv', ['pygts', 'visualize', 'Abarema', 'cochliocarpos'])
    @patch('pygts.cli.plot_species_distribution')
    def test_visualize_command_execution(self, mock_plot):
        """Test that visualize command is executed."""
        main()
        
        mock_plot.assert_called_once_with('Abarema', 'cochliocarpos', save_path=None)
    
    @patch('sys.argv', ['pygts', 'viz', 'Abarema', 'cochliocarpos', '-o', 'map.png'])
    @patch('pygts.cli.plot_species_distribution')
    def test_viz_alias_works(self, mock_plot):
        """Test that 'viz' alias works."""
        main()
        
        mock_plot.assert_called_once_with('Abarema', 'cochliocarpos', save_path='map.png')
    
    @patch('sys.argv', ['pygts', 'visualize', 'Abarema', 'cochliocarpos', '--output', 'map.png'])
    @patch('pygts.cli.plot_species_distribution')
    def test_output_long_form(self, mock_plot):
        """Test that --output long form works."""
        main()
        
        mock_plot.assert_called_once_with('Abarema', 'cochliocarpos', save_path='map.png')
