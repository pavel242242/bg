#!/usr/bin/env python3
"""
Export data from Keboola to JSON for the visualization page
"""

import os
import json
from dotenv import load_dotenv
from keboola_writer import KeboolaWriter


def export_to_json():
    """Export Keboola table to JSON file"""
    load_dotenv()

    keboola_token = os.getenv("KEBOOLA_TOKEN")
    keboola_url = os.getenv("KEBOOLA_URL", "https://connection.keboola.com")

    writer = KeboolaWriter(keboola_token, keboola_url)
    table_id = "in.c-google-suggestions.google_hate_suggestions"

    print(f"Fetching data from Keboola table: {table_id}...")

    # Get table data
    table_data = writer.client.tables.detail(table_id)

    # Download table as CSV, then convert to JSON
    import tempfile
    import csv

    temp_dir = tempfile.mkdtemp()

    # Export table to CSV (it will create a file in temp_dir)
    writer.client.tables.export_to_file(table_id, temp_dir)

    # The file will be named after the table
    temp_file = os.path.join(temp_dir, 'google_hate_suggestions')

    # Read CSV and convert to JSON
    data = []
    with open(temp_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Split suggestions by pipe
            suggestions = row['suggestions'].split('|') if row['suggestions'] else []
            data.append({
                'query': row['query'],
                'suggestions': suggestions,
                'count': int(row['suggestion_count']),
                'timestamp': row['timestamp']
            })

    # Clean up temp directory
    import shutil
    shutil.rmtree(temp_dir)

    # Write to JSON
    output_file = 'data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"✓ Exported {len(data)} records to {output_file}")

    return data


if __name__ == "__main__":
    export_to_json()
