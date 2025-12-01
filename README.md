# pyGTS

**Python Global Tree Search** - A Python package for fetching and visualizing geographic distribution data for tree species from the [BGCI Global Tree Search](https://www.bgci.org/resources/global-tree-search/) database.

[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- 🌍 **Geographic Data Fetching**: Retrieve detailed location data (countries and provinces) for any tree species
- 🗺️ **Interactive Visualizations**: Generate beautiful world maps showing species distribution
- ⚡ **Parallel Processing**: Efficiently fetch data for multiple species concurrently
- 🛡️ **Robust Error Handling**: Gracefully handles API errors, timeouts, and missing data
- 🖥️ **Dual Interface**: Use as a command-line tool or Python library
- 📊 **Flexible Output**: Human-readable or JSON format for easy integration

## Installation

### From PyPI (once published)

```bash
pip install pygts
```

### From Source

```bash
git clone https://github.com/charbel-el-khoury/pygts
cd pygts
pip install -e .
```

## Quick Start

### Command Line Interface

Check if a species exists:
```bash
pygts check Abarema cochliocarpos
# Output: ✓ Abarema cochliocarpos exists in the database
```

Fetch geographic data:
```bash
pygts fetch Abarema cochliocarpos

# Output:
# Geographic data for Abarema cochliocarpos:
# Total locations: 11
#
#   Brazil:
#     - Alagoas
#     - Bahia
#     - Ceará
#     ...
```

Create a distribution map:
```bash
pygts visualize Abies alba -o abies_map.png
```

### Python API

```python
from pygts import request_data, species_exists, plot_species_distribution

# Check if a species exists
if species_exists("Abarema", "cochliocarpos"):
    print("Species found!")

# Fetch geographic distribution data
data = request_data("Abarema", "cochliocarpos")
if data:
    print(f"Found in {len(data)} locations")
    for location in data:
        print(f"  {location['country']}: {location.get('province', 'entire country')}")

# Generate a distribution map
plot_species_distribution("Abies", "alba", save_path="abies_distribution.png")
```

### Batch Processing

```python
import pandas as pd
from pygts.data_fetcher import fetch_species_data_parallel
from pygts.utils import load_species_data

# Load species list from CSV
species_df = load_species_data("data/species_list.csv")

# Fetch data for all species in parallel
results = fetch_species_data_parallel(species_df, max_workers=10)
species_df['geo_data'] = results

# Filter successful results
successful = species_df[species_df['geo_data'].notna()]
print(f"Successfully fetched data for {len(successful)} species")
```

## CLI Reference

### Global Options

```bash
pygts --help  # Show all available commands
```

### Commands

#### `check` - Validate Species Existence

Check if a species exists in the BGCI database.

```bash
pygts check <genus> <species>
```

**Exit Codes:**
- `0`: Species exists
- `1`: Species not found

**Example:**
```bash
pygts check Abarema cochliocarpos
```

#### `fetch` - Retrieve Geographic Data

Fetch and display geographic distribution data.

```bash
pygts fetch <genus> <species> [--json]
```

**Options:**
- `--json`: Output in JSON format (default: human-readable)

**Examples:**
```bash
# Human-readable format
pygts fetch Abarema cochliocarpos

# JSON output for scripting
pygts fetch Abies alba --json > output.json
```

#### `visualize` - Generate Distribution Map

Create a world map showing species distribution.

```bash
pygts visualize <genus> <species> [-o OUTPUT]
```

**Alias:** `viz`

**Options:**
- `-o, --output`: Save to file (PNG, PDF, SVG, JPG). If omitted, displays interactively.

**Examples:**
```bash
# Display interactive map
pygts visualize Abarema cochliocarpos

# Save to file
pygts viz Abies alba -o abies_map.png
```

## API Reference

### Core Functions

#### `species_exists(genus: str, species: str) -> bool`

Check if a species exists in the BGCI database.

**Parameters:**
- `genus` (str): Genus name (e.g., "Abarema")
- `species` (str): Species epithet (e.g., "cochliocarpos")

**Returns:** `bool` - True if species exists, False otherwise

---

#### `request_data(genus: str, species: str) -> list[dict] | None`

Fetch geographic distribution data for a species.

**Parameters:**
- `genus` (str): Genus name
- `species` (str): Species epithet

**Returns:** List of location dictionaries or None if not found. Each dict contains:
- `country` (str): Country name
- `province` (str | None): Province/state name
- `uncertainty` (str | None): Data uncertainty indicator

---

#### `fetch_species_data_parallel(species_df: pd.DataFrame, max_workers: int = 10) -> list`

Fetch data for multiple species in parallel.

**Parameters:**
- `species_df` (pd.DataFrame): DataFrame with 'Genus' and 'Species' columns
- `max_workers` (int): Maximum concurrent threads (default: 10)

**Returns:** Ordered list of results matching input DataFrame

---

#### `plot_species_distribution(genus: str, species: str, save_path: str = None)`

Generate a world map visualization of species distribution.

**Parameters:**
- `genus` (str): Genus name
- `species` (str): Species epithet
- `save_path` (str, optional): File path to save map. If None, displays interactively.

**Map Legend:**
- Dark green: Countries where species occurs throughout
- Light green: Specific provinces/states with occurrences
- Gray: Areas where species is not recorded

## Requirements

- Python 3.14+
- geopandas >= 1.1.1
- matplotlib >= 3.10.7
- pandas >= 2.3.3
- requests >= 2.32.5
- tqdm >= 4.67.1

## Data Source

This package uses the [BGCI Global Tree Search](https://www.bgci.org/resources/global-tree-search/) API, which provides comprehensive data on the world's tree species from Botanic Gardens Conservation International.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Data provided by [BGCI Global Tree Search](https://www.bgci.org/resources/global-tree-search/)
- Base maps from [Natural Earth](https://www.naturalearthdata.com/)

## Citation

If you use this package in your research, please cite:

```bibtex
@software{pygts,
  title = {pyGTS: Python Global Tree Search - Tree Species Geographic Data Fetcher and Visualizer},
  author = {Charbel EL KHOURY},
  year = {2025},
  url = {https://github.com/charbel-el-khoury/pygts}
}
```

## Support

- **Issues**: [GitHub Issues](https://github.com/charbel-el-khoury/pygts/issues)
- **Documentation**: [Full Documentation](https://github.com/charbel-el-khoury/pygts/wiki)
- **BGCI**: [Global Tree Search](https://www.bgci.org/resources/global-tree-search/)
