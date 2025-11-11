"""
IF.talent Dashboard - Web UI for Talent Pipeline

Simple Flask dashboard for monitoring capability discovery and onboarding.

Features:
- Capabilities in queue (scouted, not yet sandboxed)
- Sandbox results (bloom patterns, costs, accuracy)
- Pending certifications (waiting for IF.guard approval)
- Deployed capabilities (currently in IF.swarm router)

Tech Stack:
- Flask backend
- SQLite database
- HTML + HTMX frontend (simple, no React needed)

Author: IF.talent Team (Agent 6)
Date: 2025-11-11
Citation: if://component/talent/dashboard-v1
"""

from flask import Flask, render_template_string, jsonify
import sqlite3
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# Database setup
DB_PATH = Path("data/talent/dashboard.db")


def init_db():
    """Initialize SQLite database for dashboard"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Capabilities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS capabilities (
            capability_id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            provider TEXT,
            description TEXT,
            discovered_at TEXT,
            status TEXT,
            bloom_score INTEGER,
            avg_accuracy REAL,
            cost_per_1k REAL,
            approved BOOLEAN
        )
    """)

    # Sandbox results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sandbox_results (
            result_id TEXT PRIMARY KEY,
            capability_id TEXT,
            tasks_run INTEGER,
            success_rate REAL,
            avg_latency_ms REAL,
            total_cost_usd REAL,
            tested_at TEXT,
            FOREIGN KEY (capability_id) REFERENCES capabilities(capability_id)
        )
    """)

    conn.commit()
    conn.close()


# HTML Template (inline for simplicity)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>IF.talent Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
        }
        .section {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f8f8f8;
            font-weight: 600;
        }
        .status-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-scouted { background: #E3F2FD; color: #1976D2; }
        .status-sandboxed { background: #FFF3E0; color: #F57C00; }
        .status-certified { background: #E8F5E9; color: #388E3C; }
        .status-deployed { background: #C8E6C9; color: #2E7D32; }
        .bloom-high { color: #4CAF50; }
        .bloom-medium { color: #FF9800; }
        .bloom-low { color: #9E9E9E; }
    </style>
</head>
<body>
    <h1>🎯 IF.talent Dashboard</h1>

    <div class="stats" hx-get="/api/stats" hx-trigger="load, every 10s" hx-swap="innerHTML">
        Loading stats...
    </div>

    <div class="section">
        <h2>📋 Capability Queue</h2>
        <table hx-get="/api/capabilities" hx-trigger="load, every 10s" hx-swap="innerHTML">
            <tbody>Loading capabilities...</tbody>
        </table>
    </div>

    <div class="section">
        <h2>🧪 Recent Sandbox Results</h2>
        <table hx-get="/api/sandbox" hx-trigger="load, every 10s" hx-swap="innerHTML">
            <tbody>Loading sandbox results...</tbody>
        </table>
    </div>
</body>
</html>
"""


@app.route("/")
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/stats")
def api_stats():
    """Get dashboard stats"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Count by status
    cursor.execute("SELECT status, COUNT(*) FROM capabilities GROUP BY status")
    status_counts = dict(cursor.fetchall())

    # Average bloom score
    cursor.execute("SELECT AVG(bloom_score) FROM capabilities WHERE bloom_score IS NOT NULL")
    avg_bloom = cursor.fetchone()[0] or 0

    # Total cost (from sandbox results)
    cursor.execute("SELECT SUM(total_cost_usd) FROM sandbox_results")
    total_cost = cursor.fetchone()[0] or 0

    conn.close()

    return f"""
        <div class="stat-card">
            <h3>Scouted</h3>
            <div class="value">{status_counts.get('scouted', 0)}</div>
        </div>
        <div class="stat-card">
            <h3>Sandboxed</h3>
            <div class="value">{status_counts.get('sandboxed', 0)}</div>
        </div>
        <div class="stat-card">
            <h3>Deployed</h3>
            <div class="value">{status_counts.get('deployed', 0)}</div>
        </div>
        <div class="stat-card">
            <h3>Avg Bloom Score</h3>
            <div class="value">{int(avg_bloom)}</div>
        </div>
        <div class="stat-card">
            <h3>Total Cost</h3>
            <div class="value">${total_cost:.2f}</div>
        </div>
    """


@app.route("/api/capabilities")
def api_capabilities():
    """Get capabilities list"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT capability_id, name, provider, type, status, bloom_score, avg_accuracy, approved
        FROM capabilities
        ORDER BY discovered_at DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "<tr><td colspan='7'>No capabilities yet. Run IF.talent scout to discover!</td></tr>"

    html = "<tr><th>Name</th><th>Provider</th><th>Type</th><th>Status</th><th>Bloom</th><th>Accuracy</th><th>Approved</th></tr>"

    for row in rows:
        cap_id, name, provider, typ, status, bloom, accuracy, approved = row

        bloom_class = "bloom-high" if bloom and bloom > 70 else "bloom-medium" if bloom and bloom > 40 else "bloom-low"
        bloom_display = f"{bloom}" if bloom else "N/A"

        accuracy_display = f"{accuracy:.1f}%" if accuracy else "N/A"
        approved_display = "✅" if approved else "⏳"

        html += f"""
            <tr>
                <td><strong>{name}</strong></td>
                <td>{provider}</td>
                <td>{typ}</td>
                <td><span class="status-badge status-{status}">{status}</span></td>
                <td class="{bloom_class}">{bloom_display}</td>
                <td>{accuracy_display}</td>
                <td>{approved_display}</td>
            </tr>
        """

    return html


@app.route("/api/sandbox")
def api_sandbox():
    """Get recent sandbox results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.capability_id, c.name, s.tasks_run, s.success_rate, s.avg_latency_ms, s.total_cost_usd, s.tested_at
        FROM sandbox_results s
        JOIN capabilities c ON s.capability_id = c.capability_id
        ORDER BY s.tested_at DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "<tr><td colspan='6'>No sandbox results yet.</td></tr>"

    html = "<tr><th>Capability</th><th>Tasks</th><th>Success Rate</th><th>Latency</th><th>Cost</th><th>Tested</th></tr>"

    for row in rows:
        cap_id, name, tasks, success_rate, latency, cost, tested_at = row

        html += f"""
            <tr>
                <td><strong>{name}</strong></td>
                <td>{tasks}</td>
                <td>{success_rate:.1f}%</td>
                <td>{latency:.0f}ms</td>
                <td>${cost:.2f}</td>
                <td>{tested_at[:10]}</td>
            </tr>
        """

    return html


# Utility functions for populating database
def add_capability(conn, capability_data):
    """Add capability to database"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO capabilities
        (capability_id, name, type, provider, description, discovered_at, status, bloom_score, avg_accuracy, cost_per_1k, approved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, capability_data)
    conn.commit()


def add_sandbox_result(conn, result_data):
    """Add sandbox result to database"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sandbox_results
        (result_id, capability_id, tasks_run, success_rate, avg_latency_ms, total_cost_usd, tested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, result_data)
    conn.commit()


if __name__ == "__main__":
    # Initialize database
    init_db()

    # Populate with sample data for testing
    conn = sqlite3.connect(DB_PATH)

    # Sample capabilities
    add_capability(conn, (
        "gemini-2.0-flash",
        "Gemini 2.0 Flash",
        "model",
        "google",
        "Fast and efficient multimodal model",
        "2025-11-11T00:15:00Z",
        "deployed",
        65,
        76.4,
        0.1875,
        True
    ))

    add_capability(conn, (
        "claude-sonnet-4.5",
        "Claude Sonnet 4.5",
        "model",
        "anthropic",
        "Balanced intelligence and speed",
        "2025-11-10T12:00:00Z",
        "certified",
        82,
        88.5,
        9.0,
        True
    ))

    add_capability(conn, (
        "langchain-v0.1.0",
        "LangChain v0.1.0",
        "framework",
        "github",
        "Build applications with LLMs",
        "2025-11-09T08:30:00Z",
        "scouted",
        None,
        None,
        None,
        False
    ))

    # Sample sandbox results
    add_sandbox_result(conn, (
        "result-gemini-flash",
        "gemini-2.0-flash",
        20,
        90.0,
        1850.0,
        18.75,
        "2025-11-11T02:00:00Z"
    ))

    add_sandbox_result(conn, (
        "result-claude-sonnet",
        "claude-sonnet-4.5",
        20,
        95.0,
        2200.0,
        45.00,
        "2025-11-10T14:00:00Z"
    ))

    conn.close()

    print("🎯 IF.talent Dashboard running on http://localhost:5000")
    print("   Database initialized with sample data")

    app.run(debug=True, host="0.0.0.0", port=5000)
