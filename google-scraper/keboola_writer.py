"""
Keboola Storage Writer

Writes scraped data to Keboola Storage as a publicly accessible CSV table.
"""

import csv
import os
from typing import List, Dict
from datetime import datetime
from kbcstorage.client import Client


class KeboolaWriter:
    """Writes data to Keboola Storage"""

    def __init__(self, keboola_token: str, keboola_url: str):
        """
        Initialize Keboola Storage client

        Args:
            keboola_token: Keboola Storage API token
            keboola_url: Keboola Storage API URL (e.g., https://connection.keboola.com)
        """
        self.client = Client(keboola_url, keboola_token)
        self.bucket_name = "in.c-google-suggestions"
        self.table_name = "google_hate_suggestions"

    def create_bucket_if_needed(self):
        """Create storage bucket if it doesn't exist"""
        try:
            # List all buckets
            buckets = self.client.buckets.list()
            bucket_ids = [b['id'] for b in buckets]

            if self.bucket_name not in bucket_ids:
                print(f"Creating bucket: {self.bucket_name}")
                self.client.buckets.create(
                    name="google-suggestions",
                    stage="in",
                    description="Google autocomplete suggestions data"
                )
                print(f"✓ Bucket created")
            else:
                print(f"✓ Bucket exists: {self.bucket_name}")

        except Exception as e:
            print(f"Error managing bucket: {str(e)}")
            raise

    def write_to_csv(self, data: List[Dict], filename: str = "suggestions.csv") -> str:
        """
        Write data to local CSV file

        Args:
            data: List of dictionaries with scraped data
            filename: Output filename

        Returns:
            Path to created CSV file
        """
        filepath = f"/tmp/{filename}"

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

        print(f"✓ CSV created: {filepath}")
        return filepath

    def upload_to_keboola(self, data: List[Dict]) -> str:
        """
        Upload data to Keboola Storage

        Args:
            data: List of dictionaries with scraped data

        Returns:
            Table ID in Keboola Storage
        """
        if not data:
            raise ValueError("No data to upload")

        # Create bucket if needed
        self.create_bucket_if_needed()

        # Write to temporary CSV
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        csv_file = self.write_to_csv(data, f"suggestions_{timestamp}.csv")

        # Table ID format: bucket.table
        table_id = f"{self.bucket_name}.{self.table_name}"

        try:
            # Check if table exists
            tables = self.client.tables.list()
            table_ids = [t['id'] for t in tables]

            if table_id in table_ids:
                print(f"Updating existing table: {table_id}")
                # Update existing table (append or replace)
                self.client.tables.load(
                    table_id=table_id,
                    file_path=csv_file,
                    is_incremental=False  # Replace data each time
                )
            else:
                print(f"Creating new table: {table_id}")
                # Create new table
                self.client.tables.create(
                    name=self.table_name,
                    file_path=csv_file,
                    bucket_id=self.bucket_name,
                    primary_key=["query"]
                )

            print(f"✓ Data uploaded to Keboola Storage: {table_id}")

            # Clean up temp file
            os.remove(csv_file)

            return table_id

        except Exception as e:
            print(f"Error uploading to Keboola: {str(e)}")
            raise

    def get_public_url(self, table_id: str) -> str:
        """
        Get public URL for the table (if sharing is enabled)

        Args:
            table_id: Keboola table ID

        Returns:
            Public URL or instructions
        """
        # Note: Keboola doesn't provide direct public URLs by default
        # Data needs to be shared via Data Catalog or exported to public storage
        return f"Table uploaded: {table_id}\nAccess via Keboola Storage or configure public sharing in Data Catalog"


def main():
    """Test the writer standalone"""
    from dotenv import load_dotenv

    load_dotenv()

    keboola_token = os.getenv("KEBOOLA_TOKEN")
    keboola_url = os.getenv("KEBOOLA_URL", "https://connection.keboola.com")

    if not keboola_token:
        raise ValueError("KEBOOLA_TOKEN not found in environment")

    # Sample data
    sample_data = [
        {
            "query": "i hate",
            "suggestions": "monday|my job|mornings",
            "suggestion_count": 3,
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "query": "i hate a",
            "suggestions": "apples|airplanes",
            "suggestion_count": 2,
            "timestamp": datetime.utcnow().isoformat()
        }
    ]

    writer = KeboolaWriter(keboola_token, keboola_url)
    table_id = writer.upload_to_keboola(sample_data)
    print(writer.get_public_url(table_id))


if __name__ == "__main__":
    main()
