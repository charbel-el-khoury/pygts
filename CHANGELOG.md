# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-01

### Added
- Initial release of pyGTS (Python Global Tree Search)
- Core functionality for fetching species data from BGCI Global Tree Search API
- `species_exists()` function to check if species exists in database
- `request_data()` function to fetch geographic distribution data
- `fetch_species_data_parallel()` for batch processing multiple species
- `plot_species_distribution()` for creating world map visualizations
- Command-line interface with three commands: check, fetch, visualize
- Comprehensive error handling for API requests and data parsing
- Progress bars for parallel operations using tqdm
- Support for JSON and human-readable output formats
- Interactive and file-based map output options
- Utility functions for loading species data from CSV files
- Full documentation with docstrings and examples
- README with usage examples and API reference

### Features
- Robust error handling with graceful degradation
- Parallel processing with configurable worker threads
- High-quality map visualizations with GeoPandas and Matplotlib
- Dual interface: CLI and Python API
- Distinguishes between country-level and province-level occurrences
- Automatic base map downloading and caching

[Unreleased]: https://github.com/charbel-el-khoury/pygts/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/charbel-el-khoury/pygts/releases/tag/v0.1.0
