"""
Sample fixtures for mock Grafana API.
Loads realistic test data into DuckDB.
"""

import json
from datetime import datetime, timedelta
from db import get_connection

def load_fixtures():
    """Load sample data into the database."""
    conn = get_connection()

    # Load folders
    folders = [
        (1, "general", "General"),
        (2, "monitoring", "Monitoring"),
        (3, "business", "Business Metrics")
    ]

    for folder in folders:
        conn.execute(
            "INSERT INTO folders (id, uid, title) VALUES (?, ?, ?)",
            folder
        )

    # Load datasources
    datasources = [
        (
            1,
            "prometheus-1",
            "Prometheus",
            "prometheus",
            "http://prometheus:9090",
            "proxy",
            True,
            json.dumps({"timeInterval": "15s", "httpMethod": "POST"})
        ),
        (
            2,
            "postgres-1",
            "PostgreSQL",
            "postgres",
            "postgres:5432",
            "proxy",
            False,
            json.dumps({"sslmode": "require", "database": "metrics"})
        ),
        (
            3,
            "loki-1",
            "Loki",
            "loki",
            "http://loki:3100",
            "proxy",
            False,
            json.dumps({"maxLines": 1000})
        )
    ]

    for ds in datasources:
        conn.execute(
            """
            INSERT INTO datasources (id, uid, name, type, url, access, is_default, json_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ds
        )

    # Load dashboards
    dashboards = [
        {
            "id": 1,
            "uid": "system-overview",
            "title": "System Overview",
            "tags": json.dumps(["system", "production"]),
            "starred": True,
            "folder_id": 2,
            "folder_uid": "monitoring",
            "folder_title": "Monitoring",
            "json_model": json.dumps({
                "uid": "system-overview",
                "title": "System Overview",
                "tags": ["system", "production"],
                "timezone": "browser",
                "schemaVersion": 38,
                "version": 1,
                "panels": [
                    {
                        "id": 1,
                        "type": "graph",
                        "title": "CPU Usage",
                        "targets": [
                            {
                                "expr": "avg(rate(cpu_usage[5m]))",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 2,
                        "type": "graph",
                        "title": "Memory Usage",
                        "targets": [
                            {
                                "expr": "memory_used_bytes / memory_total_bytes",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    }
                ]
            }),
            "created_at": datetime.now() - timedelta(days=30),
            "updated_at": datetime.now() - timedelta(days=1),
            "version": 5
        },
        {
            "id": 2,
            "uid": "api-metrics",
            "title": "API Metrics",
            "tags": json.dumps(["api", "production", "http"]),
            "starred": False,
            "folder_id": 2,
            "folder_uid": "monitoring",
            "folder_title": "Monitoring",
            "json_model": json.dumps({
                "uid": "api-metrics",
                "title": "API Metrics",
                "tags": ["api", "production", "http"],
                "timezone": "browser",
                "schemaVersion": 38,
                "version": 1,
                "panels": [
                    {
                        "id": 1,
                        "type": "graph",
                        "title": "Request Rate",
                        "targets": [
                            {
                                "expr": "sum(rate(http_requests_total[5m])) by (endpoint)",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 2,
                        "type": "graph",
                        "title": "Error Rate",
                        "targets": [
                            {
                                "expr": "sum(rate(http_errors_total[5m])) by (endpoint)",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "id": 3,
                        "type": "graph",
                        "title": "Response Time (p95)",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"x": 0, "y": 8, "w": 24, "h": 8}
                    }
                ]
            }),
            "created_at": datetime.now() - timedelta(days=20),
            "updated_at": datetime.now() - timedelta(hours=6),
            "version": 12
        },
        {
            "id": 3,
            "uid": "sales-dashboard",
            "title": "Sales Dashboard",
            "tags": json.dumps(["business", "sales"]),
            "starred": True,
            "folder_id": 3,
            "folder_uid": "business",
            "folder_title": "Business Metrics",
            "json_model": json.dumps({
                "uid": "sales-dashboard",
                "title": "Sales Dashboard",
                "tags": ["business", "sales"],
                "timezone": "browser",
                "schemaVersion": 38,
                "version": 1,
                "panels": [
                    {
                        "id": 1,
                        "type": "stat",
                        "title": "Total Revenue",
                        "targets": [
                            {
                                "query": "SELECT SUM(amount) FROM sales WHERE date >= NOW() - INTERVAL '30 days'",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4}
                    },
                    {
                        "id": 2,
                        "type": "stat",
                        "title": "Orders Today",
                        "targets": [
                            {
                                "query": "SELECT COUNT(*) FROM orders WHERE date = CURRENT_DATE",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"x": 6, "y": 0, "w": 6, "h": 4}
                    }
                ]
            }),
            "created_at": datetime.now() - timedelta(days=15),
            "updated_at": datetime.now() - timedelta(hours=2),
            "version": 8
        },
        {
            "id": 4,
            "uid": "database-monitoring",
            "title": "Database Monitoring",
            "tags": json.dumps(["database", "postgres", "production"]),
            "starred": False,
            "folder_id": 2,
            "folder_uid": "monitoring",
            "folder_title": "Monitoring",
            "json_model": json.dumps({
                "uid": "database-monitoring",
                "title": "Database Monitoring",
                "tags": ["database", "postgres", "production"],
                "timezone": "browser",
                "schemaVersion": 38,
                "version": 1,
                "panels": [
                    {
                        "id": 1,
                        "type": "graph",
                        "title": "Query Performance",
                        "targets": [
                            {
                                "query": "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"x": 0, "y": 0, "w": 24, "h": 8}
                    }
                ]
            }),
            "created_at": datetime.now() - timedelta(days=10),
            "updated_at": datetime.now(),
            "version": 3
        }
    ]

    for dashboard in dashboards:
        conn.execute(
            """
            INSERT INTO dashboards
            (id, uid, title, tags, starred, folder_id, folder_uid, folder_title,
             json_model, created_at, updated_at, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                dashboard["id"],
                dashboard["uid"],
                dashboard["title"],
                dashboard["tags"],
                dashboard["starred"],
                dashboard["folder_id"],
                dashboard["folder_uid"],
                dashboard["folder_title"],
                dashboard["json_model"],
                dashboard["created_at"],
                dashboard["updated_at"],
                dashboard["version"]
            ]
        )

    # Load annotations
    now = int(datetime.now().timestamp() * 1000)
    one_day = 24 * 60 * 60 * 1000
    annotations = [
        (
            1,
            1,  # dashboard_id
            1,  # panel_id
            now - (7 * one_day),
            now - (7 * one_day) + (2 * 60 * 60 * 1000),  # 2 hours later
            "Deployment v2.1.0",
            json.dumps(["deployment", "release"])
        ),
        (
            2,
            1,
            None,
            now - (5 * one_day),
            None,
            "High CPU usage incident",
            json.dumps(["incident", "performance"])
        ),
        (
            3,
            2,
            1,
            now - (3 * one_day),
            now - (3 * one_day) + (30 * 60 * 1000),  # 30 minutes later
            "Database maintenance window",
            json.dumps(["maintenance", "database"])
        ),
        (
            4,
            3,
            None,
            now - (1 * one_day),
            None,
            "Black Friday sales event",
            json.dumps(["business", "event"])
        )
    ]

    for annotation in annotations:
        conn.execute(
            """
            INSERT INTO annotations (id, dashboard_id, panel_id, time, time_end, text, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            annotation
        )

    print("✓ Fixtures loaded successfully")
    print(f"  - {len(folders)} folders")
    print(f"  - {len(datasources)} datasources")
    print(f"  - {len(dashboards)} dashboards")
    print(f"  - {len(annotations)} annotations")
