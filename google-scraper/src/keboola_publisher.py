"""
Keboola Data Publisher
Publishes scraper results to Keboola Storage for public access
"""
from kbcstorage.client import Client
from typing import Dict, List
import csv
import os
from pathlib import Path
from datetime import datetime


class KeboolaPublisher:
    """Publisher for Keboola Connection Storage"""

    def __init__(self, token: str = None, url: str = None):
        """
        Initialize Keboola publisher

        Args:
            token: Keboola Storage API token (or set KEBOOLA_STORAGE_TOKEN env var)
            url: Keboola Storage API URL (or set KEBOOLA_STORAGE_URL env var)
        """
        self.token = token or os.getenv('KEBOOLA_STORAGE_TOKEN')
        self.url = url or os.getenv('KEBOOLA_STORAGE_URL', 'https://connection.keboola.com')

        if not self.token:
            raise ValueError(
                "Keboola Storage token required. Set KEBOOLA_STORAGE_TOKEN env var or pass token parameter.\n"
                "Get your token at: https://connection.keboola.com/admin/projects"
            )

        self.client = Client(self.url, self.token)
        self.bucket_name = "in.c-google-scraper"
        self.table_name = "google_autocomplete_suggestions"

    def ensure_bucket(self):
        """Ensure the storage bucket exists"""
        try:
            buckets = self.client.buckets.list()
            bucket_exists = any(b['id'] == self.bucket_name for b in buckets)

            if not bucket_exists:
                print(f"Creating bucket: {self.bucket_name}")
                self.client.buckets.create(
                    name="google-scraper",
                    stage="in",
                    description="Google autocomplete suggestions data"
                )
                print(f"✓ Bucket created: {self.bucket_name}")
            else:
                print(f"✓ Bucket exists: {self.bucket_name}")

        except Exception as e:
            print(f"Note: Bucket check/create: {e}")

    def prepare_csv(self, results: Dict[str, List[str]], output_path: Path) -> Path:
        """
        Prepare CSV file for upload

        Args:
            results: Dictionary mapping query -> list of suggestions
            output_path: Path to save the CSV file

        Returns:
            Path to the created CSV file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow([
                'query',
                'suggestion_rank',
                'suggestion_text',
                'scraped_at'
            ])

            # Write data
            timestamp = datetime.now().isoformat()
            for query, suggestions in results.items():
                if not suggestions:
                    writer.writerow([query, 0, '', timestamp])
                else:
                    for rank, suggestion in enumerate(suggestions, 1):
                        writer.writerow([query, rank, suggestion, timestamp])

        print(f"✓ CSV prepared: {output_path}")
        return output_path

    def publish(self, results: Dict[str, List[str]], incremental: bool = False) -> str:
        """
        Publish results to Keboola Storage

        Args:
            results: Dictionary mapping query -> list of suggestions
            incremental: If True, append to existing data. If False, replace.

        Returns:
            Table ID in Keboola Storage
        """
        print("\n" + "=" * 60)
        print("Publishing to Keboola Storage")
        print("=" * 60)

        # Ensure bucket exists
        self.ensure_bucket()

        # Prepare CSV file
        temp_dir = Path("data/temp")
        csv_path = self.prepare_csv(results, temp_dir / "keboola_upload.csv")

        try:
            table_id = f"{self.bucket_name}.{self.table_name}"

            # Upload to Keboola
            print(f"\nUploading to table: {table_id}")
            print(f"Mode: {'Incremental (append)' if incremental else 'Full (replace)'}")

            self.client.tables.load(
                table_id=table_id,
                file_path=str(csv_path),
                is_incremental=incremental
            )

            print(f"✓ Data published successfully!")
            print(f"\nTable ID: {table_id}")

            # Get table info
            table_info = self.client.tables.detail(table_id)
            row_count = table_info.get('rowsCount', 0)

            print(f"Total rows in table: {row_count}")
            print(f"\n{'=' * 60}")

            # Clean up temp file
            csv_path.unlink(missing_ok=True)

            return table_id

        except Exception as e:
            print(f"\n❌ Error publishing to Keboola: {e}")
            print("\nTroubleshooting:")
            print("1. Check your KEBOOLA_STORAGE_TOKEN is valid")
            print("2. Ensure you have write permissions to the bucket")
            print("3. Verify the bucket exists or can be created")
            raise

    def get_public_url(self, table_id: str = None) -> str:
        """
        Get information about accessing the published data

        Args:
            table_id: Table ID (uses default if not provided)

        Returns:
            Information about accessing the data
        """
        if table_id is None:
            table_id = f"{self.bucket_name}.{self.table_name}"

        info = f"""
Data Access Information
{'=' * 60}

Table ID: {table_id}

To access this data:

1. Via Keboola UI:
   {self.url}/admin/projects

2. Via API:
   Use the Keboola Storage API to export the table

3. Via Data Sharing:
   Set up Keboola Data Catalog sharing for public access

4. Export to CSV:
   Use Keboola's export functionality to generate public links

For public sharing, you can:
- Use Keboola Data Apps to create a public interface
- Export to cloud storage (S3, GCS) with public access
- Use Keboola's data sharing features

{'=' * 60}
"""
        return info
