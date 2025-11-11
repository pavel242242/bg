"""Sample fixtures for mock PostHog API."""

import json
from datetime import datetime, timedelta
from db import get_connection

def load_fixtures():
    conn = get_connection()

    # Projects
    conn.execute("INSERT INTO projects VALUES (?, ?, ?, ?)",
                 [12345, "proj-123", "Production", "org-123"])

    # Event definitions
    events = [
        (1, 12345, "$pageview", 150000, 500),
        (2, 12345, "$click", 80000, 200),
        (3, 12345, "signup_completed", 5000, 150),
        (4, 12345, "purchase_completed", 2000, 100)
    ]
    for e in events:
        conn.execute("INSERT INTO event_definitions VALUES (?, ?, ?, ?, ?)", e)

    # Sample events
    now = datetime.now()
    for i in range(100):
        conn.execute(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)",
            [
                i + 1,
                12345,
                "$pageview" if i % 3 == 0 else "$click",
                now - timedelta(hours=i),
                f"user-{i % 10}",
                json.dumps({"$current_url": f"/page-{i}", "$browser": "Chrome"})
            ]
        )

    # Feature flags
    flags = [
        (1, 12345, "new-dashboard", "New Dashboard", True, json.dumps({"groups": [{"properties": []}]})),
        (2, 12345, "beta-features", "Beta Features", False, json.dumps({}))
    ]
    for f in flags:
        conn.execute("INSERT INTO feature_flags VALUES (?, ?, ?, ?, ?, ?)", f)

    # Insights
    conn.execute(
        "INSERT INTO insights VALUES (?, ?, ?, ?, ?, ?)",
        [1, 12345, "Pageview Trend", json.dumps({"insight": "TRENDS"}), now, json.dumps({"result": []})]
    )

    print("✓ PostHog fixtures loaded")
