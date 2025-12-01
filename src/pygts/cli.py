"""Command-line interface for the pyGTS package.

This module provides a full-featured CLI with three main commands:
- check: Validate species existence
- fetch: Retrieve geographic distribution data
- visualize: Generate distribution maps

The CLI is installed as 'pygts' when the package is installed.

Usage:
    pygts check <genus> <species>
    pygts fetch <genus> <species> [--json]
    pygts visualize <genus> <species> [-o OUTPUT]
"""

import argparse
import sys

from pygts.data_fetcher import request_data, species_exists
from pygts.visualizer import plot_species_distribution


def cli_check(args):
    """CLI handler for the 'check' command.
    
    Validates whether a species exists in the BGCI database and exits with
    status code 0 for success or 1 for not found. Useful for scripting.
    
    Args:
        args: Argument namespace from argparse containing genus and species.
    """
    exists = species_exists(args.genus, args.species)
    if exists:
        print(f"✓ {args.genus} {args.species} exists in the database")
        sys.exit(0)
    else:
        print(f"✗ {args.genus} {args.species} not found in the database")
        sys.exit(1)


def cli_fetch(args):
    """CLI handler for the 'fetch' command.
    
    Retrieves and displays geographic distribution data for a species.
    Output can be formatted as human-readable grouped text or JSON.
    
    Args:
        args: Argument namespace from argparse containing genus, species,
            and json flag.
    """
    data = request_data(args.genus, args.species)
    
    if data is None:
        print(f"No data found for {args.genus} {args.species}")
        sys.exit(1)
    
    print(f"\nGeographic data for {args.genus} {args.species}:")
    print(f"Total locations: {len(data)}\n")
    
    if args.json:
        import json
        print(json.dumps(data, indent=2))
    else:
        # Group by country
        from collections import defaultdict
        by_country = defaultdict(list)
        for entry in data:
            country = entry.get('country', 'Unknown')
            province = entry.get('province')
            if province:
                by_country[country].append(province)
            else:
                by_country[country].append('(entire country)')
        
        for country in sorted(by_country.keys()):
            provinces = by_country[country]
            print(f"  {country}:")
            for province in sorted(provinces):
                print(f"    - {province}")


def cli_visualize(args):
    """CLI handler for the 'visualize' command.
    
    Generates a world map showing species distribution. Can either display
    interactively or save to a file.
    
    Args:
        args: Argument namespace from argparse containing genus, species,
            and optional output file path.
    """
    plot_species_distribution(args.genus, args.species, save_path=args.output)
    
    if args.output:
        print(f"\n✓ Map saved to {args.output}")
    else:
        print("\n✓ Displaying map...")


def main():
    """Main entry point for the pyGTS command-line interface.
    
    Parses command-line arguments and dispatches to appropriate handler functions.
    Called automatically when the package is run as 'pygts' from the command line.
    
    Commands:
        check: Validate species existence (returns exit code 0/1)
        fetch: Retrieve and display geographic data
        visualize (viz): Generate distribution map
    """
    parser = argparse.ArgumentParser(
        prog="pygts",
        description="Tree species data fetcher and visualizer using BGCI Global Tree Search API"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Check command
    check_parser = subparsers.add_parser(
        "check",
        help="Check if a species exists in the database"
    )
    check_parser.add_argument("genus", help="Genus name (e.g., Abarema)")
    check_parser.add_argument("species", help="Species name (e.g., cochliocarpos)")
    check_parser.set_defaults(func=cli_check)
    
    # Fetch command
    fetch_parser = subparsers.add_parser(
        "fetch",
        help="Fetch geographic data for a species"
    )
    fetch_parser.add_argument("genus", help="Genus name (e.g., Abarema)")
    fetch_parser.add_argument("species", help="Species name (e.g., cochliocarpos)")
    fetch_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON format"
    )
    fetch_parser.set_defaults(func=cli_fetch)
    
    # Visualize command
    viz_parser = subparsers.add_parser(
        "visualize",
        help="Visualize species distribution on a map",
        aliases=["viz"]
    )
    viz_parser.add_argument("genus", help="Genus name (e.g., Abarema)")
    viz_parser.add_argument("species", help="Species name (e.g., cochliocarpos)")
    viz_parser.add_argument(
        "-o", "--output",
        help="Output file path (e.g., map.png). If not specified, displays interactively"
    )
    viz_parser.set_defaults(func=cli_visualize)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute the appropriate function
    args.func(args)


if __name__ == "__main__":
    main()
