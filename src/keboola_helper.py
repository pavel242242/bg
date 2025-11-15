"""
Keboola Storage API helper - minimal wrapper for table sampling.
"""
import os
import tempfile
from typing import Optional
from kbcstorage import Client


class KeboolaHelper:
    """Simple helper for Keboola Storage API operations."""

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize Keboola client.

        Args:
            url: Keboola connection URL (defaults to KBC_URL env var)
            token: Storage API token (defaults to KBC_TOKEN env var)
        """
        self.url = url or os.getenv("KBC_URL")
        self.token = token or os.getenv("KBC_TOKEN")

        if not self.url or not self.token:
            raise ValueError("KBC_URL and KBC_TOKEN must be set")

        self.client = Client(self.url, self.token)

    def get_table_sample_csv(self, table_id: str, limit: int = 5) -> str:
        """
        Export a sample of rows from a Keboola table as CSV string.

        Args:
            table_id: Full table ID (e.g., "in.c-main.orders")
            limit: Number of rows to export (default: 5)

        Returns:
            CSV string with header and sample rows

        Raises:
            Exception: If table doesn't exist or export fails
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = os.path.join(temp_dir, "sample.csv")

            # Export table with limit
            self.client.tables.export_to_file(
                table_id=table_id,
                path_name=export_path,
                limit=limit
            )

            # Read exported CSV
            with open(export_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()

            return csv_content

    def list_buckets(self) -> list:
        """
        List all buckets in the project.

        Returns:
            List of bucket objects
        """
        return self.client.buckets.list()

    def list_tables(self, bucket_id: Optional[str] = None) -> list:
        """
        List tables, optionally filtered by bucket.

        Args:
            bucket_id: Optional bucket ID to filter by

        Returns:
            List of table objects
        """
        tables = self.client.tables.list()

        if bucket_id:
            tables = [t for t in tables if t.get('bucket', {}).get('id') == bucket_id]

        return tables
