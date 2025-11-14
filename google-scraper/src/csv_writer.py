"""
CSV Writer Module
Handles writing scraper results to CSV files
"""
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class CSVWriter:
    """Simple CSV writer for scraper results"""

    def __init__(self, output_dir: str = "data"):
        """
        Initialize CSV writer

        Args:
            output_dir: Directory to save CSV files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_results(self, results: Dict[str, List[str]], filename: str = None) -> Path:
        """
        Write scraper results to CSV file

        Args:
            results: Dictionary mapping query -> list of suggestions
            filename: Optional filename (auto-generated if not provided)

        Returns:
            Path to the created CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"suggestions_{timestamp}.csv"

        filepath = self.output_dir / filename

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(['query', 'suggestion_rank', 'suggestion_text'])

            # Write data
            for query, suggestions in results.items():
                if not suggestions:
                    # Write row even if no suggestions found
                    writer.writerow([query, 0, ''])
                else:
                    for rank, suggestion in enumerate(suggestions, 1):
                        writer.writerow([query, rank, suggestion])

        print(f"\nResults saved to: {filepath}")
        return filepath

    def write_flat_results(self, results: Dict[str, List[str]], filename: str = None) -> Path:
        """
        Write results in flat format (one column per query)

        Args:
            results: Dictionary mapping query -> list of suggestions
            filename: Optional filename

        Returns:
            Path to the created CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"suggestions_flat_{timestamp}.csv"

        filepath = self.output_dir / filename

        # Prepare data
        max_suggestions = max((len(sugs) for sugs in results.values()), default=0)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            queries = list(results.keys())
            writer.writerow(queries)

            # Write suggestions row by row
            for i in range(max_suggestions):
                row = []
                for query in queries:
                    suggestions = results[query]
                    row.append(suggestions[i] if i < len(suggestions) else '')
                writer.writerow(row)

        print(f"Flat results saved to: {filepath}")
        return filepath
